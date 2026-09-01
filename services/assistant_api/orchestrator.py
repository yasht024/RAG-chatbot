import logging
from typing import List

from infra.environments.config import config
from packages.contracts.schemas import QueryRequest, FactualResponse, TerminalState, Citation
from packages.contracts.evidence import EvidenceItem
from packages.retrieval.search import InMemoryKeywordSearch, InMemoryVectorSearch
from packages.retrieval.fusion import reciprocal_rank_fusion
from packages.retrieval.router import DocumentRouter
from packages.policy.validation import validate_candidates
from packages.policy.compliance import enforce_compliance
from packages.policy.privacy_guard import PrivacyGuard
from packages.policy.injection_guard import PromptInjectionGuard
from packages.policy.classifier import QueryClassifier
from packages.policy.resolver import SchemeResolver
from packages.resilience.circuit_breaker import CircuitBreaker
from packages.cache.answer_cache import EvidenceAwareAnswerCache
from services.assistant_api.query_decomposer import QueryDecomposer
from services.assistant_api.generator import (
    handle_recommendation_refusal,
)

logger = logging.getLogger(__name__)


class Orchestrator:
    def __init__(self):
        self.keyword_search = InMemoryKeywordSearch()
        self.vector_search = InMemoryVectorSearch()
        self.privacy_guard = PrivacyGuard()
        self.injection_guard = PromptInjectionGuard()
        self.classifier = QueryClassifier()
        self.resolver = SchemeResolver()
        self.decomposer = QueryDecomposer()
        self.answer_cache = EvidenceAwareAnswerCache()

        self.corpus_version = "2.0.0"
        self.policy_version = config.policy_version
        self.vector_circuit_breaker = CircuitBreaker(
            failure_threshold=3, recovery_timeout_sec=5.0, name="vector_search_service"
        )
        self.keyword_circuit_breaker = CircuitBreaker(
            failure_threshold=3, recovery_timeout_sec=5.0, name="keyword_search_service"
        )

    def process_query(self, request: QueryRequest) -> FactualResponse:
        raw_query = request.query
        query_text = raw_query.lower()

        # 0. Safety: PII & Financial Credential Redaction Guard (P3-SEC-05)
        pii_result = self.privacy_guard.scan_query(raw_query)
        if pii_result:
            return FactualResponse(
                status=TerminalState.SENSITIVE_DATA_WARNING,
                refusal_reason=pii_result["message"],
            )

        # 0b. Safety: Prompt Injection Guard on User Query (P3-SEC-01)
        inj_result = self.injection_guard.scan_text(raw_query)
        if inj_result:
            return FactualResponse(
                status=TerminalState.POLICY_REFUSAL,
                refusal_reason="Adversarial prompt injection pattern detected and rejected.",
            )

        # 1. Classification & AMC Path Router
        classification = self.classifier.classify_query(raw_query)
        query_class = classification.get("query_class")

        # Advisory / Recommendation refusal
        if query_class == "ADVISORY":
            return handle_recommendation_refusal()

        # Phase 7: Performance Comparison refusal vs Single Fact allowance
        if query_class == "PERFORMANCE_COMPARISON":
            return FactualResponse(
                status=TerminalState.POLICY_REFUSAL,
                refusal_reason="I can provide verified facts about HDFC mutual fund schemes, but I cannot compare or rank fund performance.",
            )

        # 2. Scheme Resolution (Phase 3)
        resolve_res = self.resolver.resolve_scheme(query_text)

        scheme_id = resolve_res.get("scheme_id")
        plan = resolve_res.get("plan", "Direct")
        option = resolve_res.get("option", "Growth")
        amc_level = False

        if not scheme_id and getattr(request, "history", None):
            for msg in reversed(request.history):
                if msg.role == "user":
                    hist_res = self.resolver.resolve_scheme(msg.content)
                    if hist_res.get("scheme_id"):
                        scheme_id = hist_res.get("scheme_id")
                        plan = hist_res.get("plan", plan)
                        option = hist_res.get("option", option)
                        break
                    elif "elss" in msg.content.lower():
                        scheme_id = "hdfc_elss_tax_saver"
                        break

        # Check for AMC-level procedural queries before enforcing scheme
        amc_procedures = [
            "kyc_procedure",
            "factsheet_location",
            "account_statement_procedure",
            "capital_gains_procedure",
        ]
        requested_facts = self.decomposer.decompose(query_text)

        requested_fact_count = len(requested_facts)
        logger.info(f"requested_fact_count = {requested_fact_count}")

        if any(f in amc_procedures for f in requested_facts):
            amc_level = True

        # If the query mentions ELSS, implicitly set the scheme to the tax saver fund
        if not scheme_id and "elss" in query_text:
            scheme_id = "hdfc_elss_tax_saver"

        # Ambiguity / Unsupported check
        if not amc_level:
            if resolve_res.get("status") == "UNSUPPORTED_PLAN":
                return FactualResponse(
                    status=TerminalState.POLICY_REFUSAL,
                    refusal_reason=f"Information for the {resolve_res.get('plan')} plan is not supported by this assistant.",
                )
            if not scheme_id:
                if resolve_res.get("status") == "AMBIGUOUS_SCHEME":
                    return FactualResponse(
                        status=TerminalState.AMBIGUOUS_SCHEME,
                        refusal_reason=resolve_res.get("message", "Multiple matching schemes found. Please clarify."),
                    )
                else:
                    # Could not identify scheme and not an AMC query
                    return FactualResponse(
                        status=TerminalState.AMBIGUOUS_SCHEME,
                        refusal_reason="Could not definitively identify a single scheme from the query.",
                    )

        # If no facts requested but it's an ELSS query without explicit fact, default to lock-in
        if not requested_facts:
            if "elss" in query_text:
                requested_facts = ["elss_lock_in"]
            else:
                return FactualResponse(
                    status=TerminalState.INSUFFICIENT_EVIDENCE,
                    refusal_reason="Question not supported. You can ask about: SIP amounts, expense ratios, benchmarks, lock-in periods (ELSS), KYC procedures, exit loads, fund managers, investment objectives, riskometers, inception dates, lump sum minimums, plans/options, factsheets, account statements, capital gains, and fund performance.",
                )

        # 3. Cache Check
        # Sort requested facts for deterministic cache key
        fact_key = ",".join(sorted(requested_facts))
        cache_key = f"{scheme_id or 'NONE'}|{plan}|{option}|{fact_key}"
        cached_response = self.answer_cache.get(cache_key, self.corpus_version, self.policy_version)
        if cached_response:
            logger.info(f"Returning cached answer for key '{cache_key}'")
            return cached_response

        # 4. Retrieval & Validation (Phase 4 & 5)
        evidence_items: List[EvidenceItem] = []
        overall_citation = None
        overall_citation_url = None
        overall_source_date = None
        evidence_passage_ids = []

        for fact_type in requested_facts:
            allowed_docs = DocumentRouter.get_document_types_for_fact(fact_type)

            # Keyword Search
            try:
                kw_results = self.keyword_circuit_breaker.call(
                    lambda: self.keyword_search.search(
                        query_text,
                        scheme_id=scheme_id,
                        plan=plan,
                        option=option,
                        document_types=allowed_docs,
                        fact_type=fact_type,
                        amc_level=amc_level,
                    ),
                    fallback=lambda: None,
                )
            except Exception as e:
                logger.error(f"Keyword search failed for {fact_type}: {e}")
                kw_results = None

            # Vector Search
            try:
                vec_results = self.vector_circuit_breaker.call(
                    lambda: self.vector_search.search(
                        query_text,
                        scheme_id=scheme_id,
                        plan=plan,
                        option=option,
                        document_types=allowed_docs,
                        fact_type=fact_type,
                        amc_level=amc_level,
                    ),
                    fallback=lambda: None,
                )
            except Exception as e:
                logger.warning(f"Vector search degraded/failed for {fact_type}: {e}")
                vec_results = None

            fused_candidates = []
            if kw_results and vec_results:
                fused_candidates = reciprocal_rank_fusion(kw_results, vec_results)
            elif kw_results:
                fused_candidates = kw_results
            elif vec_results:
                fused_candidates = vec_results

            if not fused_candidates:
                continue

            expected_scheme = None if (amc_level and fact_type in amc_procedures) else scheme_id
            decision = validate_candidates(fused_candidates, expected_scheme=expected_scheme)

            if decision.status == "VALID":
                selected_passage_id = decision.selected_passage_ids[0]
                selected_passage = next(
                    (p for p in fused_candidates if p["passage_id"] == selected_passage_id),
                    fused_candidates[0],
                )

                evidence = EvidenceItem(
                    scheme_id=scheme_id or "AMC",
                    scheme_name=selected_passage.get("scheme_name"),
                    plan=plan,
                    option=option,
                    fact_type=fact_type,
                    value=selected_passage["normalized_text"],
                    source_org=selected_passage.get("source_org", "HDFC AMC"),
                    source_type=selected_passage.get("source_type", "scheme_page"),
                    source_url=decision.citation_url,
                    document_name=selected_passage.get("document_name", "Unknown Document"),
                    publication_date=decision.source_date,
                    effective_date=selected_passage.get("effective_date"),
                    page=selected_passage.get("page_number"),
                    approved=True,
                    confidence="verified",
                )
                evidence_items.append(evidence)

                # Capture URL/Date from the first valid evidence for the overall response
                if not overall_citation:
                    overall_citation = Citation(
                        organization=evidence.source_org,
                        url=decision.citation_url,
                        document_name=evidence.document_name,
                        document_type=evidence.source_type,
                        publication_date=evidence.publication_date,
                        effective_date=evidence.effective_date,
                        page_number=str(evidence.page) if evidence.page else None,
                    )
                    overall_citation_url = decision.citation_url
                    overall_source_date = decision.source_date

                evidence_passage_ids.extend(decision.selected_passage_ids)

        # 5. Completeness Check & Response Formatting (Phase 6)
        validated_fact_count = len(evidence_items)
        logger.info(f"validated_fact_count = {validated_fact_count}")

        if not evidence_items:
            # Complete failure to retrieve/validate any requested facts
            resp = FactualResponse(
                status=TerminalState.INSUFFICIENT_EVIDENCE,
                refusal_reason="Insufficient official evidence is available to verify this fact.",
            )
            self.answer_cache.put(cache_key, self.corpus_version, self.policy_version, resp)
            return resp

        # Generate answers
        from services.assistant_api.generator import generate_multi_fact_answer

        answer_sentences = generate_multi_fact_answer(evidence_items, requested_facts)

        draft = FactualResponse(
            status=TerminalState.FACTUAL_ANSWER,
            answer_sentences=answer_sentences,
            citation=overall_citation,
            citation_url=overall_citation_url,
            source_date=overall_source_date,
            evidence_passage_ids=evidence_passage_ids,
        )

        # 6. Final Compliance Validation (Phase 8)
        final_response = enforce_compliance(draft)
        self.answer_cache.put(cache_key, self.corpus_version, self.policy_version, final_response)
        return final_response

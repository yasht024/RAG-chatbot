import json
import os
import logging
from packages.contracts.schemas import QueryRequest, FactualResponse, TerminalState
from packages.retrieval.search import InMemoryKeywordSearch, InMemoryVectorSearch
from packages.retrieval.fusion import reciprocal_rank_fusion
from packages.retrieval.router import DocumentRouter
from packages.policy.validation import validate_candidates
from packages.policy.compliance import enforce_compliance
from packages.policy.privacy_guard import PrivacyGuard
from packages.policy.injection_guard import PromptInjectionGuard
from packages.policy.classifier import QueryClassifier
from packages.resilience.circuit_breaker import CircuitBreaker, CircuitBreakerOpenException
from packages.resilience.retry import retry_with_backoff
from packages.cache.answer_cache import EvidenceAwareAnswerCache
from services.assistant_api.generator import generate_scalar_answer, handle_recommendation_refusal

logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self):
        self.keyword_search = InMemoryKeywordSearch()
        self.vector_search = InMemoryVectorSearch()
        self.privacy_guard = PrivacyGuard()
        self.injection_guard = PromptInjectionGuard()
        self.classifier = QueryClassifier()
        self.answer_cache = EvidenceAwareAnswerCache()
        self.corpus_version = "2.0.0"
        self.policy_version = "2026-08-23.1"
        self.vector_circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout_sec=5.0,
            name="vector_search_service"
        )
        self.keyword_circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout_sec=5.0,
            name="keyword_search_service"
        )
        
        # Load aliases for scheme resolution
        alias_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "catalog", "aliases.json")
        try:
            with open(alias_path, "r") as f:
                self.aliases = json.load(f)
        except Exception:
            self.aliases = {}

    def _resolve_scheme(self, query: str) -> str:
        q = query.lower()
        for scheme_id, alias_list in self.aliases.items():
            for alias in alias_list:
                if alias.lower() in q:
                    return scheme_id
        return None

    def process_query(self, request: QueryRequest) -> FactualResponse:
        raw_query = request.query
        query_text = raw_query.lower()
        
        # 0. Safety: PII & Financial Credential Redaction Guard (P3-SEC-05)
        pii_result = self.privacy_guard.scan_query(raw_query)
        if pii_result:
            return FactualResponse(
                status=TerminalState.SENSITIVE_DATA_WARNING,
                refusal_reason=pii_result["message"]
            )

        # 0b. Safety: Prompt Injection Guard on User Query (P3-SEC-01)
        inj_result = self.injection_guard.scan_text(raw_query)
        if inj_result:
            return FactualResponse(
                status=TerminalState.POLICY_REFUSAL,
                refusal_reason="Adversarial prompt injection pattern detected and rejected."
            )

        # 1. Classification & AMC Path Router (P3-SEC-02 mixed-intent & advice defense)
        classification = self.classifier.classify_query(raw_query)
        if classification.get("query_class") in ["ADVISORY", "PERFORMANCE_COMPARISON"]:
            return handle_recommendation_refusal()

        scheme_id = self._resolve_scheme(query_text)
        amc_level = False
        
        if not scheme_id and getattr(request, 'history', None):
            for msg in reversed(request.history):
                if msg.role == 'user':
                    hist_scheme = self._resolve_scheme(msg.content)
                    if hist_scheme:
                        scheme_id = hist_scheme
                        break
                    elif "elss" in msg.content.lower():
                        scheme_id = "hdfc_elss_tax_saver"
                        break

        # 1b. Cache Check (P3-REL-05: Conserves LLM RPM/RPD/TPM/TPD)
        cache_key = f"{query_text}|{scheme_id or 'NONE'}"
        cached_response = self.answer_cache.get(cache_key, self.corpus_version, self.policy_version)
        if cached_response:
            logger.info(f"Returning cached answer for query '{query_text}'")
            return cached_response
        
        if "sip" in query_text:
            fact_type = "minimum_sip_amount"
        elif "expense" in query_text:
            fact_type = "expense_ratio"
        elif "benchmark" in query_text:
            fact_type = "benchmark_index"
        elif "lock-in" in query_text or "elss" in query_text:
            fact_type = "elss_lock_in"
            if not scheme_id:
                scheme_id = "hdfc_elss_tax_saver"
        elif "kyc" in query_text:
            fact_type = "kyc_procedure"
            amc_level = True
        elif "exit" in query_text:
            fact_type = "exit_load"
        elif "manager" in query_text:
            fact_type = "fund_manager"
        elif "objective" in query_text:
            fact_type = "investment_objective"
        elif "risk" in query_text:
            fact_type = "riskometer"
        elif "inception" in query_text or "launch date" in query_text:
            fact_type = "inception_date"
        elif "lump" in query_text or "minimum amount" in query_text or "spend" in query_text:
            fact_type = "minimum_lumpsum"
        elif "plans" in query_text or "options" in query_text:
            fact_type = "plans_options"
        elif "factsheet" in query_text:
            fact_type = "factsheet_location"
            amc_level = True
        elif "account statement" in query_text:
            fact_type = "account_statement_procedure"
            amc_level = True
        elif "capital-gains" in query_text or "capital gains" in query_text:
            fact_type = "capital_gains_procedure"
            amc_level = True
        elif "performance" in query_text or "return" in query_text:
            fact_type = "performance_value"
        else:
            resp = FactualResponse(
                status=TerminalState.INSUFFICIENT_EVIDENCE,
                refusal_reason="Question not supported in Phase 2B slice."
            )
            self.answer_cache.put(cache_key, self.corpus_version, self.policy_version, resp)
            return resp
            
        if not amc_level and not scheme_id:
            resp = FactualResponse(
                status=TerminalState.AMBIGUOUS_SCHEME,
                refusal_reason="Could not definitively identify a single scheme from the query."
            )
            self.answer_cache.put(cache_key, self.corpus_version, self.policy_version, resp)
            return resp

        # 2. Document Type Routing
        allowed_docs = DocumentRouter.get_document_types_for_fact(fact_type)

        # 3. Retrieval with Circuit Breakers and Fallbacks
        kw_results = None
        try:
            kw_results = self.keyword_circuit_breaker.call(
                lambda: self.keyword_search.search(
                    query_text, 
                    scheme_id=scheme_id,
                    document_types=allowed_docs,
                    fact_type=fact_type,
                    amc_level=amc_level
                ),
                fallback=lambda: None
            )
        except Exception as e:
            logger.error(f"Keyword search failed: {e}")
            kw_results = None

        vec_results = None
        try:
            vec_results = self.vector_circuit_breaker.call(
                lambda: self.vector_search.search(
                    query_text, 
                    scheme_id=scheme_id,
                    document_types=allowed_docs,
                    fact_type=fact_type,
                    amc_level=amc_level
                ),
                fallback=lambda: None
            )
        except Exception as e:
            logger.warning(f"Vector search degraded/failed: {e}. Falling back to lexical results.")
            vec_results = None
        
        # 4. Fusion / Degradation to Lexical
        if kw_results is None and vec_results is None:
            # Complete retrieval failure -> fail-closed
            return FactualResponse(
                status=TerminalState.TEMPORARILY_UNAVAILABLE,
                refusal_reason="Search systems are temporarily unavailable."
            )
            
        kw_res = kw_results or []
        vec_res = vec_results or []
            
        if kw_res and vec_res:
            fused_candidates = reciprocal_rank_fusion(kw_res, vec_res)
        elif kw_res:
            logger.info("Degraded retrieval: Vector unavailable, proceeding with lexical-only candidates.")
            fused_candidates = kw_res
        elif vec_res:
            logger.info("Degraded retrieval: Lexical unavailable, proceeding with vector-only candidates.")
            fused_candidates = vec_res
        else:
            # Search succeeded but found no documents
            resp = FactualResponse(
                status=TerminalState.INSUFFICIENT_EVIDENCE,
                refusal_reason="No relevant documents found for the requested scheme and fact."
            )
            self.answer_cache.put(cache_key, self.corpus_version, self.policy_version, resp)
            return resp
        
        # 5. Evidence Validation (skip scheme match if amc_level)
        expected_scheme = None if amc_level else scheme_id
        decision = validate_candidates(fused_candidates, expected_scheme=expected_scheme)
        if decision.status != "VALID":
            resp = FactualResponse(
                status=TerminalState(decision.status),
                refusal_reason="Validation rejected the retrieved candidates."
            )
            self.answer_cache.put(cache_key, self.corpus_version, self.policy_version, resp)
            return resp
            
        # 6. Generation & Repair Loop
        selected_passage_id = decision.selected_passage_ids[0]
        selected_passage = next((p for p in fused_candidates if p["passage_id"] == selected_passage_id), fused_candidates[0])
        passage_text = selected_passage["normalized_text"]
        
        if fact_type in ["investment_objective", "kyc_procedure", "capital_gains_procedure", "account_statement_procedure"]:
            from services.assistant_api.generator import generate_descriptive_answer, llm
            answer = generate_descriptive_answer(fact_type, passage_text)
            
            is_valid, reason = llm.verify_semantic_claim(answer, passage_text)
            if not is_valid:
                answer = generate_descriptive_answer(fact_type, passage_text)
                is_valid, reason = llm.verify_semantic_claim(answer, passage_text)
                if not is_valid:
                    resp = FactualResponse(
                        status=TerminalState.INSUFFICIENT_EVIDENCE,
                        refusal_reason="Semantic claim validation failed after repair attempt."
                    )
                    self.answer_cache.put(cache_key, self.corpus_version, self.policy_version, resp)
                    return resp
        else:
            answer = generate_scalar_answer(fact_type, passage_text)
        
        draft = FactualResponse(
            status=TerminalState.FACTUAL_ANSWER,
            answer_sentences=[answer],
            citation_url=decision.citation_url,
            source_date=decision.source_date,
            evidence_passage_ids=decision.selected_passage_ids
        )
        
        # 7. Compliance Validation
        final_response = enforce_compliance(draft)
        self.answer_cache.put(cache_key, self.corpus_version, self.policy_version, final_response)
        return final_response



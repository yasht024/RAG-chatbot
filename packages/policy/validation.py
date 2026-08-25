import datetime
from typing import List, Dict, Any, Optional
from packages.contracts.schemas import EvidenceDecision
from packages.corpus.lineage import DocumentLineageManager
from packages.corpus.conflicts import ConflictRegistry
from packages.policy.injection_guard import PromptInjectionGuard

SOURCE_PRECEDENCE = {"groww.in": 100, "hdfcfund.com": 50}

# Global instances for governance
default_lineage_manager = DocumentLineageManager()
default_conflict_registry = ConflictRegistry()
default_injection_guard = PromptInjectionGuard()


def get_domain(url: str) -> str:
    """Helper to extract domain for precedence check."""
    if "groww.in" in url:
        return "groww.in"
    if "hdfcfund.com" in url:
        return "hdfcfund.com"
    return "unknown"


def validate_candidates(
    candidates: List[Dict[str, Any]],
    expected_scheme: Optional[str],
    lineage_mgr: Optional[DocumentLineageManager] = None,
    conflict_reg: Optional[ConflictRegistry] = None,
    injection_guard: Optional[PromptInjectionGuard] = None,
) -> EvidenceDecision:
    """
    Validates retrieved candidates against the expected scheme.
    Filters superseded documents, strips prompt-injected passages,
    checks conflict quarantine, and applies Groww > HDFC precedence logic.
    Fails closed if conflict cannot be resolved.
    """
    lineage = lineage_mgr or default_lineage_manager
    conflicts = conflict_reg or default_conflict_registry
    inj_guard = injection_guard or default_injection_guard

    if not candidates:
        return EvidenceDecision(
            status="INSUFFICIENT_EVIDENCE",
            selected_document_id="",
            selected_passage_ids=[],
            citation_url="",
            source_date="",
            fact_type="",
            conflict_detected=False,
            validation_ruleset="v1.1",
        )

    # Filter out superseded candidates
    candidates = lineage.filter_superseded_candidates(candidates)

    # Filter out poisoned / injected candidate passages
    candidates = [c for c in candidates if inj_guard.is_safe(c.get("normalized_text", ""))]

    if expected_scheme:
        valid_candidates = [c for c in candidates if expected_scheme in c.get("scheme_ids", [])]
    else:
        # AMC-level query: no scheme enforcement needed
        valid_candidates = candidates

    if not valid_candidates:
        return EvidenceDecision(
            status="INSUFFICIENT_EVIDENCE",
            selected_document_id="",
            selected_passage_ids=[],
            citation_url="",
            source_date="",
            fact_type="",
            conflict_detected=False,
            validation_ruleset="v1.1",
        )

    fact_type = valid_candidates[0].get("fact_types", ["unknown"])[0]

    # Check if fact is currently quarantined by operator in ConflictRegistry
    if expected_scheme and conflicts.is_quarantined(expected_scheme, fact_type):
        return EvidenceDecision(
            status="SOURCE_CONFLICT",
            selected_document_id="",
            selected_passage_ids=[],
            citation_url="",
            source_date="",
            fact_type=fact_type,
            conflict_detected=True,
            validation_ruleset="v1.1",
        )

    # Conflict Detection & Resolution
    unique_values = {}

    for cand in valid_candidates:
        val = cand.get("normalized_text", "").strip()
        url = cand.get("source_url", "https://www.hdfcfund.com/")

        if val not in unique_values:
            unique_values[val] = cand
        else:
            # If same value from different sources, keep the higher precedence one
            existing_cand = unique_values[val]
            existing_domain = get_domain(existing_cand.get("source_url", "https://www.hdfcfund.com/"))
            new_domain = get_domain(url)

            if SOURCE_PRECEDENCE.get(new_domain, 0) > SOURCE_PRECEDENCE.get(existing_domain, 0):
                unique_values[val] = cand

    if len(unique_values) > 1:
        # Conflicting values detected
        best_val = None
        best_score = -1
        conflict_unresolved = False

        for val, cand in unique_values.items():
            domain = get_domain(cand.get("source_url", "https://www.hdfcfund.com/"))
            score = SOURCE_PRECEDENCE.get(domain, 0)

            if score > best_score:
                best_score = score
                best_val = val
                conflict_unresolved = False
            elif score == best_score:
                # Two different values have the SAME precedence score!
                conflict_unresolved = True

        if conflict_unresolved:
            # Record in conflict registry for operator triage and fail closed
            if expected_scheme:
                conflicts.record_conflict(expected_scheme, fact_type, list(unique_values.values()))

            return EvidenceDecision(
                status="SOURCE_CONFLICT",
                selected_document_id="",
                selected_passage_ids=[],
                citation_url="",
                source_date="",
                fact_type=fact_type,
                conflict_detected=True,
                validation_ruleset="v1.1",
            )
        else:
            # Resolved successfully by precedence
            selected = unique_values[best_val]
            conflict_detected = True
    else:
        # All valid candidates agree
        selected = list(unique_values.values())[0]
        conflict_detected = False

    return EvidenceDecision(
        status="VALID",
        selected_document_id=selected.get("document_id", "doc_unknown"),
        selected_passage_ids=[selected.get("passage_id", "passage_unknown")],
        citation_url=selected.get("source_url", "https://www.hdfcfund.com/"),
        source_date=selected.get("publication_date", datetime.date.today().strftime("%Y-%m-%d")),
        fact_type=selected.get("fact_types", ["unknown"])[0],
        conflict_detected=conflict_detected,
        validation_ruleset="v1.1",
    )

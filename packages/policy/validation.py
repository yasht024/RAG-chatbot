"""
validation.py
-------------
Evidence validation and source-precedence resolution for the HDFC FAQ Agent.

Source priority (higher = preferred):
  100  hdfcfund.com    (HDFC AMC official)
   90  amfiindia.com   (AMFI)
   80  sebi.gov.in     (SEBI)
   -1  groww.in        (PROHIBITED — hard-rejected before any scoring)
   -1  any other prohibited domain

Hard pre-filter: any candidate whose source_url or source_org contains a
prohibited domain is removed BEFORE conflict resolution. This means the LLM
never receives prohibited factual evidence, regardless of what downstream
logic does.
"""
import datetime
from typing import List, Dict, Any, Optional
from packages.contracts.schemas import EvidenceDecision
from packages.corpus.lineage import DocumentLineageManager
from packages.corpus.conflicts import ConflictRegistry
from packages.policy.injection_guard import PromptInjectionGuard

# ---------------------------------------------------------------------------
# Source precedence — HDFC AMC > AMFI > SEBI > everything else
# Groww and other prohibited aggregators receive -1 (hard-rejected)
# ---------------------------------------------------------------------------
SOURCE_PRECEDENCE: Dict[str, int] = {
    "hdfcfund.com":           100,
    "amfiindia.com":           90,
    "sebi.gov.in":             80,
    # Prohibited domains — negative score triggers hard rejection
    "groww.in":                -1,
    "moneycontrol.com":        -1,
    "etmoney.com":             -1,
    "valueresearchonline.com": -1,
    "morningstar.in":          -1,
    "zerodha.com":             -1,
    "kuvera.in":               -1,
    "scripbox.com":            -1,
}

# Prohibited domains as a set for O(1) lookup
PROHIBITED_DOMAINS = {
    "groww.in", "moneycontrol.com", "etmoney.com",
    "valueresearchonline.com", "morningstar.in",
    "zerodha.com", "kuvera.in", "scripbox.com",
}

# Global instances for governance
default_lineage_manager = DocumentLineageManager()
default_conflict_registry = ConflictRegistry()
default_injection_guard = PromptInjectionGuard()


def get_domain(url: str) -> str:
    """
    Extract the registered domain from a URL for precedence lookup.
    Returns the key that maps to SOURCE_PRECEDENCE, or 'unknown'.
    """
    if not url:
        return "unknown"
    lower = url.lower()
    for domain in SOURCE_PRECEDENCE:
        if domain in lower:
            return domain
    return "unknown"


def is_prohibited_source(candidate: Dict[str, Any]) -> bool:
    """
    Hard check: returns True if a candidate comes from a prohibited source.
    Checks both source_url (URL-based) and source_org (org-based) fields.
    """
    url = candidate.get("source_url", "") or ""
    org = (candidate.get("source_org", "") or "").lower()

    # URL-based check
    for domain in PROHIBITED_DOMAINS:
        if domain in url.lower():
            return True

    # Org-based check (belt-and-suspenders)
    prohibited_orgs = {"groww", "moneycontrol", "etmoney", "valueresearch",
                       "morningstar", "zerodha", "kuvera", "scripbox"}
    for prohibited_org in prohibited_orgs:
        if prohibited_org in org:
            return True

    return False


def validate_candidates(
    candidates: List[Dict[str, Any]],
    expected_scheme: Optional[str],
    lineage_mgr: Optional[DocumentLineageManager] = None,
    conflict_reg: Optional[ConflictRegistry] = None,
    injection_guard: Optional[PromptInjectionGuard] = None,
) -> EvidenceDecision:
    """
    Validates retrieved candidates against the expected scheme.

    Pipeline:
      1. Hard-reject prohibited sources (Groww, etc.) BEFORE any other logic.
      2. Filter superseded documents.
      3. Strip prompt-injected passages.
      4. Filter by expected scheme.
      5. Check conflict quarantine.
      6. Resolve conflicts using SOURCE_PRECEDENCE.
      7. Return best validated candidate.

    Fails closed (INSUFFICIENT_EVIDENCE) whenever no approved evidence remains.
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
            validation_ruleset="v2.0",
        )

    # --- STEP 1: Hard-reject prohibited sources ---
    # This is a hard filter — prohibited evidence never reaches the LLM.
    approved_candidates = [c for c in candidates if not is_prohibited_source(c)]

    if not approved_candidates:
        return EvidenceDecision(
            status="INSUFFICIENT_EVIDENCE",
            selected_document_id="",
            selected_passage_ids=[],
            citation_url="",
            source_date="",
            fact_type="",
            conflict_detected=False,
            validation_ruleset="v2.0",
        )

    # --- STEP 2: Filter superseded documents ---
    approved_candidates = lineage.filter_superseded_candidates(approved_candidates)

    # --- STEP 3: Filter prompt-injected passages ---
    approved_candidates = [
        c for c in approved_candidates
        if inj_guard.is_safe(c.get("normalized_text", ""))
    ]

    if not approved_candidates:
        return EvidenceDecision(
            status="INSUFFICIENT_EVIDENCE",
            selected_document_id="",
            selected_passage_ids=[],
            citation_url="",
            source_date="",
            fact_type="",
            conflict_detected=False,
            validation_ruleset="v2.0",
        )

    # --- STEP 4: Scheme filter ---
    if expected_scheme:
        valid_candidates = [
            c for c in approved_candidates
            if expected_scheme in c.get("scheme_ids", [])
        ]
    else:
        # AMC-level query: no scheme enforcement needed
        valid_candidates = approved_candidates

    if not valid_candidates:
        return EvidenceDecision(
            status="INSUFFICIENT_EVIDENCE",
            selected_document_id="",
            selected_passage_ids=[],
            citation_url="",
            source_date="",
            fact_type="",
            conflict_detected=False,
            validation_ruleset="v2.0",
        )

    fact_type = valid_candidates[0].get("fact_types", ["unknown"])[0]

    # --- STEP 5: Conflict quarantine check ---
    if expected_scheme and conflicts.is_quarantined(expected_scheme, fact_type):
        return EvidenceDecision(
            status="SOURCE_CONFLICT",
            selected_document_id="",
            selected_passage_ids=[],
            citation_url="",
            source_date="",
            fact_type=fact_type,
            conflict_detected=True,
            validation_ruleset="v2.0",
        )

    # --- STEP 6: Conflict Detection & Resolution by SOURCE_PRECEDENCE ---
    unique_values: Dict[str, Dict[str, Any]] = {}

    for cand in valid_candidates:
        val = cand.get("normalized_text", "").strip()
        url = cand.get("source_url", "")
        domain = get_domain(url)
        score = SOURCE_PRECEDENCE.get(domain, 0)

        if val not in unique_values:
            unique_values[val] = cand
        else:
            existing_domain = get_domain(
                unique_values[val].get("source_url", "")
            )
            existing_score = SOURCE_PRECEDENCE.get(existing_domain, 0)
            # Keep the higher-precedence (more authoritative) source
            if score > existing_score:
                unique_values[val] = cand

    if len(unique_values) > 1:
        # Conflicting values: resolve by precedence
        best_val = None
        best_score = -999
        conflict_unresolved = False

        for val, cand in unique_values.items():
            domain = get_domain(cand.get("source_url", ""))
            score = SOURCE_PRECEDENCE.get(domain, 0)
            
            cand_date_str = cand.get("effective_date") or cand.get("publication_date") or ""
            try:
                import dateutil.parser
                cand_date = dateutil.parser.parse(cand_date_str) if cand_date_str else datetime.datetime.min
            except:
                cand_date = datetime.datetime.min

            if score > best_score:
                best_score = score
                best_val = val
                conflict_unresolved = False
                best_date = cand_date
            elif score == best_score:
                if cand_date > best_date:
                    best_score = score
                    best_val = val
                    conflict_unresolved = False
                    best_date = cand_date
                elif cand_date < best_date:
                    # The existing best_val is newer, so we keep it.
                    pass
                else:
                    conflict_unresolved = True

        if conflict_unresolved:
            if expected_scheme:
                conflicts.record_conflict(
                    expected_scheme, fact_type, list(unique_values.values())
                )
            return EvidenceDecision(
                status="SOURCE_CONFLICT",
                selected_document_id="",
                selected_passage_ids=[],
                citation_url="",
                source_date="",
                fact_type=fact_type,
                conflict_detected=True,
                validation_ruleset="v2.0",
            )

        selected = unique_values[best_val]
        conflict_detected = True
    else:
        selected = list(unique_values.values())[0]
        conflict_detected = False

    return EvidenceDecision(
        status="VALID",
        selected_document_id=selected.get("document_id", "doc_unknown"),
        selected_passage_ids=[selected.get("passage_id", "passage_unknown")],
        citation_url=selected.get("source_url", "https://www.hdfcfund.com/"),
        source_date=selected.get("effective_date") or selected.get("publication_date") or "",
        fact_type=selected.get("fact_types", ["unknown"])[0],
        conflict_detected=conflict_detected,
        validation_ruleset="v2.0",
    )

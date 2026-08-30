import os
import datetime
from typing import List, Dict, Any, Optional

TODAY_STR = datetime.date.today().strftime("%Y-%m-%d")
from packages.retrieval.interfaces import RetrievalClient
from packages.retrieval.corpus_loader import load_corpus_from_processed

# ---------------------------------------------------------------------------
# AMC-level procedural passages (not in processed JSON files)
# These cover investor-service questions that are not scheme-specific.
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Publication dates for AMC procedural passages.
# Use real reference dates — never TODAY_STR (that would fabricate the date).
# Update these when the underlying HDFC AMC pages are revised.
# ---------------------------------------------------------------------------
_AMC_PROC_REFERENCE_DATE = "2025-01-01"  # Conservative known-good date for procedures

AMC_PROCEDURE_PASSAGES = [
    {
        "passage_id": "passage_amc_kyc",
        "document_id": "doc_hdfc_amc_proc",
        "document_type": "AMC_PROCEDURE",
        "scheme_ids": [],
        "plan": "ALL",
        "option": "ALL",
        "normalized_text": "To update your KYC, visit the HDFC AMC investor portal at hdfcfund.com and follow the KYC update process.",
        "fact_types": ["kyc_procedure"],
        "is_table": False,
        # source_org / approved_source: required by Phase 1 — source must be HDFC AMC
        "source_org": "HDFC AMC",
        "source_domain": "hdfcfund.com",
        "approved_source": True,
        "publication_date": _AMC_PROC_REFERENCE_DATE,
        "source_url": "https://www.hdfcfund.com/investor-desk/kyc",
    },
    {
        "passage_id": "passage_amc_factsheet_loc",
        "document_id": "doc_amc_factsheet_loc",
        "document_type": "AMC_PROCEDURE",
        "scheme_ids": [],
        "plan": "ALL",
        "option": "ALL",
        "normalized_text": "You can download the official HDFC Mutual Fund factsheet from the 'Downloads' section on the HDFC AMC website at hdfcfund.com.",
        "fact_types": ["factsheet_location"],
        "is_table": False,
        "source_org": "HDFC AMC",
        "source_domain": "hdfcfund.com",
        "approved_source": True,
        "publication_date": _AMC_PROC_REFERENCE_DATE,
        "source_url": "https://www.hdfcfund.com/investor-desk/downloads/factsheets",
    },
    {
        "passage_id": "passage_amc_account_stmt",
        "document_id": "doc_amc_account_stmt",
        "document_type": "AMC_PROCEDURE",
        "scheme_ids": [],
        "plan": "ALL",
        "option": "ALL",
        "normalized_text": "To download your HDFC Mutual Fund account statement, log in to the HDFC AMC investor portal or request it via SMS/email.",
        "fact_types": ["account_statement_procedure"],
        "is_table": False,
        "source_org": "HDFC AMC",
        "source_domain": "hdfcfund.com",
        "approved_source": True,
        "publication_date": _AMC_PROC_REFERENCE_DATE,
        "source_url": "https://www.hdfcfund.com/investor-desk/account-statement",
    },
    {
        "passage_id": "passage_amc_capital_gains",
        "document_id": "doc_amc_capital_gains",
        "document_type": "AMC_PROCEDURE",
        "scheme_ids": [],
        "plan": "ALL",
        "option": "ALL",
        "normalized_text": "Capital-gains statements for HDFC Mutual Fund investments can be obtained by contacting the HDFC AMC support desk from your registered email ID.",
        "fact_types": ["capital_gains_procedure"],
        "is_table": False,
        "source_org": "HDFC AMC",
        "source_domain": "hdfcfund.com",
        "approved_source": True,
        "publication_date": _AMC_PROC_REFERENCE_DATE,
        "source_url": "https://www.hdfcfund.com/investor-desk/capital-gains",
    },
]

# ---------------------------------------------------------------------------
# Build the live corpus: processed JSON data + AMC procedural passages
# ---------------------------------------------------------------------------
_PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed")
_PROCESSED_DIR = os.path.normpath(_PROCESSED_DIR)

CORPUS: List[Dict[str, Any]] = load_corpus_from_processed(_PROCESSED_DIR) + AMC_PROCEDURE_PASSAGES


# ---------------------------------------------------------------------------
# Keyword → fact_type matching rules
# Each entry: (list_of_query_keywords_any_must_match, fact_type_key, score)
# ---------------------------------------------------------------------------
KEYWORD_FACT_RULES = [
    (["sip"],                                    "minimum_sip_amount",          0.80),
    (["kyc"],                                    "kyc_procedure",               0.90),
    (["expense"],                                "expense_ratio",               0.85),
    (["exit"],                                   "exit_load",                   0.95),
    (["manager"],                                "fund_manager",                0.95),
    (["objective"],                              "investment_objective",        0.95),
    (["benchmark"],                              "benchmark_index",             0.95),
    (["risk", "riskometer"],                     "riskometer",                  0.95),
    (["inception"],                              "inception_date",              0.95),
    (["lock-in", "lock in", "lockin", "elss"],   "elss_lock_in",               0.95),
    (["lump", "lumpsum", "lump sum"],            "minimum_lumpsum",             0.90),
    (["plan", "option"],                         "plans_options",               0.85),
    (["factsheet"],                              "factsheet_location",          0.90),
    (["statement"],                              "account_statement_procedure", 0.92),
    (["capital", "gains"],                       "capital_gains_procedure",     0.93),
    (["performance", "return"],                  "performance_value",           0.88),
]

VECTOR_FACT_RULES = [
    (["sip"],                                    "minimum_sip_amount",          0.85),
    (["kyc"],                                    "kyc_procedure",               0.88),
    (["expense"],                                "expense_ratio",               0.82),
    (["exit"],                                   "exit_load",                   0.92),
    (["manager"],                                "fund_manager",                0.91),
    (["objective"],                              "investment_objective",        0.96),
    (["benchmark"],                              "benchmark_index",             0.92),
    (["risk", "riskometer"],                     "riskometer",                  0.93),
    (["inception"],                              "inception_date",              0.94),
    (["lock-in", "lock in", "lockin", "elss"],   "elss_lock_in",               0.95),
    (["lump", "lumpsum", "lump sum"],            "minimum_lumpsum",             0.92),
    (["plan", "option"],                         "plans_options",               0.89),
    (["factsheet"],                              "factsheet_location",          0.91),
    (["statement"],                              "account_statement_procedure", 0.94),
    (["capital", "gains"],                       "capital_gains_procedure",     0.95),
    (["performance", "return"],                  "performance_value",           0.90),
]


def _match_score(q: str, rules: list) -> Optional[tuple]:
    """Return (fact_type, score) for the first matching rule, or None."""
    for keywords, fact_type, score in rules:
        if any(kw in q for kw in keywords):
            return fact_type, score
    return None


def _apply_filters(
    doc: Dict[str, Any],
    scheme_id: Optional[str],
    document_types: Optional[List[str]],
    fact_type: Optional[str],
    amc_level: bool,
) -> bool:
    """Return True if the passage survives all hard filters."""
    # 1. Scheme hard filter
    if not amc_level and scheme_id and scheme_id not in doc["scheme_ids"]:
        return False
    # 2. Document type filter
    if document_types and doc["document_type"] not in document_types:
        return False
    # 3. Fact type filter
    if fact_type and fact_type not in doc["fact_types"]:
        return False
    return True


class InMemoryKeywordSearch(RetrievalClient):
    """
    Keyword-based in-memory search over the dynamically loaded corpus.

    The corpus is built at import time from ``data/processed/*.json`` plus
    the hardcoded AMC procedural passages, so every processed scheme is
    automatically searchable without any code changes.
    """

    def search(
        self,
        query: str,
        scheme_id: Optional[str] = None,
        plan: str = "Direct",
        option: str = "Growth",
        limit: int = 20,
        document_types: Optional[List[str]] = None,
        fact_type: Optional[str] = None,
        amc_level: bool = False,
    ) -> List[Dict[str, Any]]:
        results = []
        q = query.lower()
        match = _match_score(q, KEYWORD_FACT_RULES)

        for doc in CORPUS:
            if not _apply_filters(doc, scheme_id, document_types, fact_type, amc_level):
                continue

            if fact_type:
                doc_copy = doc.copy()
                doc_copy["score"] = 0.90
                results.append(doc_copy)
            elif match:
                matched_fact_type, score = match
                if matched_fact_type in doc["fact_types"]:
                    doc_copy = doc.copy()
                    doc_copy["score"] = score
                    results.append(doc_copy)
            else:
                # Fallback: include full-text passages for unmatched queries
                if "full_text" in doc["fact_types"]:
                    doc_copy = doc.copy()
                    doc_copy["score"] = 0.50
                    results.append(doc_copy)

        return results[:limit]


class InMemoryVectorSearch(RetrievalClient):
    """
    Vector-based in-memory search over the dynamically loaded corpus.

    Note: In production this expects 1024-dimensional BGE Large vectors.
    This mock uses the same keyword heuristics as the keyword search but
    with slightly different (typically higher) confidence scores.
    """

    def search(
        self,
        query: str,
        scheme_id: Optional[str] = None,
        plan: str = "Direct",
        option: str = "Growth",
        limit: int = 20,
        document_types: Optional[List[str]] = None,
        fact_type: Optional[str] = None,
        amc_level: bool = False,
    ) -> List[Dict[str, Any]]:
        results = []
        q = query.lower()
        match = _match_score(q, VECTOR_FACT_RULES)

        for doc in CORPUS:
            if not _apply_filters(doc, scheme_id, document_types, fact_type, amc_level):
                continue

            if fact_type:
                doc_copy = doc.copy()
                doc_copy["score"] = 0.90
                results.append(doc_copy)
            elif match:
                matched_fact_type, score = match
                if matched_fact_type in doc["fact_types"]:
                    doc_copy = doc.copy()
                    doc_copy["score"] = score
                    results.append(doc_copy)
            else:
                # Fallback: include full-text passages for unmatched queries
                if "full_text" in doc["fact_types"]:
                    doc_copy = doc.copy()
                    doc_copy["score"] = 0.55
                    results.append(doc_copy)

        return results[:limit]

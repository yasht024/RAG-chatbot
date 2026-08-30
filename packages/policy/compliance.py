"""
compliance.py
-------------
Post-generation compliance validator for the HDFC Mutual Fund FAQ Assistant.

Checks every FACTUAL_ANSWER response against the following rules before it
reaches the caller:

  1. Citation domain must be an approved official source.
  2. Answer must not contain advice, recommendations, or guarantees.
  3. Answer must not compare/rank funds or calculate performance.
  4. Response footer must use "Last updated from sources: <date>" — NOT today's date.
  5. Sentence count must not exceed 3.

Any failure results in POLICY_REFUSAL with an explicit reason.
"""
import re
import datetime
from packages.contracts.schemas import FactualResponse, TerminalState

# ---------------------------------------------------------------------------
# Approved citation domains — ONLY these may appear in citation_url
# ---------------------------------------------------------------------------
APPROVED_CITATION_DOMAINS = {
    "hdfcfund.com",
    "amfiindia.com",
    "sebi.gov.in",
}

# ---------------------------------------------------------------------------
# Prohibited source domains — if any appear in the citation URL, reject
# ---------------------------------------------------------------------------
PROHIBITED_CITATION_DOMAINS = {
    "groww.in",
    "moneycontrol.com",
    "etmoney.com",
    "valueresearchonline.com",
    "morningstar.in",
    "zerodha.com",
    "kuvera.in",
    "scripbox.com",
}

# ---------------------------------------------------------------------------
# Advisory / recommendation language patterns
# ---------------------------------------------------------------------------
_ADVICE_PATTERNS = [
    r"\bshould (you |i )?invest\b",
    r"\brecommend\b",
    r"\bbuy (this|it|the fund)\b",
    r"\bguarantee[sd]?\b",
    r"\bwill (definitely|certainly|surely)\b",
    r"\bsafe(r|st)? (fund|investment|option)\b",
    r"\bbest fund\b",
]

# ---------------------------------------------------------------------------
# Performance comparison / ranking language patterns
# ---------------------------------------------------------------------------
_COMPARISON_PATTERNS = [
    r"\bbetter (than|performing)\b",
    r"\bhighest return\b",
    r"\btop performing\b",
    r"\brank(ed|ing|s)?\b",
    r"\bcompare[sd]?\b",
    r"\boutperform\b",
]


def _is_approved_url(url: str) -> bool:
    """Return True only if the URL belongs to an approved source domain."""
    if not url:
        return False
    lower = url.lower()
    # Hard-reject prohibited domains first
    for domain in PROHIBITED_CITATION_DOMAINS:
        if domain in lower:
            return False
    # Then confirm it is an approved domain
    return any(domain in lower for domain in APPROVED_CITATION_DOMAINS)


def _contains_advice(text: str) -> bool:
    lower = text.lower()
    return any(re.search(p, lower) for p in _ADVICE_PATTERNS)


def _contains_comparison(text: str) -> bool:
    lower = text.lower()
    return any(re.search(p, lower) for p in _COMPARISON_PATTERNS)


def enforce_compliance(response: FactualResponse) -> FactualResponse:
    """
    Enforces post-generation compliance constraints on every FACTUAL_ANSWER.

    Pass-through for non-factual states (refusals, errors).

    Checks (in order):
      1. Sentence count ≤ 3
      2. Citation URL must be an approved official domain (never Groww)
      3. Answer must not contain advisory language
      4. Answer must not contain comparison/ranking language
      5. Append correct source-date footer ("Last updated from sources: …")
    """
    if response.status != TerminalState.FACTUAL_ANSWER:
        return response

    answer_text = " ".join(response.answer_sentences)

    # --- Check 1: Sentence count ---
    if len(response.answer_sentences) > 3:
        response.status = TerminalState.POLICY_REFUSAL
        response.refusal_reason = "Response exceeded 3-sentence limit."
        response.answer_sentences = []
        return response

    # --- Check 2: Citation domain validation ---
    if not _is_approved_url(response.citation_url or ""):
        response.status = TerminalState.POLICY_REFUSAL
        response.refusal_reason = (
            "Citation URL is missing or belongs to a prohibited source. "
            "Only hdfcfund.com, amfiindia.com, and sebi.gov.in are approved."
        )
        response.answer_sentences = []
        return response

    # --- Check 3: Advisory language in generated answer ---
    if _contains_advice(answer_text):
        response.status = TerminalState.POLICY_REFUSAL
        response.refusal_reason = (
            "Generated answer contains investment advice or guarantee language "
            "which is not permitted."
        )
        response.answer_sentences = []
        return response

    # --- Check 4: Comparison/ranking language in generated answer ---
    if _contains_comparison(answer_text):
        response.status = TerminalState.POLICY_REFUSAL
        response.refusal_reason = (
            "Generated answer contains fund comparison or ranking language "
            "which is not permitted."
        )
        response.answer_sentences = []
        return response

    # --- Check 5: Source-date footer ---
    # Use the official source date from the passage — NEVER today's date.
    # If no source date is available, omit the footer rather than fabricating it.
    if response.source_date and response.answer_sentences:
        # Guard: do not append if already present
        footer = f"Last updated from sources: {response.source_date}"
        last = response.answer_sentences[-1]
        if footer not in last:
            response.answer_sentences.append(footer)

    return response

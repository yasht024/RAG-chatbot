"""
renderer.py
-----------
Translates the internal FactualResponse schema into the public-facing JSON
payload that matches the HDFC FAQ Assistant system prompt response format:

  FACTUAL_ANSWER:
    { status, answer, citation: { url, last_updated } }

  Error states:
    { status, error: { reason, code } }

The ``citation.last_updated`` field MUST carry the official source's
publication/effective date — NOT today's date — per the system prompt's
freshness rule.
"""

from packages.contracts.schemas import FactualResponse, TerminalState

# Human-readable error codes for each terminal error state
_ERROR_CODES = {
    TerminalState.INSUFFICIENT_EVIDENCE: "INSUFFICIENT_EVIDENCE",
    TerminalState.AMBIGUOUS_SCHEME: "AMBIGUOUS_SCHEME",
    TerminalState.SOURCE_CONFLICT: "SOURCE_CONFLICT",
    TerminalState.POLICY_REFUSAL: "POLICY_REFUSAL",
    TerminalState.SENSITIVE_DATA_WARNING: "SENSITIVE_DATA_WARNING",
    TerminalState.TEMPORARILY_UNAVAILABLE: "TEMPORARILY_UNAVAILABLE",
}


def render_response(internal_response: FactualResponse) -> dict:
    """
    Translates internal schemas to public-facing JSON payload.

    For FACTUAL_ANSWER responses the citation block carries the official source
    URL and its publication/effective date (from the corpus passage), not a
    generated date, complying with the system prompt freshness rule.
    """
    if internal_response.status == TerminalState.FACTUAL_ANSWER:
        payload: dict = {
            "status": internal_response.status.value,
            "answer": "\n".join(internal_response.answer_sentences) if internal_response.answer_sentences else None,
        }
        if internal_response.citation:
            payload["citation"] = internal_response.citation.dict(exclude_none=True)
        elif internal_response.citation_url:
            payload["citation"] = {
                "url": internal_response.citation_url,
                "last_updated": internal_response.source_date,
            }
        return payload

    # --- Error / refusal states ---
    status = internal_response.status
    reason = internal_response.refusal_reason or (
        "Request could not be processed due to insufficient evidence or ambiguity."
    )

    # Map policy-defined refusals to the system prompt wording
    if status == TerminalState.INSUFFICIENT_EVIDENCE:
        reason = reason or "Insufficient official evidence is available to verify this fact."
    elif status == TerminalState.POLICY_REFUSAL:
        reason = reason or (
            "I can provide verified facts about HDFC mutual fund schemes, "
            "but I cannot recommend which fund you should invest in."
        )

    return {
        "status": status.value,
        "error": {
            "code": _ERROR_CODES.get(status, "UNKNOWN_ERROR"),
            "reason": reason,
        },
    }

from packages.contracts.schemas import FactualResponse, TerminalState


def render_response(internal_response: FactualResponse) -> dict:
    """
    Translates internal schemas to public facing JSON payload.
    """
    base = {
        "status": internal_response.status.value,
        "answer": " ".join(internal_response.answer_sentences) if internal_response.answer_sentences else None,
        "citation": {
            "url": internal_response.citation_url,
            "last_updated": internal_response.source_date,
        }
        if internal_response.citation_url
        else None,
    }

    if internal_response.status != TerminalState.FACTUAL_ANSWER:
        base["error"] = {
            "reason": internal_response.refusal_reason
            or "Request could not be processed due to insufficient evidence or ambiguity."
        }
    return base

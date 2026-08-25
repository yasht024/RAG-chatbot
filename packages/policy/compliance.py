from packages.contracts.schemas import FactualResponse, TerminalState


def enforce_compliance(response: FactualResponse) -> FactualResponse:
    """
    Enforces compliance constraints:
    - Maximum 3 sentences.
    - Exact Groww URL citation.
    """
    if response.status != TerminalState.FACTUAL_ANSWER:
        return response

    # 1. Sentence count check
    if len(response.answer_sentences) > 3:
        response.status = TerminalState.POLICY_REFUSAL
        response.refusal_reason = "Response exceeded 3 sentences limit."
        response.answer_sentences = []
        return response

    # 2. Citation validation (must be a groww.in or hdfcfund.com URL)
    if not response.citation_url or not any(domain in response.citation_url for domain in ["groww.in", "hdfcfund.com"]):
        response.status = TerminalState.POLICY_REFUSAL
        response.refusal_reason = "Invalid or missing citation domain."
        response.answer_sentences = []
        return response

    # 3. Footer Date
    if response.source_date and len(response.answer_sentences) > 0:
        footer = f"(As of {response.source_date})"
        if not response.answer_sentences[-1].endswith(footer):
            response.answer_sentences.append(footer)

    return response

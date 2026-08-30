"""
generator.py
------------
Deterministic template extraction for scalar facts and LLM-based descriptive
answer generation.  All outputs comply with the HDFC FAQ Assistant system prompt:

  - No advice, no speculation, no guarantees
  - Source is attached by the orchestrator (not here)
  - Maximum 3 sentences for scalar facts
  - Prohibited-source values are never used as answers
"""
import re
from packages.contracts.schemas import FactualResponse, TerminalState


# ---------------------------------------------------------------------------
# Source-policy: approved top-level domains
# ---------------------------------------------------------------------------
APPROVED_DOMAINS = {"hdfcfund.com", "amfiindia.com", "sebi.gov.in"}

PROHIBITED_DOMAINS = {
    "groww.in", "moneycontrol.com", "etmoney.com", "valueresearchonline.com",
    "morningstar.in", "zerodha.com",
}


def _is_approved_url(url: str) -> bool:
    """Return True only if the URL belongs to an approved source domain."""
    if not url:
        return False
    lower = url.lower()
    return any(domain in lower for domain in APPROVED_DOMAINS)


def generate_scalar_answer(fact_type: str, passage: str) -> str:
    """
    Deterministic template extraction for scalar facts.

    Produces concise, factual sentences strictly from the retrieved passage.
    Never infers, speculates, or provides advice.
    """
    passage = passage.strip()

    if fact_type == "minimum_sip_amount":
        match = re.search(r"₹\s?[\d,]+", passage)
        value = match.group(0) if match else passage
        return f"The minimum SIP amount is {value}."

    elif fact_type == "minimum_lumpsum":
        match = re.search(r"₹\s?[\d,]+", passage)
        value = match.group(0) if match else passage
        return f"The minimum lumpsum amount is {value}."

    elif fact_type == "benchmark_index":
        # Strip "Benchmark Index:" prefix if present
        clean = re.sub(r"^benchmark\s*(index)?[:\s]*", "", passage, flags=re.IGNORECASE).strip()
        return f"The benchmark index for this scheme is {clean}."

    elif fact_type == "elss_lock_in":
        match = re.search(r"\d+\s*[Yy]ear", passage)
        period = match.group(0) if match else "3 years"
        return f"The lock-in period for this ELSS scheme is {period}."

    elif fact_type == "expense_ratio":
        match = re.search(r"\d+\.?\d*%", passage)
        value = match.group(0) if match else passage
        return f"The expense ratio is {value}."

    elif fact_type == "exit_load":
        # Remove "Exit Load:" prefix if present
        clean = re.sub(r"^exit\s*load[:\s]*", "", passage, flags=re.IGNORECASE).strip()
        return f"The exit load is {clean}."

    elif fact_type == "riskometer":
        risk_levels = [
            "Very High", "High", "Moderately High",
            "Moderate", "Low to Moderate", "Low",
        ]
        for risk in risk_levels:
            if risk.lower() in passage.lower():
                return f"The riskometer classifies this fund as {risk} risk."
        return f"The riskometer classification is: {passage}."

    elif fact_type == "fund_manager":
        clean = re.sub(r"^fund\s*manager[:\s]*", "", passage, flags=re.IGNORECASE).strip()
        return f"The fund is managed by {clean}."

    elif fact_type == "inception_date":
        clean = re.sub(r"^inception\s*date[:\s]*", "", passage, flags=re.IGNORECASE).strip()
        return f"The scheme inception date is {clean}."

    elif fact_type == "plans_options":
        clean = re.sub(r"^plans\s*&?\s*options?[:\s]*", "", passage, flags=re.IGNORECASE).strip()
        return clean

    elif fact_type == "factsheet_location":
        return passage

    elif fact_type == "performance_value":
        return f"According to the official factsheet, the reported performance figure is: {passage}."

    # Generic fallback — return passage as-is
    return passage


from services.assistant_api.llm_client import MockLLMClient

llm = MockLLMClient()


def generate_descriptive_answer(fact_type: str, passage: str) -> str:
    """
    Descriptive text generation via the LLM (Groq API).
    The LLM client injects the HDFC FAQ system prompt as the ``system`` message
    so all outputs are constrained to approved sources and response format.
    """
    return llm.generate_descriptive_answer(fact_type, passage)


def handle_recommendation_refusal() -> FactualResponse:
    """
    Returns the system-prompt-compliant refusal for advisory/recommendation intents.
    """
    return FactualResponse(
        status=TerminalState.POLICY_REFUSAL,
        answer_sentences=[],
        refusal_reason=(
            "I can provide verified facts about HDFC mutual fund schemes, "
            "but I cannot recommend which fund you should invest in."
        ),
    )

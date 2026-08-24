from typing import Dict, Any
from packages.contracts.schemas import FactualResponse, TerminalState
import re

def generate_scalar_answer(fact_type: str, passage: str) -> str:
    """
    Deterministic template extraction for scalar facts.
    """
    if fact_type == "minimum_sip_amount":
        match = re.search(r"₹\s?[\d,]+", passage)
        value = match.group(0) if match else "the specified amount"
        return f"The minimum SIP amount is {value}."
    elif fact_type == "minimum_lumpsum":
        match = re.search(r"₹\s?[\d,]+", passage)
        value = match.group(0) if match else "the specified amount"
        return f"The minimum lumpsum amount is {value}."
    elif fact_type == "benchmark_index":
        return f"The benchmark index for this scheme is {passage.strip()}."
    elif fact_type == "elss_lock_in":
        return "The lock-in period for this ELSS scheme is 3 years."
    elif fact_type == "expense_ratio":
        match = re.search(r"\d+\.\d+%", passage)
        value = match.group(0) if match else "the specified percentage"
        return f"The expense ratio is {value}."
    elif fact_type == "exit_load":
        # Simplified extraction for mock: just return the passage cleanly
        return f"The exit load is: {passage.strip()}"
    elif fact_type == "riskometer":
        # Look for typical risk levels
        risks = ["Low", "Low to Moderate", "Moderate", "Moderately High", "High", "Very High"]
        for risk in risks:
            if risk.lower() in passage.lower():
                return f"The riskometer indicates this fund is {risk} Risk."
        return f"The riskometer level is specified in the document."
    elif fact_type == "fund_manager":
        # Removing boilerplate
        clean_passage = passage.replace("Fund Manager:", "").strip()
        return f"The fund is managed by {clean_passage}."
    elif fact_type == "inception_date":
        return f"The inception date is {passage.strip()}."
    elif fact_type == "plans_options":
        return passage.strip()
    elif fact_type == "factsheet_location":
        return passage.strip()
    elif fact_type == "performance_value":
        return f"The reported performance is: {passage.strip()}"
    
    return passage

from services.assistant_api.llm_client import MockLLMClient
llm = MockLLMClient()

def generate_descriptive_answer(fact_type: str, passage: str) -> str:
    """
    Descriptive text generation leveraging the LLM.
    """
    return llm.generate_descriptive_answer(fact_type, passage)

def handle_recommendation_refusal() -> FactualResponse:
    """
    Returns a predefined refusal for recommendation intents.
    """
    return FactualResponse(
        status=TerminalState.POLICY_REFUSAL,
        answer_sentences=[],
        refusal_reason="This assistant provides only factual information and cannot offer investment advice or recommendations."
    )

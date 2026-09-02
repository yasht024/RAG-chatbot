import re
from typing import Dict, Any
from infra.environments.config import config


class QueryClassifier:
    """
    Layered Query Classifier:
    1. Deterministic rules engine (catches advice, recommendations, rankings, comparisons).
    2. Fact-type extractor.
    3. Conservative policy merger (prohibited/advisory classes always take precedence).
    """

    def __init__(self):
        # Advisory / Recommendation patterns
        self.advisory_patterns = [
            r"\bshould i\b",
            r"\b(?:would|can|could) you recommend\b",
            r"\brecommend(?:s|ed|ing|ation)?\b",
            r"\bis (?:it|this|that|the fund|this fund) (?:good|safe|better|best)\b",
            r"\bwhich fund should i\b",
            r"\btell me if i should\b",
            r"\badvice\b",
            r"\bwhether to buy\b",
            r"\bshould buy\b",
            r"\bshould invest\b",
            r"\bgood to invest\b",
            r"\b(?:which|what) (?:[a-z0-9]+\s+)?(?:fund|scheme) is (?:the )?(?:best|safest)\b",
            r"\bhow much (?:money )?will i (?:make|get|receive)\b",
            # Hindi patterns
            r"क्या मुझे.*निवेश",
            r"कौन सा फंड",
            r"सलाह",
            r"सुझाव",
            r"खरीदना चाहिए",
            r"निवेश करना चाहिए",
        ]

        # Performance / Comparison / Ranking patterns
        self.comparison_patterns = [
            r"\bwhich (?:[a-z0-9]+\s+)?(?:fund|scheme)s? (?:gives?|has|generates?|provides?|delivered) (?:the )?(?:highest|best|maximum|top) returns?\b",
            r"\bwhich (?:[a-z0-9]+\s+)?(?:fund|scheme)s? performed best\b",
            r"\bcompare (?:the )?(?:returns?|performance)?\b",
            r"\bwhich is better\b",
            r"\brank (?:the )?funds?\b",
            r"\btop performing\b",
            r"\bhighest returns?\b",
            r"\bbest (?:performing|returns?|fund)\b",
            r"\bcalculate (?:my )?returns?\b",
            # Hindi patterns
            r"सबसे अच्छा फंड",
            r"अधिक रिटर्न",
            r"बेहतर कौन",
            r"तुलना",
            r"कौन सा बेहतर है",
        ]

        # Fact type patterns
        self.fact_patterns = {
            "EXPENSE_RATIO": r"\b(?:expense ratio|ter|fee|charges?)\b|एक्सपेंस रेशियो|खर्च",
            "EXIT_LOAD": r"\b(?:exit load|redemption fee|penalty)\b|एग्जिट लोड|निकासी शुल्क",
            "MINIMUM_SIP": r"\b(?:min(?:imum)? sip|sip amount|start sip)\b|न्यूनतम एसआईपी|कम से कम एसआईपी",
            "MINIMUM_LUMP_SUM": r"\b(?:min(?:imum)? lump[- ]?sum|lumpsum amount)\b|न्यूनतम एकमुश्त|लम्पसम",
            "BENCHMARK": r"\b(?:benchmark|index tracking|benchmark index)\b|बेंचमार्क",
            "RISKOMETER": r"\b(?:riskometer|risk level|risk rating)\b|रिस्कोमीटर|जोखिम",
            "FUND_MANAGER": r"\b(?:fund manager|manager|who manages|managed by)\b|फंड मैनेजर|मैनेजर",
            "INCEPTION_DATE": r"\b(?:inception date|launch date|started on|start date)\b|शुरुआत की तारीख|लॉन्च डेट",
            "LOCK_IN": r"\b(?:lock[- ]?in|lock in period|elss lock in)\b|लॉक इन|लॉक-इन",
            "OBJECTIVE": r"\b(?:investment objective|objective of the fund)\b|उद्देश्य|लक्ष्य",
        }

    def classify_query(self, query: str) -> Dict[str, Any]:
        lower_query = query.lower()

        # 1. Extract Factual Fact Types
        extracted_fact = None
        for ftype, pattern in self.fact_patterns.items():
            if re.search(pattern, lower_query):
                extracted_fact = ftype
                break

        # 2. Check Prohibited / Comparison Classes
        is_advisory = any(re.search(p, lower_query) for p in self.advisory_patterns)
        is_comparison = any(re.search(p, lower_query) for p in self.comparison_patterns)

        # Conservative Policy Merger: Prohibited class wins disagreement
        if is_advisory:
            return {
                "query_class": "ADVISORY",
                "fact_type": None,
                "confidence": 0.99,
                "contains_advice": True,
                "policy_version": config.policy_version,
            }

        if is_comparison:
            if extracted_fact:
                # Comparison of objective attributes
                return {
                    "query_class": "ATTRIBUTE_COMPARISON",
                    "fact_type": extracted_fact,
                    "confidence": 0.99,
                    "contains_comparison": True,
                    "policy_version": config.policy_version,
                }
            else:
                # Performance or ranking comparison
                return {
                    "query_class": "PERFORMANCE_COMPARISON",
                    "fact_type": None,
                    "confidence": 0.99,
                    "contains_comparison": True,
                    "policy_version": config.policy_version,
                }

        # 3. Handle Standard Factual Query
        if extracted_fact:
            return {
                "query_class": "FACTUAL",
                "fact_type": extracted_fact,
                "confidence": 0.98,
                "contains_advice": False,
                "policy_version": config.policy_version,
            }

        # 3. Default fallback
        return {
            "query_class": "FACTUAL",
            "fact_type": None,
            "confidence": 0.85,
            "contains_advice": False,
            "policy_version": "2026-08-23.1",
        }

import re
from typing import List
from packages.policy.classifier import QueryClassifier

class QueryDecomposer:
    """
    Decomposes a query into multiple requested fact types.
    """
    def __init__(self):
        self.classifier = QueryClassifier()
        # Additional patterns covering AMC and performance queries
        self.extra_patterns = {
            "factsheet_location": r"\b(?:download|where is|get|find).*\bfactsheet\b",
            "account_statement_procedure": r"\baccount statement\b",
            "capital_gains_procedure": r"\b(?:capital-gains|capital gains)\b",
            "kyc_procedure": r"\bkyc\b",
            "plans_options": r"\b(?:plans|options)\b",
            "performance_value": r"\b(?:performance|return)s?\b",
        }
    
    def decompose(self, query: str) -> List[str]:
        lower_query = query.lower()
        requested_facts = []

        # 1. Fact patterns from Classifier
        for ftype, pattern in self.classifier.fact_patterns.items():
            if re.search(pattern, lower_query):
                normalized = self._normalize_fact_type(ftype)
                if normalized not in requested_facts:
                    requested_facts.append(normalized)
        
        # 2. Extra patterns (AMC level + Performance + Plans)
        for ftype, pattern in self.extra_patterns.items():
            if re.search(pattern, lower_query):
                if ftype not in requested_facts:
                    requested_facts.append(ftype)
                    
        return requested_facts

    def _normalize_fact_type(self, raw_type: str) -> str:
        mapping = {
            "MINIMUM_SIP": "minimum_sip_amount",
            "MINIMUM_LUMP_SUM": "minimum_lumpsum",
            "BENCHMARK": "benchmark_index",
            "EXPENSE_RATIO": "expense_ratio",
            "EXIT_LOAD": "exit_load",
            "FUND_MANAGER": "fund_manager",
            "RISKOMETER": "riskometer",
            "INCEPTION_DATE": "inception_date",
            "LOCK_IN": "elss_lock_in",
            "OBJECTIVE": "investment_objective",
        }
        return mapping.get(raw_type, raw_type.lower())

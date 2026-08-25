from typing import List, Optional


class DocumentRouter:
    """
    Routes fact types to their designated target document types.
    Enforces Phase 2B rules: Data from Factsheets/SID/KIM, processes from AMC pages.
    """

    # Define document types
    DOC_FACTSHEET = "FACTSHEET"
    DOC_SID = "SID"
    DOC_KIM = "KIM"
    DOC_AMC_PROC = "AMC_PROCEDURE"

    # Map fact classes to documents
    FACT_ROUTING_MAP = {
        "minimum_sip_amount": [DOC_FACTSHEET, DOC_KIM],
        "benchmark_index": [DOC_FACTSHEET, DOC_SID, DOC_KIM],
        "elss_lock_in": [DOC_FACTSHEET, DOC_SID, DOC_KIM],
        "expense_ratio": [DOC_FACTSHEET, DOC_KIM],
        "exit_load": [DOC_FACTSHEET, DOC_SID],
        "capital_gains_procedure": [DOC_AMC_PROC],
        "kyc_procedure": [DOC_AMC_PROC],
        "fund_manager": [DOC_FACTSHEET, DOC_SID, DOC_KIM],
        "investment_objective": [DOC_FACTSHEET, DOC_SID, DOC_KIM],
        "riskometer": [DOC_FACTSHEET, DOC_SID, DOC_KIM],
        "inception_date": [DOC_FACTSHEET, DOC_SID, DOC_KIM],
    }

    @classmethod
    def get_document_types_for_fact(cls, fact_type: Optional[str]) -> List[str]:
        """
        Returns the allowed document types for a given fact type.
        If no fact_type is identified, searches all by default.
        """
        if not fact_type:
            return [cls.DOC_FACTSHEET, cls.DOC_SID, cls.DOC_KIM, cls.DOC_AMC_PROC]

        return cls.FACT_ROUTING_MAP.get(fact_type, [cls.DOC_FACTSHEET, cls.DOC_SID, cls.DOC_KIM, cls.DOC_AMC_PROC])

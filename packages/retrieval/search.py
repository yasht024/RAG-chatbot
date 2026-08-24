from typing import List, Dict, Any, Optional
from packages.retrieval.interfaces import RetrievalClient

# In-memory mock corpus representing Phase 2B expanded search space
MOCK_CORPUS = [
    {
        "passage_id": "passage_mock_1",
        "document_id": "doc_hdfc_midcap_factsheet",
        "document_type": "FACTSHEET",
        "scheme_ids": ["hdfc_mid_cap"],
        "plan": "Direct",
        "option": "Growth",
        "normalized_text": "The minimum SIP amount for HDFC Mid-Cap Opportunities Fund is ₹100.",
        "fact_types": ["minimum_sip_amount"],
        "is_table": False,
        "publication_date": "2026-08-23",
        "source_url": "https://www.hdfcfund.com/our-funds/equity-funds/hdfc-mid-cap-opportunities-fund"
    },
    {
        "passage_id": "passage_mock_2",
        "document_id": "doc_hdfc_midcap_factsheet",
        "document_type": "FACTSHEET",
        "scheme_ids": ["hdfc_mid_cap"],
        "plan": "Direct",
        "option": "Growth",
        "normalized_text": "Expense Ratio: 0.85%",
        "fact_types": ["expense_ratio"],
        "is_table": True,
        "publication_date": "2026-08-23",
        "source_url": "https://www.hdfcfund.com/our-funds/equity-funds/hdfc-mid-cap-opportunities-fund"
    },
    {
        "passage_id": "passage_mock_3",
        "document_id": "doc_hdfc_amc_proc",
        "document_type": "AMC_PROCEDURE",
        "scheme_ids": [],
        "plan": "ALL",
        "option": "ALL",
        "normalized_text": "To update your KYC, visit the AMC portal and submit form 10.",
        "fact_types": ["kyc_procedure"],
        "is_table": False,
        "publication_date": "2026-07-01",
        "source_url": "https://groww.in/mutual-funds/default"
    },
    {
        "passage_id": "passage_mock_conflict_1",
        "document_id": "doc_hdfc_midcap_amc",
        "document_type": "FACTSHEET",
        "scheme_ids": ["hdfc_mid_cap"],
        "plan": "Direct",
        "option": "Growth",
        "normalized_text": "Exit Load: 1%",
        "fact_types": ["exit_load"],
        "is_table": False,
        "publication_date": "2026-08-20",
        "source_url": "https://hdfcfund.com/scheme/hdfc-mid-cap"
    },
    {
        "passage_id": "passage_mock_conflict_2",
        "document_id": "doc_hdfc_midcap_groww",
        "document_type": "FACTSHEET",
        "scheme_ids": ["hdfc_mid_cap"],
        "plan": "Direct",
        "option": "Growth",
        "normalized_text": "Exit Load: 1.5%",
        "fact_types": ["exit_load"],
        "is_table": False,
        "publication_date": "2026-08-23",
        "source_url": "https://groww.in/mutual-funds/hdfc-mid-cap"
    },
    {
        "passage_id": "passage_mock_unresolved_1",
        "document_id": "doc_unresolved_groww1",
        "document_type": "FACTSHEET",
        "scheme_ids": ["hdfc_mid_cap"],
        "plan": "Direct",
        "option": "Growth",
        "normalized_text": "Fund Manager: Rahul",
        "fact_types": ["fund_manager"],
        "is_table": False,
        "publication_date": "2026-08-23",
        "source_url": "https://groww.in/mutual-funds/hdfc-mid-cap-a"
    },
    {
        "passage_id": "passage_mock_unresolved_2",
        "document_id": "doc_unresolved_groww2",
        "document_type": "FACTSHEET",
        "scheme_ids": ["hdfc_mid_cap"],
        "plan": "Direct",
        "option": "Growth",
        "normalized_text": "Fund Manager: Gopal",
        "fact_types": ["fund_manager"],
        "is_table": False,
        "publication_date": "2026-08-23",
        "source_url": "https://hdfcfund.com/scheme/hdfc-mid-cap-b"
    },
    {
        "passage_id": "passage_mock_objective",
        "document_id": "doc_hdfc_midcap_objective",
        "document_type": "FACTSHEET",
        "scheme_ids": ["hdfc_mid_cap"],
        "plan": "Direct",
        "option": "Growth",
        "normalized_text": "The investment objective of the scheme is to provide long-term capital appreciation.",
        "fact_types": ["investment_objective"],
        "is_table": False,
        "publication_date": "2026-08-23",
        "source_url": "https://groww.in/mutual-funds/hdfc-mid-cap-objective"
    },
    {
        "passage_id": "passage_mock_benchmark",
        "document_id": "doc_hdfc_midcap_benchmark",
        "document_type": "FACTSHEET",
        "scheme_ids": ["hdfc_mid_cap"],
        "plan": "Direct",
        "option": "Growth",
        "normalized_text": "Benchmark: NIFTY Midcap 150 TRI",
        "fact_types": ["benchmark_index"],
        "is_table": False,
        "publication_date": "2026-08-23",
        "source_url": "https://www.hdfcfund.com/our-funds/equity-funds/hdfc-mid-cap-opportunities-fund"
    },
    {
        "passage_id": "passage_mock_riskometer",
        "document_id": "doc_hdfc_midcap_riskometer",
        "document_type": "FACTSHEET",
        "scheme_ids": ["hdfc_mid_cap"],
        "plan": "Direct",
        "option": "Growth",
        "normalized_text": "Riskometer: Very High",
        "fact_types": ["riskometer"],
        "is_table": False,
        "publication_date": "2026-08-23",
        "source_url": "https://www.hdfcfund.com/our-funds/equity-funds/hdfc-mid-cap-opportunities-fund"
    },
    {
        "passage_id": "passage_mock_inception",
        "document_id": "doc_hdfc_midcap_inception",
        "document_type": "FACTSHEET",
        "scheme_ids": ["hdfc_mid_cap"],
        "plan": "Direct",
        "option": "Growth",
        "normalized_text": "Inception Date: 25 June 2007",
        "fact_types": ["inception_date"],
        "is_table": False,
        "publication_date": "2026-08-23",
        "source_url": "https://www.hdfcfund.com/our-funds/equity-funds/hdfc-mid-cap-opportunities-fund"
    },
    {
        "passage_id": "passage_mock_elss_lockin",
        "document_id": "doc_hdfc_elss_lockin",
        "document_type": "FACTSHEET",
        "scheme_ids": ["hdfc_elss_tax_saver"],
        "plan": "Direct",
        "option": "Growth",
        "normalized_text": "Lock-in Period: 3 Years",
        "fact_types": ["elss_lock_in"],
        "is_table": False,
        "publication_date": "2026-08-23",
        "source_url": "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth"
    },
    {
        "passage_id": "passage_mock_lumpsum",
        "document_id": "doc_hdfc_midcap_lumpsum",
        "document_type": "FACTSHEET",
        "scheme_ids": ["hdfc_mid_cap"],
        "plan": "Direct",
        "option": "Growth",
        "normalized_text": "Min Lumpsum: ₹5,000",
        "fact_types": ["minimum_lumpsum"],
        "is_table": False,
        "publication_date": "2026-08-23",
        "source_url": "https://www.hdfcfund.com/our-funds/equity-funds/hdfc-mid-cap-opportunities-fund"
    },
    {
        "passage_id": "passage_mock_plans",
        "document_id": "doc_hdfc_midcap_plans",
        "document_type": "FACTSHEET",
        "scheme_ids": ["hdfc_mid_cap"],
        "plan": "ALL",
        "option": "ALL",
        "normalized_text": "Available Plans: Direct and Regular. Options: Growth and IDCW.",
        "fact_types": ["plans_options"],
        "is_table": False,
        "publication_date": "2026-08-23",
        "source_url": "https://www.hdfcfund.com/our-funds/equity-funds/hdfc-mid-cap-opportunities-fund"
    },
    {
        "passage_id": "passage_mock_factsheet_loc",
        "document_id": "doc_amc_factsheet_loc",
        "document_type": "AMC_PROCEDURE",
        "scheme_ids": [],
        "plan": "ALL",
        "option": "ALL",
        "normalized_text": "You can download the official factsheet from the 'Downloads' section on the HDFC AMC website.",
        "fact_types": ["factsheet_location"],
        "is_table": False,
        "publication_date": "2026-08-23",
        "source_url": "https://www.hdfcfund.com/investor-desk/downloads/factsheets"
    },
    {
        "passage_id": "passage_mock_account_stmt",
        "document_id": "doc_amc_account_stmt",
        "document_type": "AMC_PROCEDURE",
        "scheme_ids": [],
        "plan": "ALL",
        "option": "ALL",
        "normalized_text": "To download your account statement, log in to the HDFC Mutual Fund investor portal or request it via SMS.",
        "fact_types": ["account_statement_procedure"],
        "is_table": False,
        "publication_date": "2026-08-23",
        "source_url": "https://www.hdfcfund.com/investor-desk/account-statement"
    },
    {
        "passage_id": "passage_mock_capital_gains",
        "document_id": "doc_amc_capital_gains",
        "document_type": "AMC_PROCEDURE",
        "scheme_ids": [],
        "plan": "ALL",
        "option": "ALL",
        "normalized_text": "Capital-gains statements can be obtained by sending an email to our support desk from your registered email ID.",
        "fact_types": ["capital_gains_procedure"],
        "is_table": False,
        "publication_date": "2026-08-23",
        "source_url": "https://www.hdfcfund.com/investor-desk/capital-gains"
    },
    {
        "passage_id": "passage_mock_performance",
        "document_id": "doc_hdfc_midcap_performance",
        "document_type": "FACTSHEET",
        "scheme_ids": ["hdfc_mid_cap"],
        "plan": "Direct",
        "option": "Growth",
        "normalized_text": "1 Year Return: 15.4%",
        "fact_types": ["performance_value"],
        "is_table": True,
        "publication_date": "2026-08-23",
        "source_url": "https://www.hdfcfund.com/our-funds/equity-funds/hdfc-mid-cap-opportunities-fund"
    },
    {
        "passage_id": "passage_mock_largecap_expense",
        "document_id": "doc_hdfc_largecap_factsheet",
        "document_type": "FACTSHEET",
        "scheme_ids": ["hdfc_large_cap"],
        "plan": "Direct",
        "option": "Growth",
        "normalized_text": "Expense Ratio: 0.95%",
        "fact_types": ["expense_ratio"],
        "is_table": True,
        "publication_date": "2026-08-23",
        "source_url": "https://www.hdfcfund.com/our-funds/equity-funds/hdfc-top-100-fund"
    },
    {
        "passage_id": "passage_mock_largecap_exitload",
        "document_id": "doc_hdfc_largecap_factsheet",
        "document_type": "FACTSHEET",
        "scheme_ids": ["hdfc_large_cap"],
        "plan": "Direct",
        "option": "Growth",
        "normalized_text": "Exit Load: 1% if redeemed within 1 year.",
        "fact_types": ["exit_load"],
        "is_table": False,
        "publication_date": "2026-08-23",
        "source_url": "https://www.hdfcfund.com/our-funds/equity-funds/hdfc-top-100-fund"
    }
]

class InMemoryKeywordSearch(RetrievalClient):
    """InMemory Search simulating database retrieval for Phase 2B."""
    def search(
        self, 
        query: str, 
        scheme_id: Optional[str] = None, 
        plan: str = "Direct", 
        option: str = "Growth", 
        limit: int = 20,
        document_types: Optional[List[str]] = None,
        fact_type: Optional[str] = None,
        amc_level: bool = False
    ) -> List[Dict[str, Any]]:
        results = []
        q = query.lower()
        
        for doc in MOCK_CORPUS:
            # 1. Scheme Hard Filter
            if not amc_level and scheme_id and scheme_id not in doc["scheme_ids"]:
                continue
                
            # 2. Document Type Routing Filter
            if document_types and doc["document_type"] not in document_types:
                continue

            # 3. Fact Type Filter
            if fact_type and fact_type not in doc["fact_types"]:
                continue
                
            # Keyword matching logic mock
            if "sip" in q and "minimum_sip_amount" in doc["fact_types"]:
                doc_copy = doc.copy()
                doc_copy["score"] = 0.8
                results.append(doc_copy)
            elif "kyc" in q and "kyc_procedure" in doc["fact_types"]:
                doc_copy = doc.copy()
                doc_copy["score"] = 0.9
                results.append(doc_copy)
            elif "expense" in q and "expense_ratio" in doc["fact_types"]:
                doc_copy = doc.copy()
                doc_copy["score"] = 0.85
                results.append(doc_copy)
            elif "exit" in q and "exit_load" in doc["fact_types"]:
                doc_copy = doc.copy()
                doc_copy["score"] = 0.95
                results.append(doc_copy)
            elif "manager" in q and "fund_manager" in doc["fact_types"]:
                doc_copy = doc.copy()
                doc_copy["score"] = 0.95
                results.append(doc_copy)
            elif "objective" in q and "investment_objective" in doc["fact_types"]:
                doc_copy = doc.copy()
                doc_copy["score"] = 0.95
                results.append(doc_copy)
            elif "benchmark" in q and "benchmark_index" in doc["fact_types"]:
                doc_copy = doc.copy()
                doc_copy["score"] = 0.95
                results.append(doc_copy)
            elif "risk" in q and "riskometer" in doc["fact_types"]:
                doc_copy = doc.copy()
                doc_copy["score"] = 0.95
                results.append(doc_copy)
            elif "inception" in q and "inception_date" in doc["fact_types"]:
                doc_copy = doc.copy()
                doc_copy["score"] = 0.95
                results.append(doc_copy)
            elif ("lock-in" in q or "elss" in q) and "elss_lock_in" in doc["fact_types"]:
                doc_copy = doc.copy()
                doc_copy["score"] = 0.95
                results.append(doc_copy)
            elif ("lump" in q or "spend" in q or "amount" in q) and "minimum_lumpsum" in doc["fact_types"]:
                doc_copy = doc.copy()
                doc_copy["score"] = 0.90
                results.append(doc_copy)
            elif ("plan" in q or "option" in q) and "plans_options" in doc["fact_types"]:
                doc_copy = doc.copy()
                doc_copy["score"] = 0.85
                results.append(doc_copy)
            elif "factsheet" in q and "factsheet_location" in doc["fact_types"]:
                doc_copy = doc.copy()
                doc_copy["score"] = 0.90
                results.append(doc_copy)
            elif "statement" in q and "account_statement_procedure" in doc["fact_types"]:
                doc_copy = doc.copy()
                doc_copy["score"] = 0.92
                results.append(doc_copy)
            elif ("capital" in q or "gains" in q) and "capital_gains_procedure" in doc["fact_types"]:
                doc_copy = doc.copy()
                doc_copy["score"] = 0.93
                results.append(doc_copy)
            elif ("performance" in q or "return" in q) and "performance_value" in doc["fact_types"]:
                doc_copy = doc.copy()
                doc_copy["score"] = 0.88
                results.append(doc_copy)
                
        return results

class InMemoryVectorSearch(RetrievalClient):
    """
    InMemory Vector Search for Phase 2B.
    Note: In production, this expects 1024-dimensional BGE Large vectors.
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
        amc_level: bool = False
    ) -> List[Dict[str, Any]]:
        results = []
        q = query.lower()
        
        for doc in MOCK_CORPUS:
            # 1. Scheme Hard Filter
            if not amc_level and scheme_id and scheme_id not in doc["scheme_ids"]:
                continue
                
            # 2. Document Type Routing Filter
            if document_types and doc["document_type"] not in document_types:
                continue

            # 3. Fact Type Filter
            if fact_type and fact_type not in doc["fact_types"]:
                continue
                
            # Vector matching logic mock (similar for simplicity, slightly diff scores)
            if "sip" in q and "minimum_sip_amount" in doc["fact_types"]:
                doc_copy = doc.copy()
                doc_copy["score"] = 0.85
                results.append(doc_copy)
            elif "expense" in q and "expense_ratio" in doc["fact_types"]:
                doc_copy = doc.copy()
                doc_copy["score"] = 0.82
                results.append(doc_copy)
            elif "kyc" in q and "kyc_procedure" in doc["fact_types"]:
                doc_copy = doc.copy()
                doc_copy["score"] = 0.88
                results.append(doc_copy)
            elif "exit" in q and "exit_load" in doc["fact_types"]:
                doc_copy = doc.copy()
                doc_copy["score"] = 0.92
                results.append(doc_copy)
            elif "manager" in q and "fund_manager" in doc["fact_types"]:
                doc_copy = doc.copy()
                doc_copy["score"] = 0.91
                results.append(doc_copy)
            elif "objective" in q and "investment_objective" in doc["fact_types"]:
                doc_copy = doc.copy()
                doc_copy["score"] = 0.96
                results.append(doc_copy)
            elif "benchmark" in q and "benchmark_index" in doc["fact_types"]:
                doc_copy = doc.copy()
                doc_copy["score"] = 0.92
                results.append(doc_copy)
            elif "risk" in q and "riskometer" in doc["fact_types"]:
                doc_copy = doc.copy()
                doc_copy["score"] = 0.93
                results.append(doc_copy)
            elif "inception" in q and "inception_date" in doc["fact_types"]:
                doc_copy = doc.copy()
                doc_copy["score"] = 0.94
                results.append(doc_copy)
            elif ("lock-in" in q or "elss" in q) and "elss_lock_in" in doc["fact_types"]:
                doc_copy = doc.copy()
                doc_copy["score"] = 0.95
                results.append(doc_copy)
            elif ("lump" in q or "spend" in q or "amount" in q) and "minimum_lumpsum" in doc["fact_types"]:
                doc_copy = doc.copy()
                doc_copy["score"] = 0.92
                results.append(doc_copy)
            elif ("plan" in q or "option" in q) and "plans_options" in doc["fact_types"]:
                doc_copy = doc.copy()
                doc_copy["score"] = 0.89
                results.append(doc_copy)
            elif "factsheet" in q and "factsheet_location" in doc["fact_types"]:
                doc_copy = doc.copy()
                doc_copy["score"] = 0.91
                results.append(doc_copy)
            elif "statement" in q and "account_statement_procedure" in doc["fact_types"]:
                doc_copy = doc.copy()
                doc_copy["score"] = 0.94
                results.append(doc_copy)
            elif ("capital" in q or "gains" in q) and "capital_gains_procedure" in doc["fact_types"]:
                doc_copy = doc.copy()
                doc_copy["score"] = 0.95
                results.append(doc_copy)
            elif ("performance" in q or "return" in q) and "performance_value" in doc["fact_types"]:
                doc_copy = doc.copy()
                doc_copy["score"] = 0.90
                results.append(doc_copy)
                
        return results

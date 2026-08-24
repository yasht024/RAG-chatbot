import sys
sys.path.append("c:/Users/yash.tiwari/OneDrive/Desktop/Milestone - RAG")

from packages.retrieval.search import InMemoryKeywordSearch

searcher = InMemoryKeywordSearch()
res = searcher.search(
    query="who is the current fund manager?",
    scheme_id="hdfc_mid_cap",
    fact_type="fund_manager"
)
print("SEARCH_MANAGER:", len(res))

res2 = searcher.search(
    query="what is the riskometer classification?",
    scheme_id="hdfc_mid_cap",
    fact_type="riskometer"
)
print("SEARCH_RISK:", len(res2))

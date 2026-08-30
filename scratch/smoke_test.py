import sys
sys.path.insert(0, '.')
from packages.retrieval.search import InMemoryKeywordSearch, CORPUS

print(f"Total passages loaded: {len(CORPUS)}")

schemes = set(s for doc in CORPUS for s in doc['scheme_ids'])
print(f"Unique schemes in corpus: {len(schemes)}")

ks = InMemoryKeywordSearch()

tests = [
    ("What is the minimum SIP amount for HDFC Small Cap Fund", "hdfc_small_cap"),
    ("What is the exit load of HDFC Flexi Cap Fund?", "hdfc_flexi_cap"),
    ("What is the riskometer classification of HDFC Small Cap Fund?", "hdfc_small_cap"),
    # Previously working ones should still work
    ("What is the minimum SIP for HDFC Mid Cap?", "hdfc_mid_cap"),
    ("What is the exit load of HDFC Mid Cap?", "hdfc_mid_cap"),
]

print()
for query, scheme in tests:
    results = ks.search(query, scheme_id=scheme)
    status = "PASS" if results else "FAIL"
    if results:
        print(f"{status}: [{scheme}]")
        print(f"       Q: {query}")
        answer = results[0]['normalized_text'].replace('\u20b9', 'Rs.')
        print(f"       A: {answer} (score={results[0]['score']})")
    else:
        print(f"{status}: [{scheme}] -> NO RESULTS")
        print(f"       Q: {query}")
    print()

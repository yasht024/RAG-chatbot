import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from packages.retrieval.search import MOCK_CORPUS

def main():
    counts = {}
    for passage in MOCK_CORPUS:
        # User query used 'scheme_id', but the field is 'scheme_ids'.
        # We will explode the list like a JOIN or just treat the list as the grouping key.
        # Let's count by each individual scheme_id in the list, and if empty, count as 'NULL' or empty.
        s_ids = passage.get("scheme_ids", [])
        if not s_ids:
            s_ids = ["NULL"]
        for s_id in s_ids:
            counts[s_id] = counts.get(s_id, 0) + 1

    print("| scheme_id | chunk_count |")
    print("| :--- | :--- |")
    for s_id in sorted(counts.keys()):
        print(f"| {s_id} | {counts[s_id]} |")

if __name__ == "__main__":
    main()

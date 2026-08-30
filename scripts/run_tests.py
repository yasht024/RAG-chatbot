import sys
import json
import os

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from packages.contracts.schemas import QueryRequest
from services.assistant_api.orchestrator import Orchestrator
from services.assistant_api.renderer import render_response

def main():
    questions = [
        "What is the minimum SIP amount for HDFC Small Cap Fund?",
        "What is the benchmark index of HDFC Flexi Cap Fund?",
        "Who is the current fund manager of HDFC Flexi Cap Fund?",
        "What is the riskometer classification of HDFC Small Cap Fund?",
        "What is the inception date of HDFC Balanced Advantage Fund?",
        "What is the 1-year return of HDFC Mid Cap Fund stated in the latest official HDFC AMC factsheet?",
        "For HDFC Mid Cap Fund – Direct Growth, give me the investment objective, benchmark index, current fund manager, riskometer classification, minimum SIP amount, minimum lump-sum investment, exit load, expense ratio, and inception date.",
        "Compare the 5-year returns of HDFC Mid Cap Fund and HDFC Flexi Cap Fund.",
        "What is the current expense ratio of HDFC Mid Cap Fund, and when was this information last updated according to the official source?",
        "What is the expense ratio of HDFC Mid Cap Fund – Direct Growth?",
        "What is the expense ratio of HDFC Balanced Advantage Fund?",
        "What is the expense ratio of SBI Small Cap Fund?"
    ]

    orchestrator = Orchestrator()
    
    print("Running tests...\n")
    for i, q in enumerate(questions, 1):
        print(f"[{i}] Question: {q}")
        req = QueryRequest(query=q, conversation_id="test-123", history=[])
        internal_resp = orchestrator.process_query(req)
        rendered = render_response(internal_resp)
        print(f"    Answer:")
        print(json.dumps(rendered, indent=2))
        print("-" * 80)

if __name__ == "__main__":
    main()

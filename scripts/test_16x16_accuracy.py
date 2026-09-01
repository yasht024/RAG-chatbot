import sys
import json
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[1]))

from packages.contracts.schemas import QueryRequest, TerminalState
from services.assistant_api.orchestrator import Orchestrator

# 16 Representative Schemes
SCHEMES = [
    "hdfc mid cap",
    "hdfc flexi cap",
    "hdfc small cap",
    "hdfc large and mid cap",
    "hdfc large cap",
    "hdfc multi cap",
    "hdfc focused",
    "hdfc value",
    "hdfc elss tax saver",
    "hdfc mnc",
    "hdfc business cycle",
    "hdfc defence",
    "hdfc consumption",
    "hdfc transportation and logistics",
    "hdfc technology",
    "hdfc nifty 50 index",
]

# 16 Parameter queries (using {scheme} as placeholder)
PARAMETERS = {
    "SIP amounts": "what is the minimum sip amount for {scheme}?",
    "Expense ratios": "what is the expense ratio of {scheme}?",
    "Benchmarks": "what is the benchmark for {scheme}?",
    "Lock-in periods": "what is the lock-in period for {scheme}?",
    "KYC procedures": "what is the kyc procedure for {scheme}?",
    "Exit loads": "what is the exit load for {scheme}?",
    "Fund managers": "who are the fund managers of {scheme}?",
    "Investment objectives": "what is the investment objective of {scheme}?",
    "Riskometers": "what is the riskometer rating for {scheme}?",
    "Inception dates": "what is the inception date of {scheme}?",
    "Lump sum minimums": "what is the minimum lumpsum amount for {scheme}?",
    "Plans/Options": "what plans and options are available for {scheme}?",
    "Factsheets": "where can I find the factsheet for {scheme}?",
    "Account statements": "how to get my account statement for {scheme}?",
    "Capital gains": "how do I download my capital gains statement for {scheme}?",
    "Fund performance": "what is the 1 year performance of {scheme}?",
}


def main():
    print("Initializing Orchestrator for 16x16 Validation Matrix...")
    orchestrator = Orchestrator()

    results = []

    total_queries = len(SCHEMES) * len(PARAMETERS)
    print(f"Total queries to run: {total_queries}")

    counter = 1
    for scheme in SCHEMES:
        print(f"\n--- Testing Scheme: {scheme.upper()} ---")
        for param_name, query_template in PARAMETERS.items():
            query = query_template.format(scheme=scheme)
            request = QueryRequest(query=query, conversation_id=f"test_{int(time.time())}")

            print(f"[{counter}/{total_queries}] Testing {param_name}... ", end="", flush=True)

            try:
                response = orchestrator.process_query(request)
                status = response.status.value

                result_entry = {
                    "scheme": scheme,
                    "parameter": param_name,
                    "query": query,
                    "status": status,
                    "answer": getattr(response, "answer", None),
                    "source_url": getattr(response, "source_url", None),
                    "last_updated_date": getattr(response, "last_updated_date", None),
                    "refusal_reason": getattr(response, "refusal_reason", None),
                }
                results.append(result_entry)

                if response.status == TerminalState.FACTUAL_ANSWER:
                    print("SUCCESS")
                else:
                    print(f"FAILED ({status})")
            except Exception as e:
                print(f"ERROR: {e}")
                results.append(
                    {"scheme": scheme, "parameter": param_name, "query": query, "status": "ERROR", "error": str(e)}
                )

            counter += 1

    # Output results to a file
    output_path = Path(__file__).parents[1] / "docs" / "reports" / "16x16_results.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(results, f, indent=4)

    print(f"\nCompleted 16x16 evaluation. Results saved to {output_path}")

    # Calculate summary
    success = sum(1 for r in results if r.get("status") == "FACTUAL_ANSWER")
    failed = total_queries - success
    print(f"Summary: {success} successful, {failed} failed/refused/error.")


if __name__ == "__main__":
    main()

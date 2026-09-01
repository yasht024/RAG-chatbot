import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[1]))

from packages.contracts.schemas import QueryRequest, TerminalState
from services.assistant_api.orchestrator import Orchestrator

def main():
    # Initialize the orchestrator
    print("Initializing Orchestrator...")
    orchestrator = Orchestrator()
    
    # Test queries mapping to each supported category
    test_queries = {
        "SIP amounts": "what is the minimum sip amount for hdfc mid cap?",
        "Expense ratios": "what is the expense ratio of hdfc flexi cap?",
        "Benchmarks": "what is the benchmark for hdfc small cap?",
        "Lock-in periods (ELSS)": "what is the lock-in period for hdfc elss tax saver?",
        "KYC procedures": "what is the kyc procedure?",
        "Exit loads": "what is the exit load for hdfc mid cap?",
        "Fund managers": "who are the fund managers of hdfc mid cap?",
        "Investment objectives": "what is the investment objective of hdfc mid cap?",
        "Riskometers": "what is the riskometer rating for hdfc mid cap?",
        "Inception dates": "what is the inception date of hdfc mid cap?",
        "Lump sum minimums": "what is the minimum lumpsum amount for hdfc mid cap?",
        "Plans/Options": "what plans and options are available for hdfc mid cap?",
        "Factsheets": "where can I find the factsheet?",
        "Account statements": "how to get my account statement?",
        "Capital gains": "how do I download my capital gains statement?",
        "Fund performance": "what is the 1 year performance of hdfc mid cap?",
    }
    
    print("\nStarting comprehensive query testing...")
    print("=" * 120)
    print(f"{'Category':<25} | {'Status':<30} | {'Result'}")
    print("-" * 120)
    
    issues = 0
    failed_details = []
    
    for category, query in test_queries.items():
        request = QueryRequest(query=query, conversation_id="test_session")
        try:
            response = orchestrator.process_query(request)
            status = response.status.value
            
            if response.status == TerminalState.FACTUAL_ANSWER:
                result = "SUCCESS"
            else:
                result = "FAILED"
                issues += 1
                failed_details.append((category, query, status, response.refusal_reason))
        except Exception as e:
            status = "ERROR"
            result = f"FAILED: Exception raised - {e}"
            issues += 1
            failed_details.append((category, query, status, str(e)))
            
        print(f"{category:<25} | {status:<30} | {result}")
        
    print("=" * 120)
    print(f"Total queries tested: {len(test_queries)}")
    print(f"Successful: {len(test_queries) - issues}")
    print(f"Failed: {issues}")
    
    if issues > 0:
        print("\n--- Failure Details ---")
        for cat, q, st, msg in failed_details:
            print(f"\nCategory: {cat}")
            print(f"Query:    '{q}'")
            print(f"Status:   {st}")
            print(f"Reason:   {msg}")

if __name__ == '__main__':
    main()

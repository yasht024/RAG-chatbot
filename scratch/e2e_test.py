"""Full end-to-end trace for the failing queries via the Orchestrator."""
import sys, os
sys.path.insert(0, '.')

from packages.contracts.schemas import QueryRequest
from services.assistant_api.orchestrator import Orchestrator

orch = Orchestrator()

queries = [
    "What is the minimum SIP amount for HDFC Small Cap Fund?",
    "What is the exit load of HDFC Flexi Cap Fund?",
    "What is the riskometer classification of HDFC Small Cap Fund?",
    # Baseline - should still work
    "What is the minimum SIP for HDFC Mid Cap?",
]

for q in queries:
    req = QueryRequest(query=q, conversation_id="test-session-001")
    resp = orch.process_query(req)
    print(f"Q: {q}")
    print(f"   status : {resp.status}")
    if hasattr(resp, 'answer_sentences') and resp.answer_sentences:
        safe = [s.replace('\u20b9', 'Rs.') for s in resp.answer_sentences]
        print(f"   answer : {safe}")
    if hasattr(resp, 'refusal_reason') and resp.refusal_reason:
        print(f"   reason : {resp.refusal_reason}")
    print()

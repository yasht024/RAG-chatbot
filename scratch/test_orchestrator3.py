import sys

sys.path.append("c:/Users/yash.tiwari/OneDrive/Desktop/Milestone - RAG")

from packages.contracts.schemas import QueryRequest, Message
from services.assistant_api.orchestrator import Orchestrator

orc = Orchestrator()

history = [
    Message(role="user", content="How can I download my account statement?"),
    Message(
        role="assistant",
        content="To download your account statement, log in to the HDFC Mutual Fund investor portal or request it via SMS. (As of 2026-08-23)",
    ),
]

req = QueryRequest(query="Who is the current fund manager?", conversation_id="123", history=history)

res = orc.process_query(req)
print("RES1:", res)

req2 = QueryRequest(
    query="What is the riskometer classification?",
    conversation_id="123",
    history=history + [Message(role="user", content="Who is the current fund manager?")],
)
res2 = orc.process_query(req2)
print("RES2:", res2)

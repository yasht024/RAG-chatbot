import asyncio
from packages.contracts.schemas import QueryRequest, Message
from services.assistant_api.orchestrator import Orchestrator

async def main():
    orchestrator = Orchestrator()
    request = QueryRequest(
        query="Who is the current fund manager?",
        conversation_id="123",
        history=[
            Message(role="user", content="What is the minimum SIP for HDFC Mid Cap?")
        ]
    )
    result = orchestrator.process_query(request)
    print(result.status)
    print(result.refusal_reason)

if __name__ == "__main__":
    asyncio.run(main())

import sys
import os

sys.path.append(os.path.abspath("."))
from services.assistant_api.orchestrator import Orchestrator
from packages.contracts.schemas import QueryRequest

orchestrator = Orchestrator()
req = QueryRequest(query="What is the ELSS lock-in period")
resp = orchestrator.process_query(req)
print(resp.dict())

req2 = QueryRequest(query="What is the benchmark index of HDFC Mid Cap Fund?")
resp2 = orchestrator.process_query(req2)
print(resp2.dict())

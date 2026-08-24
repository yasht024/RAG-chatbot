from typing import List, Dict, Any
from packages.contracts.schemas import QueryRequest, FactualResponse
from services.assistant_api.orchestrator import Orchestrator

class ReplayEvaluator:
    """
    P3-EVAL-05: Replay comparison engine across models, prompts, policies,
    parsers, and index versions.
    """
    def __init__(self, baseline_orchestrator: Orchestrator, candidate_orchestrator: Orchestrator):
        self.baseline_orch = baseline_orchestrator
        self.candidate_orch = candidate_orchestrator

    def run_replay_comparison(self, test_dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
        total_queries = len(test_dataset)
        agreements = 0
        regressions = []
        improvements = []

        for item in test_dataset:
            query = item["query"]
            req = QueryRequest(query=query, conversation_id="replay-test")

            base_resp: FactualResponse = self.baseline_orch.process_query(req)
            cand_resp: FactualResponse = self.candidate_orch.process_query(req)

            # Compare statuses
            if base_resp.status == cand_resp.status:
                agreements += 1
            elif base_resp.status.value == "FACTUAL_ANSWER" and cand_resp.status.value != "FACTUAL_ANSWER":
                regressions.append({
                    "query": query,
                    "baseline_status": base_resp.status.value,
                    "candidate_status": cand_resp.status.value,
                    "reason": cand_resp.refusal_reason
                })
            elif base_resp.status.value != "FACTUAL_ANSWER" and cand_resp.status.value == "FACTUAL_ANSWER":
                improvements.append({
                    "query": query,
                    "baseline_status": base_resp.status.value,
                    "candidate_status": cand_resp.status.value
                })

        agreement_rate = (agreements / total_queries) if total_queries > 0 else 1.0

        return {
            "total_queries": total_queries,
            "agreements": agreements,
            "agreement_rate": round(agreement_rate, 4),
            "regressions_count": len(regressions),
            "improvements_count": len(improvements),
            "regressions": regressions,
            "improvements": improvements
        }

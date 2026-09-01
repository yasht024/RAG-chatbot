import json
import sys
from pathlib import Path
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[2]))

sys.stdout.reconfigure(encoding="utf-8")

from packages.contracts.schemas import QueryRequest
from services.assistant_api.orchestrator import Orchestrator


class EvaluationRunner:
    def __init__(self, dataset_path: Path = None):
        if dataset_path is None:
            dataset_path = Path(__file__).parents[2] / "data" / "fixtures" / "seed_eval.json"

        with open(dataset_path, "r", encoding="utf-8") as f:
            self.dataset = json.load(f)

        self.orchestrator = Orchestrator()

    def run_evaluation(self) -> Dict[str, Any]:
        cases = self.dataset.get("cases", [])
        total_cases = len(cases)

        terminal_status_correct = 0
        advisory_refusal = 0
        advisory_total = 0
        groww_violations = 0

        results = []

        for case in cases:
            case_id = case["case_id"]
            query = case["query"]
            expected_status = case.get("expected_terminal_status")

            req = QueryRequest(query=query, conversation_id="eval-conv-001")
            response = self.orchestrator.process_query(req)

            actual_status = response.status.value
            is_status_match = actual_status == expected_status

            if expected_status == "POLICY_REFUSAL":
                advisory_total += 1
                if is_status_match:
                    advisory_refusal += 1

            if is_status_match:
                terminal_status_correct += 1

            # Groww citation violation check
            if "groww.in" in (response.citation_url or "").lower():
                groww_violations += 1

            results.append(
                {
                    "case_id": case_id,
                    "query": query,
                    "expected_status": expected_status,
                    "actual_status": actual_status,
                    "passed": is_status_match,
                    "refusal_reason": response.refusal_reason,
                    "citation": response.citation_url,
                    "answers": response.answer_sentences,
                }
            )

        status_accuracy = terminal_status_correct / total_cases if total_cases > 0 else 0
        advisory_accuracy = advisory_refusal / advisory_total if advisory_total > 0 else 1.0

        return {
            "total_cases": total_cases,
            "status_accuracy": status_accuracy,
            "advisory_accuracy": advisory_accuracy,
            "groww_violations": groww_violations,
            "detailed_results": results,
        }


if __name__ == "__main__":
    runner = EvaluationRunner()
    report = runner.run_evaluation()
    print("--- End-to-End Evaluation Report ---")
    print(f"Total Cases: {report['total_cases']}")
    print(f"Terminal Status Accuracy: {report['status_accuracy'] * 100:.1f}%")
    print(f"Advisory Refusal Compliance: {report['advisory_accuracy'] * 100:.1f}%")
    print(f"Groww Citation Violations: {report['groww_violations']}")

    print("\n--- Failed Cases ---")
    for res in report["detailed_results"]:
        if not res["passed"]:
            print(f"[{res['case_id']}] FAILED. Expected {res['expected_status']}, Got {res['actual_status']}")
            print(f"  Q: {res['query']}")
            if res['refusal_reason']:
                print(f"  Reason: {res['refusal_reason']}")
            if res['answers']:
                print(f"  Ans: {res['answers']}")

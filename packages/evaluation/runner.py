import json
import sys
from pathlib import Path
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[2]))

from packages.policy.privacy_guard import PrivacyGuard
from packages.policy.classifier import QueryClassifier
from packages.policy.resolver import SchemeResolver


class EvaluationRunner:
    def __init__(self, dataset_path: Path = None):
        if dataset_path is None:
            dataset_path = Path(__file__).parents[2] / "data" / "fixtures" / "seed_eval.json"

        with open(dataset_path, "r", encoding="utf-8") as f:
            self.dataset = json.load(f)

        self.guard = PrivacyGuard()
        self.classifier = QueryClassifier()
        self.resolver = SchemeResolver()

    def run_evaluation(self) -> Dict[str, Any]:
        cases = self.dataset.get("cases", [])
        total_cases = len(cases)

        classification_correct = 0
        resolution_correct = 0
        privacy_correct = 0
        false_factual_on_advisory = 0

        results = []

        for case in cases:
            case_id = case["case_id"]
            query = case["query"]
            expected_class = case.get("expected_class")
            expected_scheme = case.get("expected_canonical_scheme")
            expected_status = case.get("expected_terminal_status")

            # 1. Privacy Guard
            privacy_res = self.guard.scan_query(query)

            # 2. Classifier
            class_res = self.classifier.classify_query(query)
            actual_class = class_res["query_class"]

            # 3. Resolver
            resolve_res = self.resolver.resolve_scheme(query)
            actual_scheme = resolve_res.get("scheme_id")

            # Metric: Zero false factual on advisory
            if expected_class in ["ADVISORY", "PERFORMANCE_COMPARISON"] and actual_class == "FACTUAL":
                false_factual_on_advisory += 1

            # Checks
            is_class_match = actual_class == expected_class
            is_scheme_match = (actual_scheme == expected_scheme) or (expected_scheme is None and actual_scheme is None)
            is_privacy_match = (privacy_res is not None) == (expected_status == "SENSITIVE_DATA_WARNING")

            if is_class_match:
                classification_correct += 1
            if is_scheme_match:
                resolution_correct += 1
            if is_privacy_match:
                privacy_correct += 1

            results.append(
                {
                    "case_id": case_id,
                    "query": query,
                    "expected_class": expected_class,
                    "actual_class": actual_class,
                    "expected_scheme": expected_scheme,
                    "actual_scheme": actual_scheme,
                    "classification_passed": is_class_match,
                    "resolution_passed": is_scheme_match,
                    "privacy_passed": is_privacy_match,
                }
            )

        class_accuracy = classification_correct / total_cases if total_cases > 0 else 0
        res_accuracy = resolution_correct / total_cases if total_cases > 0 else 0
        privacy_accuracy = privacy_correct / total_cases if total_cases > 0 else 0

        return {
            "total_cases": total_cases,
            "classification_accuracy": class_accuracy,
            "resolution_accuracy": res_accuracy,
            "privacy_accuracy": privacy_accuracy,
            "false_factual_on_advisory_count": false_factual_on_advisory,
            "detailed_results": results,
        }


if __name__ == "__main__":
    runner = EvaluationRunner()
    report = runner.run_evaluation()
    print("--- Evaluation Report ---")
    print(f"Total Cases: {report['total_cases']}")
    print(f"Classification Accuracy: {report['classification_accuracy']*100:.1f}%")
    print(f"Scheme Resolution Accuracy: {report['resolution_accuracy']*100:.1f}%")
    print(f"Privacy Accuracy: {report['privacy_accuracy']*100:.1f}%")
    print(f"False Factual on Advisory: {report['false_factual_on_advisory_count']}")

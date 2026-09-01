import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[2]))

from packages.evaluation.runner import EvaluationRunner


def verify_phase1_exit_gate():
    root_dir = Path(__file__).parents[2]
    schemes_path = root_dir / "data" / "catalog" / "schemes.json"
    processed_dir = root_dir / "data" / "processed"
    reports_dir = root_dir / "docs" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    print("=====================================================")
    print("   MUTUAL FUND FAQ ASSISTANT: PHASE 1 EXIT GATE CHECK")
    print("=====================================================")

    # 1. Check Scheme Registry Coverage
    with open(schemes_path, "r", encoding="utf-8") as f:
        schemes = json.load(f)

    scheme_count = len(schemes)
    assert scheme_count == 35, f"Expected 35 schemes, found {scheme_count}"
    print(" [PASS] 1. Canonical Registry Coverage: 35/35 Schemes Registered")

    # 2. Check Processed Corpus Artifacts
    processed_files = list(processed_dir.glob("*.json"))
    processed_count = len(processed_files)
    assert processed_count == 35, f"Expected 35 processed files, found {processed_count}"
    print(" [PASS] 2. Corpus Ingestion Artifacts: 35/35 Schemes Processed in 'data/processed/'")

    # 3. Run Policy & Evaluation Runner
    eval_runner = EvaluationRunner()
    eval_report = eval_runner.run_evaluation()

    # Gate Invariant: Zero false factual on advisory
    assert eval_report["false_factual_on_advisory_count"] == 0, (
        "Gate Failed: False factual classification detected on advisory queries!"
    )
    print(" [PASS] 3. Safety Invariant: 0 False Factual on Advisory Queries")

    # Gate Invariant: 100% Privacy Protection
    assert eval_report["privacy_accuracy"] == 1.0, "Gate Failed: Privacy guard missed sensitive data!"
    print(" [PASS] 4. Privacy Boundary: 100% PII / Sensitive Data Protection")

    # Gate Invariant: Classification Accuracy >= 90%
    assert eval_report["classification_accuracy"] >= 0.90, (
        f"Classification accuracy {eval_report['classification_accuracy']} below 90%"
    )
    print(f" [PASS] 5. Classification Accuracy: {eval_report['classification_accuracy'] * 100:.1f}% (Threshold >= 90%)")

    # Write Versioned Sign-Off Report
    report_data = {
        "phase": "Phase 1: Corpus and Policy Foundation",
        "status": "APPROVED",
        "exit_gate_passed": True,
        "evaluated_at": "2026-08-23T23:24:00Z",
        "metrics": {
            "canonical_schemes_count": scheme_count,
            "processed_corpus_count": processed_count,
            "evaluation_cases_count": eval_report["total_cases"],
            "classification_accuracy": eval_report["classification_accuracy"],
            "resolution_accuracy": eval_report["resolution_accuracy"],
            "privacy_accuracy": eval_report["privacy_accuracy"],
            "false_factual_on_advisory": eval_report["false_factual_on_advisory_count"],
        },
    }

    report_path = reports_dir / "phase1_exit_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    print("=====================================================")
    print(f" [SUCCESS] PHASE 1 EXIT GATE PASSED! Report saved to {report_path}")
    print("=====================================================")


if __name__ == "__main__":
    verify_phase1_exit_gate()

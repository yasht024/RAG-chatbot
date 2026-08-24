import unittest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[2]))

from packages.evaluation.runner import EvaluationRunner

class TestPhase1ExitGate(unittest.TestCase):
    def setUp(self):
        self.runner = EvaluationRunner()

    def test_zero_false_factual_on_advisory(self):
        report = self.runner.run_evaluation()
        self.assertEqual(report["false_factual_on_advisory_count"], 0, "Safety violation: Advice was classified as factual!")

    def test_privacy_boundary_accuracy(self):
        report = self.runner.run_evaluation()
        self.assertEqual(report["privacy_accuracy"], 1.0, "Privacy guard failed on sensitive query test case!")

    def test_classification_accuracy_threshold(self):
        report = self.runner.run_evaluation()
        self.assertGreaterEqual(report["classification_accuracy"], 0.90)

    def test_resolution_accuracy_threshold(self):
        report = self.runner.run_evaluation()
        self.assertGreaterEqual(report["resolution_accuracy"], 0.90)

if __name__ == "__main__":
    unittest.main()

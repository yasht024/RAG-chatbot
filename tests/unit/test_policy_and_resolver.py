import unittest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[2]))

from packages.policy.privacy_guard import PrivacyGuard
from packages.policy.classifier import QueryClassifier
from packages.policy.refusal_renderer import RefusalRenderer
from packages.policy.resolver import SchemeResolver


class TestPolicyAndResolver(unittest.TestCase):
    def setUp(self):
        self.guard = PrivacyGuard()
        self.classifier = QueryClassifier()
        self.renderer = RefusalRenderer()
        self.resolver = SchemeResolver()

    # 1. Privacy Guard Tests
    def test_privacy_guard_pan_detection(self):
        res = self.guard.scan_query("My PAN is ABCDE1234F. What is the exit load?")
        self.assertIsNotNone(res)
        self.assertIn("PAN_NUMBER", res["categories"])
        self.assertEqual(res["terminal_status"], "SENSITIVE_DATA_WARNING")

    def test_privacy_guard_clean_query(self):
        res = self.guard.scan_query("What is the expense ratio of HDFC Mid Cap Fund?")
        self.assertIsNone(res)

    # 2. Query Classifier Tests
    def test_classifier_advisory_refusal(self):
        res = self.classifier.classify_query("Should I invest in HDFC Mid Cap Fund?")
        self.assertEqual(res["query_class"], "ADVISORY")
        self.assertTrue(res["contains_advice"])

    def test_classifier_performance_comparison(self):
        res = self.classifier.classify_query("Which HDFC fund gives the highest return?")
        self.assertEqual(res["query_class"], "PERFORMANCE_COMPARISON")
        self.assertTrue(res["contains_comparison"])

    def test_classifier_factual_expense_ratio(self):
        res = self.classifier.classify_query("What is the expense ratio of HDFC Flexi Cap?")
        self.assertEqual(res["query_class"], "FACTUAL")
        self.assertEqual(res["fact_type"], "EXPENSE_RATIO")

    # 3. Refusal Renderer Tests
    def test_refusal_renderer_advisory(self):
        res = self.renderer.render_refusal("ADVISORY")
        self.assertEqual(res["status"], "POLICY_REFUSAL")
        self.assertIn("https://www.amfiindia.com/investor-corner", res["answer_sentences"][1])

    # 4. Scheme Resolver Tests
    def test_resolver_canonical_match(self):
        res = self.resolver.resolve_scheme("What is the minimum SIP for HDFC Mid Cap Fund - Direct Growth?")
        self.assertEqual(res["status"], "RESOLVED")
        self.assertEqual(res["scheme_id"], "hdfc_mid_cap")
        self.assertEqual(res["plan"], "Direct")
        self.assertEqual(res["option"], "Growth")

    def test_resolver_curated_alias(self):
        res = self.resolver.resolve_scheme("Tell me about HDFC BAF exit load")
        self.assertEqual(res["status"], "RESOLVED")
        self.assertEqual(res["scheme_id"], "hdfc_balanced_advantage")

    def test_resolver_regular_idcw_plan(self):
        res = self.resolver.resolve_scheme("What is the expense ratio of HDFC Mid Cap Regular IDCW?")
        self.assertEqual(res["status"], "RESOLVED")
        self.assertEqual(res["plan"], "Regular")
        self.assertEqual(res["option"], "IDCW")
        self.assertEqual(res["canonical_name"], "HDFC Mid Cap Fund - Regular IDCW")

    def test_resolver_unsupported_exotic_plan(self):
        res = self.resolver.resolve_scheme("What is the expense ratio of HDFC Mid Cap bonus plan?")
        self.assertEqual(res["status"], "UNSUPPORTED_PLAN")

    def test_resolver_sbi_scheme_alias(self):
        res = self.resolver.resolve_scheme("What is the expense ratio for SBI Small Cap?")
        self.assertEqual(res["status"], "RESOLVED")
        self.assertEqual(res["scheme_id"], "sbi_small_cap")

    def test_resolver_cross_amc_disambiguation(self):
        # Even if they just say "small cap", it should become ambiguous or resolve properly
        res = self.resolver.resolve_scheme("What is the exit load for small cap fund?")
        self.assertEqual(res["status"], "AMBIGUOUS_SCHEME")

        # Explicit AMC should resolve properly
        res_sbi = self.resolver.resolve_scheme("What is the exit load for SBI small cap fund?")
        self.assertEqual(res_sbi["status"], "RESOLVED")
        self.assertEqual(res_sbi["scheme_id"], "sbi_small_cap")

        res_hdfc = self.resolver.resolve_scheme("What is the exit load for HDFC small cap fund?")
        self.assertEqual(res_hdfc["status"], "RESOLVED")
        self.assertEqual(res_hdfc["scheme_id"], "hdfc_small_cap")


if __name__ == "__main__":
    unittest.main()

import unittest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[2]))

from packages.policy.classifier import QueryClassifier
from packages.policy.refusal_renderer import RefusalRenderer


class TestMultilingualExpansion(unittest.TestCase):
    """
    Validates Track C - Hindi language support across the classifier and refusal renderer.
    """

    def setUp(self):
        self.classifier = QueryClassifier()
        self.renderer = RefusalRenderer()

    def test_hindi_advisory_classification(self):
        # "क्या मुझे निवेश करना चाहिए" -> "should I invest"
        res = self.classifier.classify_query("क्या मुझे HDFC Mid Cap में निवेश करना चाहिए?")
        self.assertEqual(res["query_class"], "ADVISORY")
        self.assertTrue(res["contains_advice"])

    def test_hindi_comparison_classification(self):
        # "सबसे अच्छा फंड" -> "best fund"
        res = self.classifier.classify_query("SBI और HDFC में सबसे अच्छा फंड कौन सा है?")
        self.assertEqual(res["query_class"], "PERFORMANCE_COMPARISON")
        self.assertTrue(res["contains_comparison"])

    def test_hindi_factual_extraction(self):
        # "एग्जिट लोड" -> "exit load"
        res = self.classifier.classify_query("HDFC Small Cap का एग्जिट लोड क्या है?")
        self.assertEqual(res["query_class"], "FACTUAL")
        self.assertEqual(res["fact_type"], "EXIT_LOAD")

        # "एक्सपेंस रेशियो" -> "expense ratio"
        res_exp = self.classifier.classify_query("इस फंड का एक्सपेंस रेशियो कितना है?")
        self.assertEqual(res_exp["query_class"], "FACTUAL")
        self.assertEqual(res_exp["fact_type"], "EXPENSE_RATIO")

    def test_hindi_refusal_rendering(self):
        query = "क्या मुझे निवेश करना चाहिए?"
        res = self.renderer.render_refusal("ADVISORY", query=query)

        self.assertEqual(res["status"], "POLICY_REFUSAL")
        # Check that the Hindi response is returned
        self.assertIn("मैं निवेश सलाह या सिफारिशें नहीं दे सकता", res["answer_sentences"][0])
        self.assertIn("AMFI पोर्टल", res["answer_sentences"][1])

    def test_hindi_unsupported_plan_rendering(self):
        query = "रेगुलर प्लान"
        res = self.renderer.render_refusal("FACTUAL", reason_code="UNSUPPORTED_PLAN", query=query)
        self.assertIn("डायरेक्ट, रेगुलर, ग्रोथ और IDCW", res["answer_sentences"][0])


if __name__ == "__main__":
    unittest.main()

import unittest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[2]))

from services.policy_service.main import app

class TestPolicyServiceAPI(unittest.TestCase):
    """
    Integration tests for the standalone FastAPI policy microservice.
    Verifies that HTTP serialization and endpoint mapping preserve existing logic.
    """
    def setUp(self):
        self.client = TestClient(app)

    def test_scan_query_clean(self):
        response = self.client.post("/v1/policy/scan", json={"query": "What is the exit load of HDFC Mid Cap?"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "CLEAN")

    def test_scan_query_sensitive(self):
        response = self.client.post("/v1/policy/scan", json={"query": "My PAN is ABCDE1234F. What is the exit load?"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["terminal_status"], "SENSITIVE_DATA_WARNING")

    def test_classify_query_hindi_advisory(self):
        response = self.client.post("/v1/policy/classify", json={"query": "क्या मुझे HDFC Mid Cap में निवेश करना चाहिए?"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["query_class"], "ADVISORY")
        self.assertTrue(data["contains_advice"])

    def test_resolve_scheme_amc_disambiguation(self):
        response = self.client.post("/v1/policy/resolve", json={"query": "What is the exit load for small cap fund?"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "AMBIGUOUS_SCHEME")
        self.assertIn("hdfc_small_cap", data["candidate_schemes"])
        self.assertIn("sbi_small_cap", data["candidate_schemes"])

    def test_render_refusal_hindi(self):
        response = self.client.post("/v1/policy/refusal", json={
            "query_class": "ADVISORY",
            "query": "क्या मुझे निवेश करना चाहिए?"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "POLICY_REFUSAL")
        self.assertIn("मैं निवेश सलाह या सिफारिशें नहीं दे सकता", data["answer_sentences"][0])

if __name__ == "__main__":
    unittest.main()

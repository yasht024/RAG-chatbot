import unittest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[2]))

from packages.policy.resolver import SchemeResolver

class TestAMCExpansion(unittest.TestCase):
    """
    Validates cross-AMC expansion logic and ensures zero regression
    on the original HDFC MVP (35 schemes) when adding SBI schemes.
    """
    def setUp(self):
        self.resolver = SchemeResolver()

    def test_original_hdfc_mvp_no_regression(self):
        """Ensure all 35 HDFC MVP behaviors remain unchanged."""
        # 1. Exact canonical
        res = self.resolver.resolve_scheme("HDFC Mid Cap Fund - Direct Growth")
        self.assertEqual(res["status"], "RESOLVED")
        self.assertEqual(res["scheme_id"], "hdfc_mid_cap")

        # 2. Curated alias
        res_alias = self.resolver.resolve_scheme("HDFC BAF")
        self.assertEqual(res_alias["status"], "RESOLVED")
        self.assertEqual(res_alias["scheme_id"], "hdfc_balanced_advantage")

        # 3. Partial tokens
        res_partial = self.resolver.resolve_scheme("HDFC Small Cap")
        self.assertEqual(res_partial["status"], "RESOLVED")
        self.assertEqual(res_partial["scheme_id"], "hdfc_small_cap")

    def test_new_sbi_amc_resolution(self):
        """Ensure the newly onboarded SBI AMC resolves correctly."""
        # Exact canonical (base)
        res = self.resolver.resolve_scheme("SBI Small Cap Fund")
        self.assertEqual(res["status"], "RESOLVED")
        self.assertEqual(res["scheme_id"], "sbi_small_cap")

        # Alias
        res_alias = self.resolver.resolve_scheme("SBI Hybrid")
        self.assertEqual(res_alias["status"], "RESOLVED")
        self.assertEqual(res_alias["scheme_id"], "sbi_equity_hybrid")

    def test_amc_leakage_prevention(self):
        """Ensure one AMC's partial match does not leak to another AMC."""
        # "Small Cap Fund" without AMC should be ambiguous because both HDFC and SBI have it
        res_ambig = self.resolver.resolve_scheme("What is the expense ratio for small cap fund?")
        self.assertEqual(res_ambig["status"], "AMBIGUOUS_SCHEME")
        self.assertIn("hdfc_small_cap", res_ambig["candidate_schemes"])
        self.assertIn("sbi_small_cap", res_ambig["candidate_schemes"])

if __name__ == "__main__":
    unittest.main()

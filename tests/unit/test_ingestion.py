import unittest
from pathlib import Path
from workers.ingestion.fetcher import Fetcher, AllowlistViolationError
from workers.ingestion.parser import SchemeParser
from workers.ingestion.chunker import Chunker
from workers.ingestion.pipeline import IngestionPipeline

SAMPLE_GROWW_HTML = """
<!DOCTYPE html>
<html>
<head><title>HDFC Mid Cap Fund - Direct Growth</title></head>
<body>
  <h1>HDFC Mid Cap Fund Details</h1>
  <div class="facts">
    <p>Expense Ratio: 0.85%</p>
    <p>Exit Load: 1% if redeemed within 1 year</p>
    <p>Min SIP amount: ₹ 100</p>
    <p>Benchmark Index: NIFTY Midcap 150 TRI</p>
    <p>Riskometer: Very High</p>
    <p>Fund Manager: Chirag Setalvad</p>
  </div>
</body>
</html>
"""


class TestIngestion(unittest.TestCase):
    def test_fetcher_allowlist_enforcement(self):
        fetcher = Fetcher()

        # Valid allowlisted domain
        self.assertTrue(
            fetcher.validate_url("https://www.hdfcfund.com/our-funds/equity-funds/hdfc-mid-cap-opportunities-fund")
        )

        # Invalid domain should raise AllowlistViolationError
        with self.assertRaises(AllowlistViolationError):
            fetcher.validate_url("https://unapproved-aggregator.com/scheme")

    def test_fetcher_snapshot_and_hashing(self):
        fetcher = Fetcher()
        url = "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth"

        meta = fetcher.fetch_and_snapshot(url=url, raw_html_content=SAMPLE_GROWW_HTML)

        self.assertEqual(meta["canonical_url"], url)
        self.assertEqual(meta["source_domain"], "groww.in")
        self.assertTrue(meta["content_hash"].startswith("sha256:"))
        self.assertTrue(Path(meta["snapshot_path"]).exists())

    def test_parser_fact_extraction(self):
        parser = SchemeParser()
        doc = parser.parse_scheme_page(
            raw_html=SAMPLE_GROWW_HTML,
            scheme_id="hdfc_mid_cap",
            canonical_url="https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
        )

        self.assertEqual(doc["scheme_id"], "hdfc_mid_cap")
        facts = {f["fact_type"]: f["value_display"] for f in doc["extracted_facts"]}

        self.assertIn("0.85%", facts["EXPENSE_RATIO"])
        self.assertIn("1%", facts["EXIT_LOAD"])
        self.assertIn("100", facts["MINIMUM_SIP"])
        self.assertIn("NIFTY Midcap 150 TRI", facts["BENCHMARK"])
        self.assertIn("Very High", facts["RISKOMETER"])
        self.assertIn("Chirag Setalvad", facts["FUND_MANAGER"])

    def test_chunker_structure_and_tagging(self):
        parser = SchemeParser()
        chunker = Chunker()

        parsed = parser.parse_scheme_page(
            raw_html=SAMPLE_GROWW_HTML,
            scheme_id="hdfc_mid_cap",
            canonical_url="https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
        )

        passages = chunker.chunk_document(parsed)
        self.assertGreaterThan(len(passages), 0) if hasattr(self, "assertGreaterThan") else self.assertTrue(
            len(passages) > 0
        )
        self.assertEqual(passages[0]["scheme_ids"], ["hdfc_mid_cap"])
        self.assertIn("EXPENSE_RATIO", passages[0]["fact_types"])

    def test_pipeline_end_to_end(self):
        pipeline = IngestionPipeline()

        res = pipeline.process_scheme_url(
            db=None,  # Test without active DB connection
            scheme_id="hdfc_mid_cap",
            url="https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
            raw_html=SAMPLE_GROWW_HTML,
        )

        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["scheme_id"], "hdfc_mid_cap")
        self.assertTrue(res["passages_count"] > 0)
        self.assertEqual(res["facts_count"], 6)


if __name__ == "__main__":
    unittest.main()

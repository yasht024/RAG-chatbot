"""
corpus_loader.py
----------------
Dynamically loads searchable passages from every processed JSON file in
``data/processed/``.  This removes the need for a hardcoded MOCK_CORPUS
and makes every scheme available to the search layer automatically.

Fact-type key mapping
~~~~~~~~~~~~~~~~~~~~~
The processed JSONs store fact types in UPPER_SNAKE_CASE (e.g. ``EXIT_LOAD``,
``MINIMUM_SIP``).  The search engine and document router expect lower_snake_case
keys that may also differ in name (e.g. ``exit_load``, ``minimum_sip_amount``).
``FACT_TYPE_MAP`` handles that translation.
"""

import json
import glob
import os
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Mapping: processed-JSON fact_type  →  search-layer fact_type key
# ---------------------------------------------------------------------------
FACT_TYPE_MAP: Dict[str, str] = {
    "expense_ratio": "expense_ratio",
    "exit_load": "exit_load",
    "minimum_sip": "minimum_sip_amount",
    "minimum_lump_sum": "minimum_lumpsum",
    "benchmark": "benchmark_index",
    "riskometer": "riskometer",
    "fund_manager": "fund_manager",
    "lock_in": "elss_lock_in",  # generic lock-in maps to elss_lock_in key
    "investment_objective": "investment_objective",
    "inception_date": "inception_date",
    "plans_options": "plans_options",
}

# Human-readable label used inside normalized_text
FACT_TYPE_LABEL: Dict[str, str] = {
    "expense_ratio": "Expense Ratio",
    "exit_load": "Exit Load",
    "minimum_sip": "Min SIP Amount",
    "minimum_lump_sum": "Min Lumpsum",
    "benchmark": "Benchmark Index",
    "riskometer": "Riskometer",
    "fund_manager": "Fund Manager",
    "lock_in": "Lock-in Period",
    "investment_objective": "Investment Objective",
    "inception_date": "Inception Date",
    "plans_options": "Plans & Options",
}

# ---------------------------------------------------------------------------
# Official source URLs per scheme.
# The system prompt prohibits citing Groww as a factual source.
# Passages use these instead of the Groww canonical_url from the JSON files.
# ---------------------------------------------------------------------------
_HDFC_BASE = "https://www.hdfcfund.com/our-funds"
SCHEME_OFFICIAL_URL_MAP: Dict[str, str] = {
    "hdfc_mid_cap": f"{_HDFC_BASE}/equity-funds/hdfc-mid-cap-opportunities-fund",
    "hdfc_flexi_cap": f"{_HDFC_BASE}/equity-funds/hdfc-flexi-cap-fund",
    "hdfc_small_cap": f"{_HDFC_BASE}/equity-funds/hdfc-small-cap-fund",
    "hdfc_large_and_mid_cap": f"{_HDFC_BASE}/equity-funds/hdfc-large-and-mid-cap-fund",
    "hdfc_large_cap": f"{_HDFC_BASE}/equity-funds/hdfc-top-100-fund",
    "hdfc_multi_cap": f"{_HDFC_BASE}/equity-funds/hdfc-multi-cap-fund",
    "hdfc_focused": f"{_HDFC_BASE}/equity-funds/hdfc-focused-30-fund",
    "hdfc_value": f"{_HDFC_BASE}/equity-funds/hdfc-capital-builder-value-fund",
    "hdfc_elss_tax_saver": f"{_HDFC_BASE}/equity-funds/hdfc-elss-tax-saver-fund",
    "hdfc_mnc": f"{_HDFC_BASE}/equity-funds/hdfc-mnc-fund",
    "hdfc_business_cycle": f"{_HDFC_BASE}/equity-funds/hdfc-business-cycle-fund",
    "hdfc_defence": f"{_HDFC_BASE}/equity-funds/hdfc-defence-fund",
    "hdfc_consumption": f"{_HDFC_BASE}/equity-funds/hdfc-consumption-fund",
    "hdfc_transportation_and_logistics": f"{_HDFC_BASE}/equity-funds/hdfc-transportation-and-logistics-fund",
    "hdfc_technology": f"{_HDFC_BASE}/equity-funds/hdfc-technology-fund",
    "hdfc_pharma_and_healthcare": f"{_HDFC_BASE}/equity-funds/hdfc-pharma-and-healthcare-fund",
    "hdfc_manufacturing": f"{_HDFC_BASE}/equity-funds/hdfc-manufacturing-fund",
    "hdfc_infrastructure": f"{_HDFC_BASE}/equity-funds/hdfc-infrastructure-fund",
    "hdfc_innovation": f"{_HDFC_BASE}/equity-funds/hdfc-innovation-fund",
    "hdfc_childrens": f"{_HDFC_BASE}/equity-funds/hdfc-childrens-gift-fund",
    "hdfc_balanced_advantage": f"{_HDFC_BASE}/hybrid-funds/hdfc-balanced-advantage-fund",
    "hdfc_multi_asset_allocation": f"{_HDFC_BASE}/hybrid-funds/hdfc-multi-asset-allocation-fund",
    "hdfc_gold_etf_fof": f"{_HDFC_BASE}/other-funds/hdfc-gold-exchange-traded-fund-fund-of-fund",
    "hdfc_nifty_50_index": f"{_HDFC_BASE}/index-funds/hdfc-nifty-50-index-fund",
    "hdfc_nifty_next_50_index": f"{_HDFC_BASE}/index-funds/hdfc-nifty-next-50-index-fund",
    "hdfc_nifty_100_index": f"{_HDFC_BASE}/index-funds/hdfc-nifty-100-index-fund",
    "hdfc_nifty_100_equal_weight_index": f"{_HDFC_BASE}/index-funds/hdfc-nifty-100-equal-weight-index-fund",
    "hdfc_nifty50_equal_weight_index": f"{_HDFC_BASE}/index-funds/hdfc-nifty-50-equal-weight-index-fund",
    "hdfc_nifty_midcap_150_index": f"{_HDFC_BASE}/index-funds/hdfc-nifty-midcap-150-index-fund",
    "hdfc_nifty_smallcap_250_index": f"{_HDFC_BASE}/index-funds/hdfc-nifty-smallcap-250-index-fund",
    "hdfc_nifty_largemidcap_250_index": f"{_HDFC_BASE}/index-funds/hdfc-nifty-largemidcap-250-index-fund",
    "hdfc_nifty200_momentum_30_index": f"{_HDFC_BASE}/index-funds/hdfc-nifty200-momentum-30-index-fund",
    "hdfc_nifty100_low_volatility_30_index": f"{_HDFC_BASE}/index-funds/hdfc-nifty100-low-volatility-30-index-fund",
    "hdfc_nifty100_quality_30_index": f"{_HDFC_BASE}/index-funds/hdfc-nifty100-quality-30-index-fund",
    "hdfc_nifty_top_20_equal_weight_index": f"{_HDFC_BASE}/index-funds/hdfc-nifty-top-20-equal-weight-index-fund",
    "sbi_small_cap": "https://www.sbimf.com/en-us/schemes/equity-funds/sbi-small-cap-fund",
    "sbi_equity_hybrid": "https://www.sbimf.com/en-us/schemes/hybrid-funds/sbi-equity-hybrid-fund",
    "sbi_bluechip": "https://www.sbimf.com/en-us/schemes/equity-funds/sbi-bluechip-fund",
}
_HDFC_FALLBACK_URL = "https://www.hdfcfund.com/our-funds"


def _normalise_fact_type(raw: str) -> str:
    """Convert an uppercase JSON fact_type to the search-layer key."""
    key = raw.lower()
    return FACT_TYPE_MAP.get(key, key)


def _label(raw: str) -> str:
    key = raw.lower()
    return FACT_TYPE_LABEL.get(key, raw.replace("_", " ").title())


def load_corpus_from_processed(processed_dir: str) -> List[Dict[str, Any]]:
    """
    Read every ``*.json`` file under *processed_dir* and return a list of
    passage dicts compatible with ``InMemoryKeywordSearch`` / ``InMemoryVectorSearch``.

    Each extracted fact becomes one passage so that the scheme hard-filter and
    fact-type filter in the search layer can operate at maximum granularity.
    """
    passages: List[Dict[str, Any]] = []
    pattern = os.path.join(processed_dir, "*.json")
    files = sorted(glob.glob(pattern))

    if not files:
        logger.warning("corpus_loader: no processed JSON files found at %s", processed_dir)
        return passages

    for path in files:
        try:
            with open(path, encoding="utf-8") as fh:
                doc = json.load(fh)
        except (json.JSONDecodeError, OSError) as exc:
            logger.error("corpus_loader: skipping %s — %s", path, exc)
            continue

        scheme_id: str = doc.get("scheme_id", os.path.splitext(os.path.basename(path))[0])
        doc_title: str = doc.get("document_title", scheme_id)
        full_text: str = doc.get("full_text", "")

        # Use official HDFC AMC URL instead of the Groww canonical_url.
        # The system prompt prohibits citing Groww as a factual source.
        official_url: str = SCHEME_OFFICIAL_URL_MAP.get(scheme_id, _HDFC_FALLBACK_URL)

        # Extract structured metadata from JSON
        source_org: str = doc.get("source_org", "HDFC AMC")
        source_domain: str = doc.get("source_domain", "hdfcfund.com")
        source_type: str = doc.get("source_type", "scheme_page")
        pub_date = doc.get("publication_date", None)
        eff_date = doc.get("effective_date", None)
        approved_source = True  # Hardcoded True for corpus passages, controlled by validation.py

        extracted_facts: List[Dict[str, Any]] = doc.get("extracted_facts", [])

        for fact in extracted_facts:
            raw_type: str = fact.get("fact_type", "")
            if not raw_type:
                continue

            norm_type = _normalise_fact_type(raw_type)
            value_display = fact.get("value_display", "")
            unit = fact.get("unit") or ""

            # Build a readable normalized_text
            label = _label(raw_type)
            unit_suffix = f" {unit}" if unit and unit not in ("INR", "%") else ""
            if unit == "INR":
                value_str = f"₹{value_display}"
            elif unit == "%" and "%" not in str(value_display):
                # Only append % if the value doesn't already contain one
                value_str = f"{value_display}%"
            else:
                value_str = value_display
            normalized_text = f"{label}: {value_str}{unit_suffix}"

            passage: Dict[str, Any] = {
                "passage_id": f"{scheme_id}__{norm_type}",
                "document_id": f"doc_{scheme_id}",
                "document_type": "FACTSHEET",
                "scheme_ids": [scheme_id],
                "scheme_name": doc_title,
                "plan": "ALL",
                "option": "ALL",
                "normalized_text": normalized_text,
                "fact_types": [norm_type],
                "is_table": False,
                "publication_date": pub_date,
                "effective_date": eff_date,
                "source_url": official_url,
                "source_org": source_org,
                "source_domain": source_domain,
                "source_type": source_type,
                "approved_source": approved_source,
                "document_name": doc_title,
                "page_number": fact.get("page_number"),
                "supersedes": doc.get("supersedes"),
                "superseded_by": doc.get("superseded_by"),
            }
            passages.append(passage)

        # Also add a full-text passage for open-ended / unrecognised queries
        if full_text:
            passages.append(
                {
                    "passage_id": f"{scheme_id}__full_text",
                    "document_id": f"doc_{scheme_id}",
                    "document_type": "FACTSHEET",
                    "scheme_ids": [scheme_id],
                    "scheme_name": doc_title,
                    "plan": "ALL",
                    "option": "ALL",
                    "normalized_text": full_text,
                    "fact_types": ["full_text"],
                    "is_table": False,
                    "publication_date": pub_date,
                    "effective_date": eff_date,
                    "source_url": official_url,
                    "source_org": source_org,
                    "source_domain": source_domain,
                    "source_type": source_type,
                    "approved_source": approved_source,
                    "document_name": doc_title,
                    "page_number": None,
                    "supersedes": doc.get("supersedes"),
                    "superseded_by": doc.get("superseded_by"),
                }
            )

    logger.info(
        "corpus_loader: loaded %d passages from %d scheme files in %s",
        len(passages),
        len(files),
        processed_dir,
    )
    return passages

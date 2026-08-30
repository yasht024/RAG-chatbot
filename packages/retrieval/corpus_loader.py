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
import datetime
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

TODAY_STR = datetime.date.today().strftime("%Y-%m-%d")

# ---------------------------------------------------------------------------
# Mapping: processed-JSON fact_type  →  search-layer fact_type key
# ---------------------------------------------------------------------------
FACT_TYPE_MAP: Dict[str, str] = {
    "expense_ratio":    "expense_ratio",
    "exit_load":        "exit_load",
    "minimum_sip":      "minimum_sip_amount",
    "minimum_lump_sum": "minimum_lumpsum",
    "benchmark":        "benchmark_index",
    "riskometer":       "riskometer",
    "fund_manager":     "fund_manager",
    "lock_in":          "elss_lock_in",      # generic lock-in maps to elss_lock_in key
    "investment_objective": "investment_objective",
    "inception_date":   "inception_date",
    "plans_options":    "plans_options",
}

# Human-readable label used inside normalized_text
FACT_TYPE_LABEL: Dict[str, str] = {
    "expense_ratio":       "Expense Ratio",
    "exit_load":           "Exit Load",
    "minimum_sip":         "Min SIP Amount",
    "minimum_lump_sum":    "Min Lumpsum",
    "benchmark":           "Benchmark Index",
    "riskometer":          "Riskometer",
    "fund_manager":        "Fund Manager",
    "lock_in":             "Lock-in Period",
    "investment_objective":"Investment Objective",
    "inception_date":      "Inception Date",
    "plans_options":       "Plans & Options",
}


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
        canonical_url: str = doc.get("canonical_url", "")
        doc_title: str = doc.get("document_title", scheme_id)
        full_text: str = doc.get("full_text", "")

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
                "passage_id":      f"{scheme_id}__{norm_type}",
                "document_id":     f"doc_{scheme_id}",
                "document_type":   "FACTSHEET",
                "scheme_ids":      [scheme_id],
                "plan":            "ALL",
                "option":          "ALL",
                "normalized_text": normalized_text,
                "fact_types":      [norm_type],
                "is_table":        False,
                "publication_date": TODAY_STR,
                "source_url":      canonical_url,
            }
            passages.append(passage)

        # Also add a full-text passage for open-ended / unrecognised queries
        if full_text:
            passages.append({
                "passage_id":      f"{scheme_id}__full_text",
                "document_id":     f"doc_{scheme_id}",
                "document_type":   "FACTSHEET",
                "scheme_ids":      [scheme_id],
                "plan":            "ALL",
                "option":          "ALL",
                "normalized_text": full_text,
                "fact_types":      ["full_text"],
                "is_table":        False,
                "publication_date": TODAY_STR,
                "source_url":      canonical_url,
            })

    logger.info(
        "corpus_loader: loaded %d passages from %d scheme files in %s",
        len(passages), len(files), processed_dir,
    )
    return passages

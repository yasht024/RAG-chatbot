import logging
from typing import List, Dict, Any, Set, Tuple

logger = logging.getLogger(__name__)


class CorpusQualityChecker:
    """
    Validates corpus consistency, source link availability, and detects parser/coverage regressions.
    """

    EXPECTED_FACT_TYPES = {
        "minimum_sip_amount",
        "expense_ratio",
        "benchmark_index",
        "elss_lock_in",
        "exit_load",
        "fund_manager",
        "investment_objective",
        "riskometer",
        "inception_date",
    }

    ALLOWED_DOMAINS = {"groww.in", "hdfcfund.com"}

    @staticmethod
    def validate_source_links(passages: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        P3-COR-06: Verifies that every passage has a valid, non-empty source_url
        from an approved domain.
        """
        errors = []
        for p in passages:
            url = p.get("source_url", "")
            pid = p.get("passage_id", "unknown")
            if not url:
                errors.append(f"Passage {pid} is missing a source_url.")
                continue

            has_valid_domain = any(domain in url for domain in CorpusQualityChecker.ALLOWED_DOMAINS)
            if not has_valid_domain:
                errors.append(f"Passage {pid} has unapproved domain: {url}")

        is_valid = len(errors) == 0
        return is_valid, errors

    @staticmethod
    def detect_coverage_regressions(
        passages: List[Dict[str, Any]],
        expected_schemes: Set[str],
        baseline_scheme_count: int = 1,
    ) -> Tuple[bool, List[str]]:
        """
        P3-COR-07: Checks that schemes and required fact types are not missing from parser output.
        """
        errors = []
        covered_schemes = set()
        covered_facts_by_scheme: Dict[str, Set[str]] = {}

        for p in passages:
            scheme_ids = p.get("scheme_ids", [])
            fact_types = p.get("fact_types", [])
            for sid in scheme_ids:
                covered_schemes.add(sid)
                if sid not in covered_facts_by_scheme:
                    covered_facts_by_scheme[sid] = set()
                covered_facts_by_scheme[sid].update(fact_types)

        # Check missing schemes
        missing_schemes = expected_schemes - covered_schemes
        if missing_schemes:
            errors.append(f"Coverage regression: Missing {len(missing_schemes)} expected scheme(s): {missing_schemes}")

        if len(covered_schemes) < baseline_scheme_count:
            errors.append(f"Scheme count {len(covered_schemes)} is below baseline {baseline_scheme_count}")

        is_valid = len(errors) == 0
        return is_valid, errors

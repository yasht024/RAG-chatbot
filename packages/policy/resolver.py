import json
import re
from pathlib import Path
from typing import Dict, Any, Optional


class SchemeResolver:
    """
    Resolves scheme names, aliases, and intent attributes:
    1. Canonical exact match.
    2. Curated alias match.
    3. Constrained fuzzy / partial match.
    4. Ambiguity detection (AMBIGUOUS_SCHEME).
    5. Direct Growth defaults and unsupported plan refusal.
    """

    def __init__(self, schemes_path: Path = None, aliases_path: Path = None):
        if schemes_path is None:
            schemes_path = Path(__file__).parents[2] / "data" / "catalog" / "schemes.json"
        if aliases_path is None:
            aliases_path = Path(__file__).parents[2] / "data" / "catalog" / "aliases.json"

        with open(schemes_path, "r", encoding="utf-8") as f:
            self.schemes = json.load(f)

        with open(aliases_path, "r", encoding="utf-8") as f:
            self.aliases = json.load(f)

        self.scheme_map = {s["scheme_id"]: s for s in self.schemes}

    def resolve_scheme(self, query: str) -> Dict[str, Any]:
        lower_query = query.lower()

        # Extract explicit plan and option
        extracted_plan = "Regular" if "regular" in lower_query else None
        extracted_option = "IDCW" if ("idcw" in lower_query or "dividend" in lower_query) else None

        # Check for explicit unsupported exotic plans
        if "bonus" in lower_query:
            return {
                "status": "UNSUPPORTED_PLAN",
                "resolved_scheme_id": None,
                "plan": "Bonus",
                "option": "Growth",
            }

        # 1. Exact Canonical Match
        for s in self.schemes:
            if s["canonical_name"].lower() in lower_query:
                return self._build_resolved_response(
                    s["scheme_id"], "EXACT_CANONICAL", extracted_plan, extracted_option
                )

        # 2. Curated Alias Match
        matched_schemes = set()
        for sid, alias_list in self.aliases.items():
            for alias in alias_list:
                # Use word-boundary matching for aliases
                pattern = r"\b" + re.escape(alias.lower()) + r"\b"
                if re.search(pattern, lower_query):
                    matched_schemes.add(sid)
                    break

        if len(matched_schemes) == 1:
            return self._build_resolved_response(
                list(matched_schemes)[0],
                "CURATED_ALIAS",
                extracted_plan,
                extracted_option,
            )

        if len(matched_schemes) > 1:
            return {
                "status": "AMBIGUOUS_SCHEME",
                "candidate_schemes": list(matched_schemes),
                "message": "Multiple matching schemes found. Please clarify which fund you are referring to.",
            }

        # 3. Partial Token Match across all schemes
        partial_matches = []
        for sid, scheme_info in self.scheme_map.items():
            amc_prefix = "sbi" if "sbi" in sid else "hdfc"
            tokens = [t for t in sid.split("_") if t not in [amc_prefix, "fund", "index", "direct", "growth"]]
            if tokens and all(t in lower_query for t in tokens):
                # If query contains an explicit AMC name, ensure it matches the scheme's AMC
                if "sbi" in lower_query and amc_prefix != "sbi":
                    continue
                if "hdfc" in lower_query and amc_prefix != "hdfc":
                    continue
                partial_matches.append(sid)

        if len(partial_matches) == 1:
            return self._build_resolved_response(partial_matches[0], "PARTIAL_MATCH", extracted_plan, extracted_option)
        elif len(partial_matches) > 1:
            return {
                "status": "AMBIGUOUS_SCHEME",
                "candidate_schemes": partial_matches,
                "message": "Multiple matching schemes found. Please clarify which fund you are referring to.",
            }

        return {
            "status": "UNRESOLVED_SCHEME",
            "resolved_scheme_id": None,
            "message": "No matching scheme found in the approved catalog.",
        }

    def _build_resolved_response(
        self,
        scheme_id: str,
        match_type: str,
        extracted_plan: Optional[str] = None,
        extracted_option: Optional[str] = None,
    ) -> Dict[str, Any]:
        scheme_info = self.scheme_map[scheme_id]

        plan = extracted_plan if extracted_plan else scheme_info["default_plan"]
        option = extracted_option if extracted_option else scheme_info["default_option"]

        base_name = scheme_info["canonical_name"].replace(" - Direct Growth", "")
        dynamic_canonical_name = f"{base_name} - {plan} {option}"

        return {
            "status": "RESOLVED",
            "scheme_id": scheme_id,
            "canonical_name": dynamic_canonical_name,
            "plan": plan,
            "option": option,
            "groww_url": scheme_info["groww_url"],
            "match_type": match_type,
        }

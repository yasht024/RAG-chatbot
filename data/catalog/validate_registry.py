import json
import sys
from pathlib import Path

def validate_registry():
    catalog_dir = Path(__file__).parent
    schemes_path = catalog_dir / "schemes.json"
    aliases_path = catalog_dir / "aliases.json"
    sources_path = catalog_dir / "sources.json"

    print("--- Mutual Fund FAQ Assistant: Registry Validation ---")

    # 1. Validate Schemes Catalog
    with open(schemes_path, "r", encoding="utf-8") as f:
        schemes = json.load(f)

    if len(schemes) != 35:
        print(f"FAILED: Expected exactly 35 schemes, but found {len(schemes)}")
        sys.exit(1)
    
    scheme_ids = set()
    for s in schemes:
        sid = s["scheme_id"]
        if sid in scheme_ids:
            print(f"FAILED: Duplicate scheme_id '{sid}'")
            sys.exit(1)
        scheme_ids.add(sid)

        # Ensure Groww URL is valid
        url = s.get("groww_url", "")
        if not url.startswith("https://groww.in/"):
            print(f"FAILED: Invalid Groww URL for scheme '{sid}': {url}")
            sys.exit(1)

    print(f"SUCCESS: Validated {len(schemes)} canonical schemes in schemes.json.")

    # 2. Validate Aliases Catalog
    with open(aliases_path, "r", encoding="utf-8") as f:
        aliases = json.load(f)

    total_aliases = 0
    for sid, alias_list in aliases.items():
        if sid not in scheme_ids:
            print(f"FAILED: Alias entry maps to non-existent scheme_id '{sid}'")
            sys.exit(1)
        total_aliases += len(alias_list)

    print(f"SUCCESS: Validated {total_aliases} curated aliases across {len(aliases)} schemes.")

    # 3. Validate Sources Allowlist
    with open(sources_path, "r", encoding="utf-8") as f:
        sources = json.load(f)

    if "groww.in" not in sources.get("allowed_domains", []):
        print("FAILED: 'groww.in' missing from allowed_domains")
        sys.exit(1)

    print("SUCCESS: Domain allowlist verified.")
    print("-----------------------------------------------------")
    print("REGISTRY VALIDATION PASSED: 100% Coverage for 35 Schemes.")

if __name__ == "__main__":
    validate_registry()

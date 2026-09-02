import json
from pathlib import Path

def remove_sbi_funds():
    root_dir = Path(__file__).parents[1]
    schemes_path = root_dir / "data" / "catalog" / "schemes.json"
    facts_path = root_dir / "data" / "catalog" / "scheme_facts.json"
    
    # 1. Update schemes.json
    with open(schemes_path, "r", encoding="utf-8") as f:
        schemes = json.load(f)
        
    filtered_schemes = [s for s in schemes if not s["scheme_id"].startswith("sbi_")]
    
    with open(schemes_path, "w", encoding="utf-8") as f:
        json.dump(filtered_schemes, f, indent=2)
        
    print(f"Removed SBI funds from schemes.json. Remaining: {len(filtered_schemes)}")

    # 2. Update scheme_facts.json
    with open(facts_path, "r", encoding="utf-8") as f:
        facts = json.load(f)
        
    keys_to_remove = [k for k in facts.keys() if k.startswith("sbi_")]
    for k in keys_to_remove:
        del facts[k]
        
    with open(facts_path, "w", encoding="utf-8") as f:
        json.dump(facts, f, indent=4)
        
    print(f"Removed SBI funds from scheme_facts.json. Remaining: {len(facts)}")

if __name__ == "__main__":
    remove_sbi_funds()

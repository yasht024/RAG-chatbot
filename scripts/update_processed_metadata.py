import os
import glob
import json
import re

processed_dir = r"C:\Users\yash.tiwari\OneDrive\Desktop\Milestone - RAG\data\processed"

files = glob.glob(os.path.join(processed_dir, "*.json"))

for filepath in files:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    filename = os.path.basename(filepath)
    is_sbi = filename.startswith("sbi_")

    data["source_org"] = "SBI Mutual Fund" if is_sbi else "HDFC AMC"
    data["source_domain"] = "sbimf.com" if is_sbi else "hdfcfund.com"
    data["source_type"] = "scheme_page"
    
    # We set publication_date to None because they were scraped from product pages without actual dates
    if "publication_date" not in data:
        data["publication_date"] = None
    if "effective_date" not in data:
        data["effective_date"] = None

    # Check if investment objective is missing in extracted_facts but present in full_text
    facts = data.get("extracted_facts", [])
    has_obj = any(f.get("fact_type", "").lower() == "investment_objective" for f in facts)
    
    if not has_obj:
        full_text = data.get("full_text", "")
        # Very simple extraction for investment objective from text like:
        # "The investment objective of the scheme is to provide long-term capital appreciation..."
        match = re.search(r"(investment objective[^.\n]*)", full_text, re.IGNORECASE)
        if match:
            obj_val = match.group(1).strip()
            # Clean up prefix if exists
            obj_val = re.sub(r"^(investment objective\s*of\s*the\s*scheme\s*is\s*|investment objective\s*is\s*|investment objective\s*:\s*|investment objective\s*)", "", obj_val, flags=re.IGNORECASE)
            
            if obj_val:
                facts.append({
                    "fact_type": "INVESTMENT_OBJECTIVE",
                    "value_display": obj_val,
                    "unit": None
                })
                data["extracted_facts"] = facts

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Updated {len(files)} JSON files in data/processed/")

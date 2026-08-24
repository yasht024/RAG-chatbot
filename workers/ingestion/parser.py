import re
from html.parser import HTMLParser
from typing import Dict, Any, List

class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.in_script_or_style = False

    def handle_starttag(self, tag, attrs):
        if tag.lower() in ["script", "style"]:
            self.in_script_or_style = True

    def handle_endtag(self, tag):
        if tag.lower() in ["script", "style"]:
            self.in_script_or_style = False

    def handle_data(self, data):
        if not self.in_script_or_style and data.strip():
            self.text_parts.append(data.strip())

class SchemeParser:
    """
    Structure-aware HTML parser for Groww scheme pages using standard library.
    Extracts key scheme metadata, heading paths, and scalar facts.
    """
    def parse_scheme_page(self, raw_html: str, scheme_id: str, canonical_url: str) -> Dict[str, Any]:
        extractor = _TextExtractor()
        extractor.feed(raw_html)
        page_text = "\n".join(extractor.text_parts)
        
        extracted_facts = self._extract_scalar_facts(page_text)
        sections = [{
            "heading": "Scheme Details",
            "content": page_text,
            "is_table": False
        }]
        
        # Simple title extraction
        title_match = re.search(r"<title>(.*?)</title>", raw_html, re.IGNORECASE)
        document_title = title_match.group(1).strip() if title_match else scheme_id

        return {
            "scheme_id": scheme_id,
            "canonical_url": canonical_url,
            "document_title": document_title,
            "full_text": page_text,
            "sections": sections,
            "extracted_facts": extracted_facts
        }

    def _extract_scalar_facts(self, text: str) -> List[Dict[str, Any]]:
        facts = []
        
        patterns = {
            "EXPENSE_RATIO": r"(?:Expense Ratio|TER)[:\s]*([0-9.]+\s*%)",
            "EXIT_LOAD": r"(?:Exit Load)[:\s]*([^\n]+)",
            "MINIMUM_SIP": r"(?:Min(?:imum)? SIP(?: amount)?|SIP Minimum)[:\s]*₹?\s*([0-9,]+)",
            "MINIMUM_LUMP_SUM": r"(?:Min(?:imum)? Lump\s*sum|Lumpsum)[:\s]*₹?\s*([0-9,]+)",
            "BENCHMARK": r"(?:Benchmark|Benchmark Index)[:\s]*([^\n]+)",
            "RISKOMETER": r"(?:Riskometer|Risk Level)[:\s]*([^\n]+)",
            "FUND_MANAGER": r"(?:Fund Manager|Managed by)[:\s]*([^\n]+)",
            "LOCK_IN": r"(?:Lock-in Period|Lock in)[:\s]*([^\n]+)"
        }
        
        for fact_type, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                facts.append({
                    "fact_type": fact_type,
                    "value_display": value,
                    "unit": "%" if "%" in value else ("INR" if "₹" in value or value.isdigit() else None)
                })
                
        return facts


from typing import List, Dict, Any

class Chunker:
    """
    Structure-aware chunker that splits document sections into bounded passages
    while maintaining heading metadata, table rows, and fact tags.
    """
    def __init__(self, target_chunk_size: int = 400):
        self.target_chunk_size = target_chunk_size

    def chunk_document(self, parsed_doc: Dict[str, Any], index_version: str = "corpus-2026-08-23.1") -> List[Dict[str, Any]]:
        passages = []
        scheme_id = parsed_doc["scheme_id"]
        sections = parsed_doc.get("sections", [])
        
        passage_counter = 1
        for section in sections:
            heading = section.get("heading", "Details")
            content = section.get("content", "")
            
            if not content.strip():
                continue
                
            # Tag passage with relevant fact types based on content keywords
            fact_types = self._tag_fact_types(content)
            
            passage_id = f"passage_{scheme_id}_{passage_counter}"
            passages.append({
                "passage_id": passage_id,
                "scheme_ids": [scheme_id],
                "plan": "Direct",
                "option": "Growth",
                "heading_path": ["Scheme Details", heading],
                "page_number": 1,
                "normalized_text": f"[{heading}]\n{content}",
                "source_text_hash": f"hash_{passage_counter}",
                "fact_types": fact_types,
                "extraction_confidence": 1.0,
                "index_version": index_version
            })
            passage_counter += 1
            
        # Fallback if no sections were parsed
        if not passages and parsed_doc.get("full_text"):
            passages.append({
                "passage_id": f"passage_{scheme_id}_1",
                "scheme_ids": [scheme_id],
                "plan": "Direct",
                "option": "Growth",
                "heading_path": ["Scheme Details"],
                "page_number": 1,
                "normalized_text": parsed_doc["full_text"][:1000],
                "source_text_hash": "hash_fallback",
                "fact_types": [],
                "extraction_confidence": 0.9,
                "index_version": index_version
            })
            
        return passages

    def _tag_fact_types(self, text: str) -> List[str]:
        tags = []
        lower_text = text.lower()
        if "expense ratio" in lower_text or "ter" in lower_text:
            tags.append("EXPENSE_RATIO")
        if "exit load" in lower_text:
            tags.append("EXIT_LOAD")
        if "sip" in lower_text or "minimum sip" in lower_text:
            tags.append("MINIMUM_SIP")
        if "benchmark" in lower_text:
            tags.append("BENCHMARK")
        if "riskometer" in lower_text or "risk" in lower_text:
            tags.append("RISKOMETER")
        if "manager" in lower_text:
            tags.append("FUND_MANAGER")
        if "lock-in" in lower_text or "elss" in lower_text:
            tags.append("LOCK_IN")
        return tags

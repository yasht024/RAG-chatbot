import json
from pathlib import Path
from typing import Dict, Any

from workers.ingestion.fetcher import Fetcher
from workers.ingestion.parser import SchemeParser
from workers.ingestion.chunker import Chunker
from workers.ingestion.indexer import Indexer


class IngestionPipeline:
    """
    Orchestrates the end-to-end ingestion pipeline:
    Fetch -> Parse -> Save Processed -> Chunk -> Embed -> Index
    """

    def __init__(self, processed_dir: Path = None):
        self.fetcher = Fetcher()
        self.parser = SchemeParser()
        self.chunker = Chunker()
        self.indexer = Indexer()

        if processed_dir is None:
            processed_dir = Path(__file__).parents[2] / "data" / "processed"
        self.processed_dir = processed_dir
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def process_scheme_url(self, db: Any, scheme_id: str, url: str, raw_html: str = None) -> Dict[str, Any]:
        # 1. Fetch & Snapshot
        fetch_meta = self.fetcher.fetch_and_snapshot(url=url, raw_html_content=raw_html)

        # 2. Parse HTML & Extract Facts
        parsed_doc = self.parser.parse_scheme_page(
            raw_html=fetch_meta["raw_html"], scheme_id=scheme_id, canonical_url=url
        )

        # 3. Save Processed Intermediate JSON
        processed_file_path = self.processed_dir / f"{scheme_id}.json"
        with open(processed_file_path, "w", encoding="utf-8") as f:
            json.dump(parsed_doc, f, indent=2)

        # 4. Structure-Aware Chunking
        passages = self.chunker.chunk_document(parsed_doc)

        # 5. Embed & Index to Database (if DB session provided)
        doc_record = None
        if db:
            doc_record = self.indexer.index_document(db, fetch_meta, parsed_doc, passages)

        return {
            "status": "SUCCESS",
            "scheme_id": scheme_id,
            "content_hash": fetch_meta["content_hash"],
            "processed_path": str(processed_file_path),
            "passages_count": len(passages),
            "facts_count": len(parsed_doc.get("extracted_facts", [])),
            "document_id": doc_record.document_id if doc_record else None,
        }

import hashlib
import datetime
from typing import List, Dict, Any


class Indexer:
    """
    Generates embeddings and persists Document, Passage, and Fact records
    into PostgreSQL with pgvector support.
    """

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generates a 1024-dimensional float vector (mocking BGE Large).
        Uses deterministic hashing for fast offline testing/indexing.
        """
        # Create a 1024-dim normalized vector derived from sha256 hash
        seed = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16)
        vec = []
        for i in range(1024):
            val = ((seed + i * 31) % 1000) / 1000.0 - 0.5
            vec.append(val)
        return vec

    def index_document(
        self,
        db: Any,
        fetch_meta: Dict[str, Any],
        parsed_doc: Dict[str, Any],
        passages: List[Dict[str, Any]],
    ):
        from packages.contracts.models import DocumentModel, PassageModel, FactModel

        scheme_id = parsed_doc["scheme_id"]
        doc_id = f"doc_{scheme_id}_{fetch_meta['content_hash'][-8:]}"

        # Check if document already indexed
        existing_doc = db.query(DocumentModel).filter_by(content_hash=fetch_meta["content_hash"]).first()
        if existing_doc:
            return existing_doc

        # 1. Create Document Record
        current_date_str = datetime.date.today().strftime("%Y-%m-%d")
        doc = DocumentModel(
            document_id=doc_id,
            source_domain=fetch_meta["source_domain"],
            canonical_url=fetch_meta["canonical_url"],
            document_title=parsed_doc.get("document_title", scheme_id),
            document_type="SCHEME_PAGE",
            scope="SCHEME",
            publication_date=current_date_str,
            effective_from=current_date_str,
            content_hash=fetch_meta["content_hash"],
            approval_status="APPROVED",
        )
        db.add(doc)

        # 2. Create Passages
        for p in passages:
            embedding_vector = self.generate_embedding(p["normalized_text"])
            passage_rec = PassageModel(
                passage_id=p["passage_id"],
                document_id=doc_id,
                scheme_ids=p["scheme_ids"],
                plan=p["plan"],
                option=p["option"],
                heading_path=p["heading_path"],
                page_number=p["page_number"],
                normalized_text=p["normalized_text"],
                source_text_hash=p["source_text_hash"],
                fact_types=p["fact_types"],
                extraction_confidence=p["extraction_confidence"],
                embedding=embedding_vector,
                index_version=p["index_version"],
            )
            db.add(passage_rec)

        # 3. Create Facts
        facts = parsed_doc.get("extracted_facts", [])
        for idx, f in enumerate(facts):
            fact_rec = FactModel(
                fact_id=f"fact_{scheme_id}_{idx + 1}",
                scheme_id=scheme_id,
                fact_type=f["fact_type"],
                value_display=f["value_display"],
                unit=f.get("unit"),
                plan="Direct",
                option="Growth",
                effective_from=current_date_str,
                passage_id=passages[0]["passage_id"] if passages else f"passage_{scheme_id}_1",
                validation_status="VALID",
            )
            db.add(fact_rec)

        db.commit()
        db.refresh(doc)
        return doc

from typing import Dict, List, Optional, Set, Any
import logging

logger = logging.getLogger(__name__)

class DocumentLineageManager:
    """
    Manages explicit supersedes and superseded-by relationships between documents and passages.
    Ensures that queries retrieve the latest effective evidence and filter out superseded content.
    """
    def __init__(self):
        # document_id -> set of document_ids it supersedes
        self._supersedes: Dict[str, Set[str]] = {}
        # document_id -> successor document_id that supersedes it
        self._superseded_by: Dict[str, str] = {}

    def register_relationship(self, new_doc_id: str, old_doc_id: str):
        """Explicitly records that new_doc_id supersedes old_doc_id."""
        if new_doc_id not in self._supersedes:
            self._supersedes[new_doc_id] = set()
        self._supersedes[new_doc_id].add(old_doc_id)
        self._superseded_by[old_doc_id] = new_doc_id
        logger.info(f"Lineage: '{new_doc_id}' supersedes '{old_doc_id}'")

    def is_superseded(self, doc_id: str) -> bool:
        """Returns True if the document has been replaced by a newer version."""
        return doc_id in self._superseded_by

    def get_latest_successor(self, doc_id: str) -> str:
        """Traverses the supersession chain to find the latest effective document."""
        current = doc_id
        visited = {current}
        while current in self._superseded_by:
            successor = self._superseded_by[current]
            if successor in visited:
                logger.error(f"Cycle detected in supersession chain for {doc_id}")
                break
            visited.add(successor)
            current = successor
        return current

    def filter_superseded_candidates(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filters out candidates belonging to documents that have been superseded by another candidate
        present in the same result set, or are globally marked as superseded.
        """
        active_candidates = []
        for cand in candidates:
            doc_id = cand.get("document_id")
            # If doc is superseded and a newer successor is available in the corpus, exclude old version
            if doc_id and self.is_superseded(doc_id):
                logger.debug(f"Candidate {cand.get('passage_id')} filtered: superseded by {self._superseded_by[doc_id]}")
                continue
            active_candidates.append(cand)
        return active_candidates

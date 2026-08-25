import time
import logging
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ConflictStatus(str, Enum):
    QUARANTINED = "QUARANTINED"
    RESOLVED = "RESOLVED"
    IGNORED = "IGNORED"


class ConflictRecord(BaseModel):
    conflict_id: str
    scheme_id: str
    fact_type: str
    conflicting_passages: List[Dict[str, Any]]
    detected_at: float = Field(default_factory=time.time)
    status: ConflictStatus = ConflictStatus.QUARANTINED
    resolved_by: Optional[str] = None
    resolution_reason: Optional[str] = None
    selected_passage_id: Optional[str] = None


class ConflictRegistry:
    """
    Registry for tracking fact conflicts across documents, managing operator reviews,
    and enforcing quarantine to prevent serving conflicting or ambiguous data.
    """

    def __init__(self):
        self._conflicts: Dict[str, ConflictRecord] = {}

    def record_conflict(
        self, scheme_id: str, fact_type: str, conflicting_passages: List[Dict[str, Any]]
    ) -> ConflictRecord:
        conflict_key = f"{scheme_id}:{fact_type}"
        record = ConflictRecord(
            conflict_id=conflict_key,
            scheme_id=scheme_id,
            fact_type=fact_type,
            conflicting_passages=conflicting_passages,
            status=ConflictStatus.QUARANTINED,
        )
        self._conflicts[conflict_key] = record
        logger.warning(f"Recorded and quarantined conflict for [{conflict_key}]")
        return record

    def is_quarantined(self, scheme_id: str, fact_type: str) -> bool:
        conflict_key = f"{scheme_id}:{fact_type}"
        if conflict_key in self._conflicts:
            return self._conflicts[conflict_key].status == ConflictStatus.QUARANTINED
        return False

    def resolve_conflict(
        self,
        scheme_id: str,
        fact_type: str,
        selected_passage_id: str,
        operator_name: str,
        reason: str,
    ) -> ConflictRecord:
        conflict_key = f"{scheme_id}:{fact_type}"
        if conflict_key not in self._conflicts:
            raise KeyError(f"No conflict found for {conflict_key}")

        record = self._conflicts[conflict_key]
        record.status = ConflictStatus.RESOLVED
        record.selected_passage_id = selected_passage_id
        record.resolved_by = operator_name
        record.resolution_reason = reason
        logger.info(f"Conflict [{conflict_key}] resolved by {operator_name}: {reason}")
        return record

    def get_conflict(self, scheme_id: str, fact_type: str) -> Optional[ConflictRecord]:
        return self._conflicts.get(f"{scheme_id}:{fact_type}")

    def list_quarantined_conflicts(self) -> List[ConflictRecord]:
        return [c for c in self._conflicts.values() if c.status == ConflictStatus.QUARANTINED]

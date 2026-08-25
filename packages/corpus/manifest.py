import time
import logging
from enum import Enum
from typing import Dict, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ManifestStatus(str, Enum):
    STAGED = "STAGED"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    REJECTED = "REJECTED"
    ROLLED_BACK = "ROLLED_BACK"


class CorpusManifest(BaseModel):
    manifest_id: str
    version: str
    schemes_count: int
    documents_count: int
    created_at: float = Field(default_factory=time.time)
    status: ManifestStatus = ManifestStatus.STAGED
    approved_by: Optional[str] = None
    approval_timestamp: Optional[float] = None
    index_alias_target: Optional[str] = None


class CorpusManifestManager:
    """
    Manages corpus manifests, staging approvals, Blue/Green index publications,
    and instantaneous rollback capabilities.
    """

    def __init__(self):
        self._manifests: Dict[str, CorpusManifest] = {}
        self.active_manifest_id: Optional[str] = None
        self.previous_active_manifest_id: Optional[str] = None
        # Blue/Green serving pointer
        self.active_slot: str = "blue"  # 'blue' or 'green'

    def register_manifest(
        self, manifest_id: str, version: str, schemes_count: int, documents_count: int
    ) -> CorpusManifest:
        manifest = CorpusManifest(
            manifest_id=manifest_id,
            version=version,
            schemes_count=schemes_count,
            documents_count=documents_count,
            status=ManifestStatus.STAGED,
        )
        self._manifests[manifest_id] = manifest
        logger.info(f"Registered staged manifest [{manifest_id}] for version {version}")
        return manifest

    def approve_manifest(self, manifest_id: str, approver: str) -> CorpusManifest:
        if manifest_id not in self._manifests:
            raise KeyError(f"Manifest {manifest_id} does not exist")
        manifest = self._manifests[manifest_id]
        manifest.status = ManifestStatus.APPROVED
        manifest.approved_by = approver
        manifest.approval_timestamp = time.time()
        logger.info(f"Manifest [{manifest_id}] APPROVED by {approver}")
        return manifest

    def publish_blue_green(self, manifest_id: str) -> str:
        """
        Switches the serving alias atomically from active slot to inactive slot
        only if the manifest has been approved.
        """
        if manifest_id not in self._manifests:
            raise KeyError(f"Manifest {manifest_id} does not exist")
        manifest = self._manifests[manifest_id]
        if manifest.status != ManifestStatus.APPROVED:
            raise ValueError(
                f"Cannot publish manifest [{manifest_id}] with status {manifest.status}. Must be APPROVED."
            )

        # Determine target slot
        target_slot = "green" if self.active_slot == "blue" else "blue"

        # Save previous for rollback
        self.previous_active_manifest_id = self.active_manifest_id

        # Switch pointer
        manifest.status = ManifestStatus.ACTIVE
        manifest.index_alias_target = target_slot
        self.active_manifest_id = manifest_id
        self.active_slot = target_slot

        logger.info(f"Blue/Green switch complete: Slot is now [{self.active_slot}] serving manifest [{manifest_id}]")
        return self.active_slot

    def rollback(self) -> str:
        """
        Rolls back to the previously active manifest and flips the Blue/Green slot back.
        """
        if not self.previous_active_manifest_id or self.previous_active_manifest_id not in self._manifests:
            raise RuntimeError("No valid previous manifest available for rollback.")

        current = self._manifests[self.active_manifest_id]
        current.status = ManifestStatus.ROLLED_BACK

        target_slot = "green" if self.active_slot == "blue" else "blue"
        prev_manifest = self._manifests[self.previous_active_manifest_id]
        prev_manifest.status = ManifestStatus.ACTIVE

        self.active_manifest_id = self.previous_active_manifest_id
        self.active_slot = target_slot
        logger.warning(
            f"Rollback executed! Slot is now [{self.active_slot}] serving previous manifest [{self.active_manifest_id}]"
        )
        return self.active_manifest_id

    def get_active_manifest(self) -> Optional[CorpusManifest]:
        if self.active_manifest_id:
            return self._manifests.get(self.active_manifest_id)
        return None

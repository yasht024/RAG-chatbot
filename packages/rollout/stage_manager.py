import time
import logging
from enum import Enum
from typing import Set, Optional, List
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class RolloutStage(str, Enum):
    INTERNAL_QA = "INTERNAL_QA"
    INTERNAL_PILOT = "INTERNAL_PILOT"
    LIMITED_PROD = "LIMITED_PROD"
    EXPANDED_PROD = "EXPANDED_PROD"
    GENERAL_AVAILABILITY = "GENERAL_AVAILABILITY"


class RolloutDecision(BaseModel):
    allowed: bool
    stage: RolloutStage
    reason: str
    canary_routed: bool = False


class RolloutStageManager:
    """
    Manages rollout progression (P3B-07, P3B-08, P3B-09) and automated rollback triggers (Section 13.4).
    """

    def __init__(self, initial_stage: RolloutStage = RolloutStage.INTERNAL_QA):
        self.stage = initial_stage
        self.allowlist_users: Set[str] = set()
        self.canary_percentage: float = 0.0
        self.is_emergency_refusal_mode: bool = False
        self.incident_log: List[str] = []

    def set_stage(self, stage: RolloutStage, canary_percentage: float = 0.0):
        self.stage = stage
        self.canary_percentage = canary_percentage
        logger.info(f"Rollout stage transitioned to [{stage}] with {canary_percentage}% canary traffic.")

    def add_allowlist_user(self, user_id: str):
        self.allowlist_users.add(user_id)

    def evaluate_request_access(self, user_id: Optional[str] = None) -> RolloutDecision:
        """
        Determines whether a user or request is permitted based on current rollout stage.
        """
        if self.is_emergency_refusal_mode:
            return RolloutDecision(
                allowed=False,
                stage=self.stage,
                reason="System is in emergency refusal-only mode due to active incident.",
            )

        if self.stage == RolloutStage.INTERNAL_QA:
            if user_id and user_id in self.allowlist_users:
                return RolloutDecision(allowed=True, stage=self.stage, reason="Internal QA user approved.")
            return RolloutDecision(allowed=False, stage=self.stage, reason="Internal QA restricted.")

        elif self.stage == RolloutStage.INTERNAL_PILOT:
            if user_id and user_id in self.allowlist_users:
                return RolloutDecision(
                    allowed=True,
                    stage=self.stage,
                    reason="Internal Pilot user approved.",
                )
            return RolloutDecision(allowed=False, stage=self.stage, reason="Internal Pilot restricted.")

        elif self.stage in [
            RolloutStage.LIMITED_PROD,
            RolloutStage.EXPANDED_PROD,
            RolloutStage.GENERAL_AVAILABILITY,
        ]:
            return RolloutDecision(
                allowed=True,
                stage=self.stage,
                reason="Production traffic permitted.",
                canary_routed=True,
            )

        return RolloutDecision(allowed=False, stage=self.stage, reason="Unauthorized stage.")

    def trigger_emergency_rollback(self, reason: str):
        """
        Section 13.4: Automatically switches to safe refusal mode if critical violation occurs
        (e.g., unsupported claim, non-official citation, unapproved advice).
        """
        self.is_emergency_refusal_mode = True
        self.incident_log.append(f"{time.strftime('%Y-%m-%d %H:%M:%S')}: {reason}")
        logger.critical(f"EMERGENCY ROLLBACK TRIGGERED: {reason}")

    def reset_emergency_mode(self):
        self.is_emergency_refusal_mode = False
        logger.info("Emergency refusal mode reset to normal operation.")

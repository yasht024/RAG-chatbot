import time
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class LLMRateLimiter:
    """
    Tracks and enforces strict Request and Token rate limits for LLM calls:
    - RPM: 30 requests / minute
    - RPD: 1,000 requests / day (86,400 sec)
    - TPM: 8,000 tokens / minute
    - TPD: 200,000 tokens / day (86,400 sec)

    If limits are exceeded, throttles or signals fallback to local deterministic template generation.
    """

    def __init__(
        self,
        max_rpm: int = 30,
        max_rpd: int = 1000,
        max_tpm: int = 8000,
        max_tpd: int = 200000,
    ):
        self.max_rpm = max_rpm
        self.max_rpd = max_rpd
        self.max_tpm = max_tpm
        self.max_tpd = max_tpd

        # Timestamps for minute/day sliding windows
        self._minute_requests: list[float] = []
        self._day_requests: list[float] = []

        # (timestamp, token_count) tuples for minute/day token tracking
        self._minute_tokens: list[Tuple[float, int]] = []
        self._day_tokens: list[Tuple[float, int]] = []

    def _cleanup_windows(self, now: float):
        # 1 minute window (60s)
        self._minute_requests = [t for t in self._minute_requests if now - t < 60.0]
        self._minute_tokens = [t for t in self._minute_tokens if now - t[0] < 60.0]

        # 1 day window (86400s)
        self._day_requests = [t for t in self._day_requests if now - t < 86400.0]
        self._day_tokens = [t for t in self._day_tokens if now - t[0] < 86400.0]

    def estimate_tokens(self, text: str) -> int:
        """Rough token count estimation (avg 4 chars per token)."""
        if not text:
            return 0
        return max(1, len(text) // 4)

    def check_capacity(self, estimated_tokens: int = 150) -> Tuple[bool, Optional[str]]:
        """
        Checks whether the incoming request fits within RPM, RPD, TPM, and TPD quotas.
        """
        now = time.time()
        self._cleanup_windows(now)

        # Check Requests per Minute (RPM)
        if len(self._minute_requests) >= self.max_rpm:
            return (
                False,
                f"RPM limit exceeded ({len(self._minute_requests)}/{self.max_rpm})",
            )

        # Check Requests per Day (RPD)
        if len(self._day_requests) >= self.max_rpd:
            return (
                False,
                f"RPD limit exceeded ({len(self._day_requests)}/{self.max_rpd})",
            )

        # Check Tokens per Minute (TPM)
        current_tpm = sum(count for _, count in self._minute_tokens)
        if current_tpm + estimated_tokens > self.max_tpm:
            return (
                False,
                f"TPM limit exceeded ({current_tpm + estimated_tokens}/{self.max_tpm})",
            )

        # Check Tokens per Day (TPD)
        current_tpd = sum(count for _, count in self._day_tokens)
        if current_tpd + estimated_tokens > self.max_tpd:
            return (
                False,
                f"TPD limit exceeded ({current_tpd + estimated_tokens}/{self.max_tpd})",
            )

        return True, None

    def record_usage(self, token_count: int):
        """Records a successful request and token consumption in sliding windows."""
        now = time.time()
        self._minute_requests.append(now)
        self._day_requests.append(now)
        self._minute_tokens.append((now, token_count))
        self._day_tokens.append((now, token_count))
        logger.debug(
            f"LLM usage recorded: {token_count} tokens. RPM={len(self._minute_requests)}, RPD={len(self._day_requests)}"
        )

    def reset(self):
        """Reset all tracking counters (primarily for testing)."""
        self._minute_requests.clear()
        self._day_requests.clear()
        self._minute_tokens.clear()
        self._day_tokens.clear()

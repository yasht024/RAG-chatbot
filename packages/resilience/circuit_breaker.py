import time
import logging
from enum import Enum
from typing import Callable, Any, Optional

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreakerOpenException(Exception):
    """Raised when an operation is attempted while the circuit breaker is open."""

    pass


class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout_sec: float = 10.0,
        name: str = "default",
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout_sec = recovery_timeout_sec
        self.name = name
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_state_change = time.time()

    def _update_state(self):
        now = time.time()
        if self.state == CircuitState.OPEN:
            if (now - self.last_state_change) > self.recovery_timeout_sec:
                self.state = CircuitState.HALF_OPEN
                self.last_state_change = now
                logger.info(f"CircuitBreaker [{self.name}] transition from OPEN -> HALF_OPEN")

    def call(self, func: Callable, *args, fallback: Optional[Callable] = None, **kwargs) -> Any:
        self._update_state()

        if self.state == CircuitState.OPEN:
            logger.warning(f"CircuitBreaker [{self.name}] is OPEN. Executing fallback or raising.")
            if fallback is not None:
                return fallback(*args, **kwargs)
            raise CircuitBreakerOpenException(f"CircuitBreaker [{self.name}] is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure(e)
            if fallback is not None:
                return fallback(*args, **kwargs)
            raise

    def _on_success(self):
        if self.state == CircuitState.HALF_OPEN or self.failure_count > 0:
            logger.info(f"CircuitBreaker [{self.name}] success: Resetting state to CLOSED.")
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self, exception: Exception):
        self.failure_count += 1
        logger.warning(f"CircuitBreaker [{self.name}] recorded failure #{self.failure_count}: {exception}")
        if self.failure_count >= self.failure_threshold or self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            self.last_state_change = time.time()
            logger.error(f"CircuitBreaker [{self.name}] tripped! State is now OPEN.")

    def reset(self):
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_state_change = time.time()

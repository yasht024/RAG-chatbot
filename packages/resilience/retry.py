import time
import logging
from typing import Callable, Any, Tuple, Type

logger = logging.getLogger(__name__)


def retry_with_backoff(
    func: Callable,
    max_retries: int = 2,
    initial_delay: float = 0.1,
    backoff_factor: float = 2.0,
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    *args,
    **kwargs,
) -> Any:
    """
    Executes a callable with exponential backoff retry for transient network/API failures.
    """
    delay = initial_delay
    last_exception = None

    for attempt in range(1, max_retries + 1):
        try:
            return func(*args, **kwargs)
        except retryable_exceptions as e:
            last_exception = e
            if attempt == max_retries:
                logger.error(f"Retry exhausted ({attempt}/{max_retries}) for {func.__name__}: {e}")
                raise
            logger.warning(
                f"Attempt {attempt}/{max_retries} failed for {func.__name__} with error: {e}. "
                f"Retrying in {delay:.2f}s..."
            )
            time.sleep(delay)
            delay *= backoff_factor

    if last_exception:
        raise last_exception

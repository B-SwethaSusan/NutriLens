import asyncio
import functools
import logging
from collections.abc import Callable

logger = logging.getLogger(__name__)


def async_retry(attempts: int = 3, delay: float = 0.8):
    def decorator(function: Callable):
        @functools.wraps(function)
        async def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(attempts):
                try:
                    return await function(*args, **kwargs)
                except Exception as exc:  # third-party transient errors vary by provider
                    last_error = exc
                    if attempt == attempts - 1:
                        raise
                    logger.warning("Retrying %s after error: %s", function.__name__, exc)
                    await asyncio.sleep(delay * (attempt + 1))
            raise last_error  # type: ignore[misc]

        return wrapper

    return decorator

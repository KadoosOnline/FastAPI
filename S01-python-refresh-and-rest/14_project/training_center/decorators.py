"""Typed decorators: they keep the signature of the function they wrap."""

import functools
import logging
import time
from collections.abc import Callable

logger = logging.getLogger('training_center')


def log_calls[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    """Log every call, its result, and any exception (then re-raise it)."""

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        logger.info('calling %s args=%r kwargs=%r', func.__qualname__, args[1:], kwargs)
        try:
            result = func(*args, **kwargs)
        except Exception as exc:
            logger.warning('%s raised %s: %s', func.__qualname__, type(exc).__name__, exc)
            raise
        logger.info('%s returned %r', func.__qualname__, result)
        return result

    return wrapper


def timed[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    """Measure how long a call takes; the duration is stored on the wrapper."""

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        started = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            wrapper.last_duration = time.perf_counter() - started  # type: ignore[attr-defined]

    wrapper.last_duration = 0.0  # type: ignore[attr-defined]
    return wrapper


def retry[**P, R](
    times: int, exceptions: tuple[type[Exception], ...] = (Exception,)
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator *factory*: `@retry(3, (ConnectionError,))`."""
    if times < 1:
        raise ValueError('times must be at least 1')

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt == times:
                        raise
                    logger.info('retrying %s (attempt %d)', func.__qualname__, attempt + 1)
            raise AssertionError('unreachable')

        return wrapper

    return decorator

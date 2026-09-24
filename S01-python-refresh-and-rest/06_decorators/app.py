"""Decorators: wrap a function to add behaviour, without touching its code.

    @log_calls
    def enroll(student_id: int, course_id: int) -> str: ...

is exactly the same as

    enroll = log_calls(enroll)

Three things every decorator in this course does right:
1. `@functools.wraps(func)` -- keeps the name and docstring of the original.
   FastAPI reads the *signature* of your functions, so a decorator that hides
   it breaks FastAPI.
2. `ParamSpec` (`[**P, R]`) -- keeps the parameter types, so the editor still
   knows that `enroll` takes two ints.
3. Exceptions are re-raised, never swallowed.

A decorator *factory* takes arguments and returns a decorator:
    @retry(times=3)

FastAPI itself is built with decorators: `@app.get("/courses")` registers
your function as the handler of that address.
"""

import functools
import logging
import time
from collections.abc import Callable

logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
logger = logging.getLogger('training')


def log_calls[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        logger.info('-> %s%s', func.__name__, args)
        try:
            result = func(*args, **kwargs)
        except Exception as error:
            logger.warning('<- %s raised %r', func.__name__, error)
            raise
        logger.info('<- %s returned %r', func.__name__, result)
        return result

    return wrapper


def timed[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        started = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = (time.perf_counter() - started) * 1000
            logger.info('%s took %.1f ms', func.__name__, elapsed)

    return wrapper


def retry[**P, R](times: int) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """A decorator factory: `@retry(3)` returns the real decorator."""

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except ConnectionError:
                    if attempt == times:
                        raise
                    logger.info('attempt %d failed, retrying', attempt)
            raise AssertionError('unreachable')

        return wrapper

    return decorator


@log_calls
def enroll(student_id: int, course_id: int) -> str:
    """Enroll a student in a course."""
    if course_id == 99:
        raise ValueError('course 99 is full')
    return f'student {student_id} -> course {course_id}'


calls = 0


@timed
@retry(times=3)
def flaky_remote_call() -> str:
    """Fails twice, then works: like a shaky network."""
    global calls
    calls += 1
    if calls < 3:
        raise ConnectionError('network down')
    return 'finally!'


def main() -> None:
    enroll(1, 2)
    try:
        enroll(1, 99)
    except ValueError:
        pass
    print(flaky_remote_call())
    # wraps() kept the metadata:
    print(enroll.__name__, '-', enroll.__doc__)


if __name__ == '__main__':
    main()

"""Context managers: "set up, run the block, ALWAYS clean up".

    with open('file.txt') as f:     # the file is closed even after an error
        ...

The same pattern appears everywhere in backend code:

    with Session(engine) as session:          # SQLAlchemy, session 5
        ...                                   # connection given back afterwards
    async with httpx.AsyncClient() as client: # HTTPX, session 15
        ...
    @asynccontextmanager                      # FastAPI "lifespan", session 12
    async def lifespan(app): ...

and FastAPI dependencies with `yield` (session 4) are context managers too.

Two ways to write one:
1. A class with `__enter__` and `__exit__`
2. A generator function with `@contextmanager` (usually simpler)

Below, a tiny "database transaction": changes are kept only if the block
finishes without an exception; otherwise everything is rolled back.
"""

import copy
import time
from collections.abc import Iterator
from contextlib import contextmanager
from types import TracebackType
from typing import Literal


class Timer:
    """Class-based context manager."""

    def __enter__(self) -> 'Timer':
        self.started = time.perf_counter()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> Literal[False]:
        self.elapsed = time.perf_counter() - self.started
        print(f'block took {self.elapsed * 1000:.2f} ms')
        return False  # False = do not swallow the exception


DATABASE: dict[str, list[str]] = {'students': ['sara']}


@contextmanager
def transaction(db: dict[str, list[str]]) -> Iterator[dict[str, list[str]]]:
    """Generator-based context manager: everything before `yield` is __enter__."""
    snapshot = copy.deepcopy(db)
    print('BEGIN')
    try:
        yield db
    except Exception:
        db.clear()
        db.update(snapshot)
        print('ROLLBACK')
        raise
    else:
        print('COMMIT')


def main() -> None:
    with Timer():
        sum(range(100_000))

    with transaction(DATABASE) as db:
        db['students'].append('reza')
    print(DATABASE)

    try:
        with transaction(DATABASE) as db:
            db['students'].append('ghost')
            raise RuntimeError('payment failed half way')
    except RuntimeError as error:
        print('error:', error)
    print(DATABASE)  # 'ghost' is gone


if __name__ == '__main__':
    main()

"""Generators: produce values one at a time, only when asked.

A function with `yield` returns a generator. It does not build a whole list
in memory; it hands out one item, pauses, and continues on the next request.

Backend uses:
* Reading huge tables or files row by row.
* Walking through a paginated API: page 1, page 2, ... until the end
  (our REST client does exactly this in session 14).
* FastAPI dependencies with `yield` (session 4) and `StreamingResponse`.

Generator expression: `(c.price for c in courses)` -- like a list
comprehension, but lazy. `sum(...)`, `any(...)`, `max(...)` accept them.
"""

from collections.abc import Iterator
from itertools import batched, islice

ALL_COURSE_IDS = list(range(1, 24))  # pretend this is a big table


def fetch_page(page: int, size: int) -> list[int]:
    """Pretend to be an API: returns one page of ids (empty at the end)."""
    start = (page - 1) * size
    print(f'  ...fetching page {page}')
    return ALL_COURSE_IDS[start : start + size]


def iterate_all(size: int = 10) -> Iterator[int]:
    """Hide pagination from the caller: they just see a stream of ids."""
    page = 1
    while items := fetch_page(page, size):
        yield from items
        page += 1


def main() -> None:
    # Only the pages that are really needed get fetched:
    first_twelve = list(islice(iterate_all(), 12))
    print(first_twelve)

    # A lazy pipeline: nothing runs until sum() pulls the values.
    total = sum(course_id * 1000 for course_id in iterate_all() if course_id % 2 == 0)
    print(total)

    # Python 3.12: split any iterable into fixed-size chunks
    for chunk in batched(range(1, 8), 3):
        print(chunk)


if __name__ == '__main__':
    main()

"""async / await: waiting for many things at the same time.

A backend spends most of its time WAITING: for the database, for another
API, for a file. While one request waits, the server could serve others.

    async def fetch(...)      defines a coroutine function
    await something           "pause me here, let others run, come back later"
    asyncio.gather(a, b, c)   run several coroutines concurrently
    asyncio.run(main())       start the event loop (FastAPI/uvicorn does this for us)

The golden rule (session 12 is all about it):
    inside `async def`, never call something that blocks -- `time.sleep()`,
    `requests.get()`, a sync database call. It freezes EVERY request.
    Use the async version: `await asyncio.sleep()`, `httpx.AsyncClient`,
    `AsyncSession`.

Run this file and compare the three timings.
"""

import asyncio
import time


async def fetch_seats(course_id: int) -> int:
    """Pretend network call that takes 0.5 s."""
    await asyncio.sleep(0.5)
    return 10 + course_id


async def sequential(ids: list[int]) -> list[int]:
    return [await fetch_seats(course_id) for course_id in ids]


async def concurrent(ids: list[int]) -> list[int]:
    return list(await asyncio.gather(*(fetch_seats(course_id) for course_id in ids)))


async def blocking_mistake(ids: list[int]) -> None:
    """time.sleep() inside async code: gather cannot help, the loop is frozen."""

    async def bad(course_id: int) -> None:
        time.sleep(0.5)  # WRONG inside async def

    await asyncio.gather(*(bad(course_id) for course_id in ids))


async def with_timeout() -> None:
    try:
        async with asyncio.timeout(0.2):
            await fetch_seats(1)
    except TimeoutError:
        print('gave up after 0.2 s')


async def main() -> None:
    ids = [1, 2, 3, 4]
    for label, job in [('sequential', sequential), ('concurrent', concurrent)]:
        started = time.perf_counter()
        result = await job(ids)
        print(f'{label:<11} {time.perf_counter() - started:.2f}s  {result}')

    started = time.perf_counter()
    await blocking_mistake(ids)
    print(f'blocking    {time.perf_counter() - started:.2f}s  (gather did not help!)')

    await with_timeout()


if __name__ == '__main__':
    asyncio.run(main())

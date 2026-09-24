"""Common async mistakes, each one reproduced and fixed.

1. Forgetting `await`       -> you get a coroutine object, not the result
2. Blocking the loop        -> time.sleep / requests / heavy CPU work inside async
3. Sharing one AsyncSession between concurrent tasks -> errors; one session per task
4. CPU-bound work           -> async does not make maths faster; move it to a thread
                               (asyncio.to_thread) or a process
"""

import asyncio
import hashlib
import time

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


async def fetch_price() -> int:
    await asyncio.sleep(0.1)
    return 4_800_000


def heavy_hashing() -> str:
    data = b'x'
    for _ in range(4_000_000):  # about a second of pure CPU work
        data = hashlib.sha256(data).digest()
    return data.hex()[:12]


async def ticker(label: str) -> None:
    """Should print every 0.1 s -- a long gap means the loop was blocked."""
    started = time.perf_counter()
    for _ in range(5):
        print(f'   tick ({label}) at {time.perf_counter() - started:.1f}s')
        await asyncio.sleep(0.1)


async def mistake_1() -> None:
    print('1. forgot await:', fetch_price())  # a coroutine, and a RuntimeWarning later
    print('   with await:  ', await fetch_price())


async def mistake_2_and_4() -> None:
    print('2/4. heavy work directly in async code (ticks stop):')
    started = time.perf_counter()
    await asyncio.gather(ticker('blocked'), asyncio.sleep(0), _run_blocking())
    print(f'   took {time.perf_counter() - started:.2f}s')
    print('     the same work in a thread (ticks continue):')
    started = time.perf_counter()
    await asyncio.gather(ticker('free'), asyncio.to_thread(heavy_hashing))
    print(f'   took {time.perf_counter() - started:.2f}s')


async def _run_blocking() -> None:
    heavy_hashing()  # no await inside: the loop can not switch away


async def mistake_3() -> None:
    engine = create_async_engine('sqlite+aiosqlite:///:memory:')
    SessionLocal = async_sessionmaker(engine)
    async with SessionLocal() as shared:
        # return_exceptions=True: let every task finish, then look at the failures
        results = await asyncio.gather(
            *(shared.execute(text('select 1')) for _ in range(5)), return_exceptions=True
        )
        errors = {type(r).__name__ for r in results if isinstance(r, Exception)}
        print('3. one session shared by 5 tasks ->', errors or 'no error this time (still unsafe!)')

    async def one_query() -> int:
        async with SessionLocal() as own:  # one session per task
            return (await own.execute(text('select 1'))).scalar_one()

    print('   one session per task ->', await asyncio.gather(*(one_query() for _ in range(5))))
    await engine.dispose()


async def main() -> None:
    await mistake_1()
    await mistake_2_and_4()
    await mistake_3()


if __name__ == '__main__':
    asyncio.run(main())

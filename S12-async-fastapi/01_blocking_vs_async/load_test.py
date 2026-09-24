"""Fire 10 concurrent requests at each endpoint of app.py and time them.

Uses httpx.AsyncClient with an ASGITransport: the app runs in this process,
no server needed.
"""

import asyncio
import time

import httpx

from app import app


async def hammer(client: httpx.AsyncClient, path: str, count: int = 10) -> float:
    started = time.perf_counter()
    await asyncio.gather(*(client.get(path) for _ in range(count)))
    return time.perf_counter() - started


async def main() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url='http://test') as client:
        for path in ['/async-good', '/sync-ok', '/async-bad']:
            print(f'{path:<12} 10 requests took {await hammer(client, path):.1f}s')


if __name__ == '__main__':
    asyncio.run(main())

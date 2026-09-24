"""Many requests at the same time with asyncio.gather -- and a limit.

    sequential:   for id in ids: await client.get(...)          time = sum of all
    concurrent:   await asyncio.gather(*(client.get(...) ...))   time = the slowest one

Be polite: never fire 10 000 requests at once. An `asyncio.Semaphore(5)`
lets at most 5 run at the same time (many APIs block clients that do more).

On a server in the same room (localhost) every request takes a millisecond,
so there is little to gain. The gain appears with real network latency --
that is why this example uses a public API on the internet.
"""

import asyncio
import time

import httpx

BASE_URL = 'https://jsonplaceholder.typicode.com'
IDS = list(range(1, 21))


async def sequential(client: httpx.AsyncClient) -> list[str]:
    return [(await client.get(f'/posts/{i}')).json()['title'] for i in IDS]


async def concurrent(client: httpx.AsyncClient) -> list[str]:
    responses = await asyncio.gather(*(client.get(f'/posts/{i}') for i in IDS))
    return [r.json()['title'] for r in responses]


async def concurrent_limited(client: httpx.AsyncClient, limit: int = 5) -> list[str]:
    semaphore = asyncio.Semaphore(limit)

    async def fetch(post_id: int) -> str:
        async with semaphore:  # wait here if `limit` requests are already running
            return (await client.get(f'/posts/{post_id}')).json()['title']

    return list(await asyncio.gather(*(fetch(i) for i in IDS)))


async def main() -> None:
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=15) as client:
        await client.get('/posts/1')  # warm up the connection
        for job in (sequential, concurrent, concurrent_limited):
            started = time.perf_counter()
            titles = await job(client)
            print(f'{job.__name__:<20} {len(titles)} posts in {time.perf_counter() - started:.2f}s')


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except httpx.TransportError as error:
        print(f'No internet? {error!r}')

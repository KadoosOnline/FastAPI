"""httpx.AsyncClient: the same API as httpx.Client, with `await`.

    async with httpx.AsyncClient(base_url=..., timeout=...) as client:
        response = await client.get('/courses')

Why bother? One async client can have MANY requests in flight at the same
time inside one thread (next example). Inside an async web server (FastAPI!)
it is the only correct way to call another API: a sync client would block
the event loop (session 12).

Needs the session 13 API running (see the session README).
"""

import asyncio

import httpx


async def main() -> None:
    async with httpx.AsyncClient(base_url='http://127.0.0.1:8000', timeout=5) as client:
        page = (await client.get('/courses', params={'sort': 'price'})).json()
        print(f'{page["total"]} courses')
        for course in page['items']:
            print(f'  {course["title"]:<22} {course["price"]:>12,}')

        detail = (await client.get('/courses/3')).json()
        print('course 3 is taught by', detail['instructor']['full_name'])


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except httpx.ConnectError:
        print('Start the session 13 API first.')

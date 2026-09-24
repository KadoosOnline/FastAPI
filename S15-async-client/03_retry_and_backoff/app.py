"""Retrying failed requests -- carefully.

Networks and servers fail for a moment: a timeout, a 503 during a restart.
Trying again after a short pause often succeeds. The rules:
* retry only IDEMPOTENT requests (GET, PUT, DELETE): doing them twice changes
  nothing more. Retrying a POST can enroll a student twice!
* retry only TEMPORARY failures: transport errors, 502, 503, 504 (and 429)
* wait longer each time (exponential backoff): 0.2 s, 0.4 s, 0.8 s ...
* give up after a few attempts
* respect `Retry-After` when the server sends it

A fake flaky server (MockTransport) makes the behaviour visible.
"""

import asyncio
import time

import httpx

IDEMPOTENT = {'GET', 'HEAD', 'OPTIONS', 'PUT', 'DELETE'}
TEMPORARY = {429, 502, 503, 504}


async def request_with_retry(
    client: httpx.AsyncClient, method: str, url: str, *, attempts: int = 4, backoff: float = 0.2
) -> httpx.Response:
    tries = attempts if method in IDEMPOTENT else 1
    for attempt in range(1, tries + 1):
        try:
            response = await client.request(method, url)
            if response.status_code not in TEMPORARY or attempt == tries:
                return response
            wait = float(response.headers.get('Retry-After', backoff * 2 ** (attempt - 1)))
            print(f'   attempt {attempt}: HTTP {response.status_code}, waiting {wait:.1f}s')
        except httpx.TransportError as error:
            if attempt == tries:
                raise
            wait = backoff * 2 ** (attempt - 1)
            print(f'   attempt {attempt}: {type(error).__name__}, waiting {wait:.1f}s')
        await asyncio.sleep(wait)
    raise AssertionError('unreachable')


def flaky_server() -> httpx.MockTransport:
    calls = {'n': 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls['n'] += 1
        if calls['n'] == 1:
            raise httpx.ConnectTimeout('slow network', request=request)
        if calls['n'] == 2:
            return httpx.Response(503, headers={'Retry-After': '0.3'})
        return httpx.Response(200, json={'ok': True, 'after_calls': calls['n']})

    return httpx.MockTransport(handler)


async def main() -> None:
    print('GET on a flaky server:')
    async with httpx.AsyncClient(base_url='http://api.test', transport=flaky_server()) as client:
        started = time.perf_counter()
        response = await request_with_retry(client, 'GET', '/courses')
        took = time.perf_counter() - started
        print(f'   -> {response.status_code} {response.json()} in {took:.1f}s')

    print('POST on a flaky server (no retry!):')
    async with httpx.AsyncClient(base_url='http://api.test', transport=flaky_server()) as client:
        try:
            await request_with_retry(client, 'POST', '/courses/1/enrollments')
        except httpx.TransportError as error:
            print(f'   -> gave up at once: {type(error).__name__}')


if __name__ == '__main__':
    asyncio.run(main())

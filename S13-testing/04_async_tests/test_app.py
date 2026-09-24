"""Async tests with HTTPX: `AsyncClient` + `ASGITransport`.

When the TEST itself must be async (to await database helpers, to run
requests concurrently...), use httpx.AsyncClient pointed at the app:

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url='http://test') as client:
        response = await client.get('/...')

`pytest.mark.anyio` runs the test in an event loop (the AnyIO pytest plugin
comes with FastAPI). The `anyio_backend` fixture picks asyncio.

Note: ASGITransport does not run the lifespan -- see the project's conftest.py.
"""

import asyncio
from collections.abc import AsyncIterator

import httpx
import pytest

from app import app, fetch_seats

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    return 'asyncio'


@pytest.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url='http://test') as async_client:
        yield async_client


async def test_one_request(client: httpx.AsyncClient) -> None:
    response = await client.get('/courses/5/seats')

    assert response.status_code == 200
    assert response.json() == {'course_id': 5, 'seats': 15}


async def test_many_requests_at_once(client: httpx.AsyncClient) -> None:
    responses = await asyncio.gather(*(client.get(f'/courses/{i}/seats') for i in range(20)))

    assert all(r.status_code == 200 for r in responses)
    assert [r.json()['seats'] for r in responses] == [10 + i for i in range(20)]


async def test_a_coroutine_directly() -> None:
    assert await fetch_seats(1) == 11

"""Tests of the async client with a fake server (MockTransport)."""

import asyncio

import httpx
import pytest

from client_app.api_client import (
    ApiUnavailable,
    AuthenticationFailed,
    Conflict,
    ServerError,
    TrainingCenterApi,
)

pytestmark = pytest.mark.anyio
COURSE = {
    'id': 1,
    'title': 'FastAPI',
    'price': 1,
    'capacity': 5,
    'level': 'advanced',
    'instructor_id': 2,
}


@pytest.fixture
def anyio_backend() -> str:
    return 'asyncio'


def api_for(handler, **options) -> TrainingCenterApi:  # type: ignore[no-untyped-def]
    return TrainingCenterApi(
        'http://api.test', transport=httpx.MockTransport(handler), backoff=0, **options
    )


async def test_token_is_stored_and_used() -> None:
    headers: list[str | None] = []

    def handler(request: httpx.Request) -> httpx.Response:
        headers.append(request.headers.get('Authorization'))
        if request.url.path == '/auth/token':
            return httpx.Response(200, json={'access_token': 'xyz', 'expires_in': 1800})
        return httpx.Response(
            200, json={'id': 2, 'email': 't@k.ir', 'full_name': 'Ali', 'role': 'instructor'}
        )

    async with api_for(handler) as api:
        await api.login('t@k.ir', 'pw')
        me = await api.me()

    assert headers == [None, 'Bearer xyz']
    assert me.role == 'instructor'


async def test_all_courses_follows_pages() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        page = int(request.url.params['page'])
        return httpx.Response(
            200, json={'items': [COURSE | {'id': page}], 'total': 3, 'page': page, 'pages': 3}
        )

    async with api_for(handler) as api:
        ids = [course.id async for course in api.all_courses()]

    assert ids == [1, 2, 3]


async def test_students_of_many_runs_concurrently() -> None:
    running = 0
    peak = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal running, peak
        running += 1
        peak = max(peak, running)
        await asyncio.sleep(0.05)
        running -= 1
        return httpx.Response(200, json=[])

    async with api_for(handler) as api:
        result = await api.students_of_many(list(range(10)), limit=4)

    assert list(result) == list(range(10))
    assert peak == 4  # concurrent, but never more than the limit


async def test_get_is_retried_on_503() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls < 3:
            return httpx.Response(503)
        return httpx.Response(200, json=[])

    async with api_for(handler, retries=2) as api:
        assert await api.students(1) == []
    assert calls == 3


async def test_post_is_never_retried() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(503, json={'detail': 'restarting'})

    async with api_for(handler, retries=5) as api:
        with pytest.raises(ServerError):
            await api.create_course(title='X', price=1, capacity=1)
    assert calls == 1


@pytest.mark.parametrize(
    ('status', 'error'), [(401, AuthenticationFailed), (409, Conflict), (500, ServerError)]
)
async def test_error_mapping(status: int, error: type[Exception]) -> None:
    async with api_for(
        lambda request: httpx.Response(status, json={'detail': 'x'}), retries=0
    ) as api:
        with pytest.raises(error):
            await api.me()


async def test_unreachable_server() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError('refused', request=request)

    async with api_for(handler, retries=1) as api:
        with pytest.raises(ApiUnavailable):
            await api.me()

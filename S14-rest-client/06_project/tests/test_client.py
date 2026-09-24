"""Testing a CLIENT: a fake server built with httpx.MockTransport.

No running API, no network: `handler(request)` plays the server. We can make
it answer anything -- including errors and timeouts that are hard to trigger
on a real server.
"""

import json

import httpx
import pytest

from clients import (
    ApiConnectionError,
    AuthenticationFailed,
    ConflictError,
    NotFound,
    PermissionDenied,
    ServerError,
    TrainingCenterClient,
    ValidationFailed,
)

COURSE = {
    'id': 1,
    'title': 'FastAPI',
    'description': '',
    'price': 4_800_000,
    'capacity': 12,
    'level': 'advanced',
    'start_date': None,
    'is_active': True,
    'instructor_id': 2,
    'created_at': '2026-09-24T10:00:00Z',
}
USER = {
    'id': 4,
    'email': 'sara@example.com',
    'full_name': 'Sara',
    'role': 'student',
    'is_active': True,
}


def client_for(handler) -> TrainingCenterClient:  # type: ignore[no-untyped-def]
    return TrainingCenterClient('http://api.test', transport=httpx.MockTransport(handler))


def test_login_stores_the_token_and_sends_it_afterwards() -> None:
    seen: list[str | None] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request.headers.get('Authorization'))
        if request.url.path == '/auth/token':
            assert request.headers['content-type'] == 'application/x-www-form-urlencoded'
            return httpx.Response(
                200, json={'access_token': 'abc', 'token_type': 'bearer', 'expires_in': 60}
            )
        return httpx.Response(200, json=USER)

    with client_for(handler) as api:
        api.login('sara@example.com', 'Password123')
        me = api.me()
        api.logout()

    assert seen == [None, 'Bearer abc']
    assert me.full_name == 'Sara'


def test_iter_courses_walks_every_page() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        page = int(request.url.params['page'])
        items = [COURSE | {'id': page * 10 + i} for i in range(2)] if page <= 3 else []
        return httpx.Response(
            200, json={'items': items, 'total': 6, 'page': page, 'size': 2, 'pages': 3}
        )

    with client_for(handler) as api:
        ids = [course.id for course in api.iter_courses(size=2)]

    assert ids == [10, 11, 20, 21, 30, 31]


def test_query_parameters_leave_out_none() -> None:
    urls: list[httpx.URL] = []

    def handler(request: httpx.Request) -> httpx.Response:
        urls.append(request.url)
        return httpx.Response(200, json={'items': [], 'total': 0, 'page': 1, 'size': 5, 'pages': 0})

    with client_for(handler) as api:
        api.list_courses(size=5, q='python')

    assert dict(urls[0].params) == {'page': '1', 'size': '5', 'q': 'python'}


def test_patch_sends_only_the_changes() -> None:
    bodies: list[dict] = []

    def handler(request: httpx.Request) -> httpx.Response:
        bodies.append(json.loads(request.content))
        return httpx.Response(200, json=COURSE | {'price': 100})

    with client_for(handler) as api:
        course = api.update_course(1, price=100)

    assert bodies == [{'price': 100}]
    assert course.price == 100


@pytest.mark.parametrize(
    ('status', 'error_class'),
    [
        (401, AuthenticationFailed),
        (403, PermissionDenied),
        (404, NotFound),
        (409, ConflictError),
        (422, ValidationFailed),
        (500, ServerError),
        (503, ServerError),
    ],
)
def test_status_codes_become_our_exceptions(status: int, error_class: type[Exception]) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status, json={'detail': 'nope', 'code': 'x'})

    with client_for(handler) as api, pytest.raises(error_class):
        api.get_course(1)


def test_validation_details_are_kept() -> None:
    errors = [{'loc': ['body', 'price'], 'msg': 'Input should be greater than or equal to 0'}]

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(422, json={'detail': errors})

    with client_for(handler) as api, pytest.raises(ValidationFailed) as caught:
        api.create_course(title='Bad', price=-1, capacity=1)

    assert caught.value.errors[0]['loc'] == ['body', 'price']


def test_timeout_and_connection_errors() -> None:
    def slow(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout('too slow', request=request)

    def down(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError('refused', request=request)

    for handler in (slow, down):
        with client_for(handler) as api, pytest.raises(ApiConnectionError):
            api.me()


def test_non_json_error_body() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(502, text='Bad Gateway')

    with client_for(handler) as api, pytest.raises(ServerError) as caught:
        api.list_courses()

    assert caught.value.detail == 'Bad Gateway'

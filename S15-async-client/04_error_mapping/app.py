"""Error mapping and event hooks.

1. Error mapping: turn HTTP answers into exceptions that MEAN something to
   the caller. The table lives in one place:

       401 -> AuthenticationFailed      404 -> NotFound
       403 -> PermissionDenied          409 -> Conflict
       422 -> InvalidData (with the field errors)
       5xx -> ServerError               no answer -> ApiUnavailable

2. Event hooks: functions HTTPX calls for every request / response -- a good
   place for logging, without touching each method.

Runs against a fake server (MockTransport): no network needed.
"""

import asyncio
from typing import Any

import httpx


class ApiError(Exception):
    def __init__(self, status: int, detail: Any) -> None:
        super().__init__(f'{status}: {detail}')
        self.status = status
        self.detail = detail


class AuthenticationFailed(ApiError): ...


class PermissionDenied(ApiError): ...


class NotFound(ApiError): ...


class Conflict(ApiError): ...


class InvalidData(ApiError): ...


class ServerError(ApiError): ...


class ApiUnavailable(Exception): ...


ERRORS: dict[int, type[ApiError]] = {
    401: AuthenticationFailed,
    403: PermissionDenied,
    404: NotFound,
    409: Conflict,
    422: InvalidData,
}


def raise_for_api_error(response: httpx.Response) -> None:
    if response.is_success:
        return
    try:
        detail = response.json().get('detail')
    except ValueError:
        detail = response.text
    error = ERRORS.get(
        response.status_code, ServerError if response.status_code >= 500 else ApiError
    )
    raise error(response.status_code, detail)


async def log_request(request: httpx.Request) -> None:
    print(f'  --> {request.method} {request.url.path}')


async def log_response(response: httpx.Response) -> None:
    print(f'  <-- {response.status_code} {response.request.url.path}')


def fake_api(request: httpx.Request) -> httpx.Response:
    answers = {
        '/courses/1': (200, {'id': 1, 'title': 'FastAPI'}),
        '/courses/2': (404, {'detail': 'Course 2 not found'}),
        '/courses/3/enrollments': (409, {'detail': 'Course is full'}),
        '/admin': (403, {'detail': 'Admins only'}),
        '/broken': (500, {'detail': 'Internal Server Error'}),
    }
    if request.url.path == '/offline':
        raise httpx.ConnectError('refused', request=request)
    status, body = answers.get(request.url.path, (404, {'detail': 'Not found'}))
    return httpx.Response(status, json=body)


async def call(client: httpx.AsyncClient, path: str) -> None:
    try:
        response = await client.get(path)
        raise_for_api_error(response)
        print('      OK', response.json())
    except httpx.TransportError as error:
        print('      ApiUnavailable:', ApiUnavailable(str(error)))
    except ApiError as error:
        print(f'      {type(error).__name__}: {error.detail}')


async def main() -> None:
    async with httpx.AsyncClient(
        base_url='http://api.test',
        transport=httpx.MockTransport(fake_api),
        event_hooks={'request': [log_request], 'response': [log_response]},
    ) as client:
        for path in [
            '/courses/1',
            '/courses/2',
            '/courses/3/enrollments',
            '/admin',
            '/broken',
            '/offline',
        ]:
            await call(client, path)


if __name__ == '__main__':
    asyncio.run(main())

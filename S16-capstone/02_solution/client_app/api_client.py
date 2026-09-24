"""An ASYNC client for the Training Center API (session 15).

Everything of session 14, plus:
* httpx.AsyncClient: many requests in flight at once (`asyncio.gather`)
* authentication STATE: the token is stored after login and sent automatically
* error mapping: HTTP status -> our exceptions, in one function
* retries with exponential backoff -- only for idempotent requests and only for
  temporary failures
"""

import asyncio
from collections.abc import AsyncIterator
from types import TracebackType
from typing import Any, Self

import httpx

from client_app.models import Course, CoursePage, Enrollment, Student, Token, User

IDEMPOTENT = frozenset({'GET', 'HEAD', 'OPTIONS', 'PUT', 'DELETE'})
TEMPORARY = frozenset({502, 503, 504})


# ----- errors ------------------------------------------------------------
class ApiError(Exception):
    def __init__(self, status: int, detail: Any) -> None:
        super().__init__(f'HTTP {status}: {detail}')
        self.status = status
        self.detail = detail


class AuthenticationFailed(ApiError): ...


class PermissionDenied(ApiError): ...


class NotFound(ApiError): ...


class Conflict(ApiError): ...


class InvalidData(ApiError): ...


class ServerError(ApiError): ...


class ApiUnavailable(Exception):
    """No answer at all: the server is down, unreachable or too slow."""


_ERRORS: dict[int, type[ApiError]] = {
    401: AuthenticationFailed,
    403: PermissionDenied,
    404: NotFound,
    409: Conflict,
    422: InvalidData,
}


def _to_error(response: httpx.Response) -> ApiError:
    try:
        detail = response.json().get('detail')
    except ValueError:
        detail = response.text or response.reason_phrase
    status = response.status_code
    return _ERRORS.get(status, ServerError if status >= 500 else ApiError)(status, detail)


# ----- the client --------------------------------------------------------
class TrainingCenterApi:
    def __init__(
        self,
        base_url: str = 'http://127.0.0.1:8000',
        *,
        timeout: float = 10.0,
        retries: int = 2,
        backoff: float = 0.3,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.token: str | None = None
        self.retries = retries
        self.backoff = backoff
        self._http = httpx.AsyncClient(
            base_url=base_url,
            timeout=httpx.Timeout(timeout, connect=3.0),
            headers={'User-Agent': 'training-center-client-app/1.0'},
            transport=transport,
        )

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self._http.aclose()

    async def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        headers = kwargs.pop('headers', {})
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        attempts = 1 + (self.retries if method in IDEMPOTENT else 0)
        for attempt in range(1, attempts + 1):
            try:
                response = await self._http.request(method, path, headers=headers, **kwargs)
            except httpx.TransportError as error:
                if attempt == attempts:
                    raise ApiUnavailable(f'{method} {path}: {error!r}') from error
            else:
                if response.status_code not in TEMPORARY or attempt == attempts:
                    if response.is_error:
                        raise _to_error(response)
                    return response
            await asyncio.sleep(self.backoff * 2 ** (attempt - 1))
        raise AssertionError('unreachable')

    # --- auth ----------------------------------------------------------
    async def login(self, email: str, password: str) -> Token:
        response = await self._request(
            'POST', '/auth/token', data={'username': email, 'password': password}
        )
        token = Token.model_validate(response.json())
        self.token = token.access_token
        return token

    async def me(self) -> User:
        return User.model_validate((await self._request('GET', '/users/me')).json())

    async def update_me(self, full_name: str) -> User:
        response = await self._request('PATCH', '/users/me', json={'full_name': full_name})
        return User.model_validate(response.json())

    async def change_password(self, old_password: str, new_password: str) -> None:
        body = {'old_password': old_password, 'new_password': new_password}
        await self._request('POST', '/users/me/password', json=body)

    async def my_enrollments(self) -> list[Enrollment]:
        response = await self._request('GET', '/users/me/enrollments')
        return [Enrollment.model_validate(item) for item in response.json()]

    async def enroll(self, course_id: int) -> Enrollment:
        response = await self._request('POST', f'/courses/{course_id}/enrollments')
        return Enrollment.model_validate(response.json())

    # --- courses -------------------------------------------------------
    async def courses_page(self, page: int = 1, **filters: Any) -> CoursePage:
        params = {'page': page, **{k: v for k, v in filters.items() if v is not None}}
        return CoursePage.model_validate(
            (await self._request('GET', '/courses', params=params)).json()
        )

    async def all_courses(self, **filters: Any) -> AsyncIterator[Course]:
        """An async generator over every page."""
        page = 1
        while True:
            result = await self.courses_page(page, **filters)
            for course in result.items:
                yield course
            if page >= result.pages:
                return
            page += 1

    async def create_course(self, **fields: Any) -> Course:
        return Course.model_validate((await self._request('POST', '/courses', json=fields)).json())

    async def update_course(self, course_id: int, **changes: Any) -> Course:
        response = await self._request('PATCH', f'/courses/{course_id}', json=changes)
        return Course.model_validate(response.json())

    async def students(self, course_id: int) -> list[Student]:
        response = await self._request('GET', f'/courses/{course_id}/students')
        return [Student.model_validate(item) for item in response.json()]

    async def students_of_many(
        self, course_ids: list[int], limit: int = 5
    ) -> dict[int, list[Student]]:
        """Fetch the students of several courses concurrently (at most `limit` at a time)."""
        semaphore = asyncio.Semaphore(limit)

        async def one(course_id: int) -> tuple[int, list[Student]]:
            async with semaphore:
                return course_id, await self.students(course_id)

        return dict(await asyncio.gather(*(one(cid) for cid in course_ids)))

"""A synchronous, typed client for the Training Center API.

    with TrainingCenterClient('http://127.0.0.1:8000') as api:
        api.login('sara@example.com', 'Password123')
        for course in api.iter_courses(q='python'):
            print(course.title)

Design:
* ONE httpx.Client (connection pool, base URL, timeout, User-Agent)
* the token is kept inside the client after login(); every request sends it
* every method returns typed models (clients/models.py)
* every failure becomes one of OUR exceptions (clients/errors.py)
"""

from collections.abc import Generator, Iterator
from pathlib import Path
from types import TracebackType
from typing import Any, Self

import httpx

from clients.errors import ApiConnectionError, error_from_response
from clients.models import Course, Enrollment, Material, Page, Token, User

DEFAULT_TIMEOUT = httpx.Timeout(10.0, connect=3.0)


class _BearerAuth(httpx.Auth):
    """Adds `Authorization: Bearer ...` while the client holds a token."""

    def __init__(self, client: 'TrainingCenterClient') -> None:
        self._client = client

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response, None]:
        if self._client.token:
            request.headers['Authorization'] = f'Bearer {self._client.token}'
        yield request


def _drop_none(values: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in values.items() if value is not None}


class TrainingCenterClient:
    def __init__(
        self,
        base_url: str = 'http://127.0.0.1:8000',
        *,
        timeout: httpx.Timeout | float = DEFAULT_TIMEOUT,
        token: str | None = None,
        transport: httpx.BaseTransport | None = None,  # tests pass a MockTransport here
    ) -> None:
        self.token = token
        self._http = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            auth=_BearerAuth(self),
            headers={'User-Agent': 'training-center-client/1.0', 'Accept': 'application/json'},
            transport=transport,
        )

    # --- lifecycle -----------------------------------------------------
    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def close(self) -> None:
        self._http.close()

    # --- one place for sending and error handling ------------------------
    def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        try:
            response = self._http.request(method, path, **kwargs)
        except httpx.TimeoutException as error:
            raise ApiConnectionError(f'{method} {path} timed out') from error
        except httpx.TransportError as error:
            raise ApiConnectionError(f'{method} {path} failed: {error}') from error
        if response.is_error:
            raise error_from_response(response)
        return response

    # --- authentication ------------------------------------------------
    def register(self, email: str, full_name: str, password: str) -> User:
        body = {'email': email, 'full_name': full_name, 'password': password}
        return User.model_validate(self._request('POST', '/auth/register', json=body).json())

    def login(self, email: str, password: str) -> Token:
        """OAuth2 password flow: a FORM, not JSON. The token is kept for later calls."""
        response = self._request(
            'POST', '/auth/token', data={'username': email, 'password': password}
        )
        token = Token.model_validate(response.json())
        self.token = token.access_token
        return token

    def logout(self) -> None:
        """JWTs live on the client: logging out = forgetting the token."""
        self.token = None

    def me(self) -> User:
        return User.model_validate(self._request('GET', '/users/me').json())

    # --- courses -------------------------------------------------------
    def list_courses(
        self,
        *,
        page: int = 1,
        size: int = 20,
        q: str | None = None,
        level: str | None = None,
        min_price: int | None = None,
        max_price: int | None = None,
        sort: str | None = None,
    ) -> Page[Course]:
        params = _drop_none(
            {
                'page': page,
                'size': size,
                'q': q,
                'level': level,
                'min_price': min_price,
                'max_price': max_price,
                'sort': sort,
            }
        )
        return Page[Course].model_validate(self._request('GET', '/courses', params=params).json())

    def iter_courses(self, *, size: int = 50, **filters: Any) -> Iterator[Course]:
        """A generator over EVERY page: callers never think about pagination."""
        page = 1
        while True:
            result = self.list_courses(page=page, size=size, **filters)
            yield from result.items
            if page >= result.pages:
                return
            page += 1

    def get_course(self, course_id: int) -> Course:
        return Course.model_validate(self._request('GET', f'/courses/{course_id}').json())

    def create_course(
        self,
        *,
        title: str,
        price: int,
        capacity: int,
        description: str = '',
        level: str = 'beginner',
        instructor_id: int | None = None,
    ) -> Course:
        body = _drop_none(
            {
                'title': title,
                'price': price,
                'capacity': capacity,
                'description': description,
                'level': level,
                'instructor_id': instructor_id,
            }
        )
        return Course.model_validate(self._request('POST', '/courses', json=body).json())

    def update_course(self, course_id: int, **changes: Any) -> Course:
        """PATCH: only the given fields, e.g. update_course(3, price=100)."""
        response = self._request('PATCH', f'/courses/{course_id}', json=changes)
        return Course.model_validate(response.json())

    def replace_course(self, course_id: int, course: dict[str, Any]) -> Course:
        """PUT: the complete new state of the course."""
        response = self._request('PUT', f'/courses/{course_id}', json=course)
        return Course.model_validate(response.json())

    def delete_course(self, course_id: int) -> None:
        self._request('DELETE', f'/courses/{course_id}')

    # --- enrollments ---------------------------------------------------
    def enroll(self, course_id: int) -> Enrollment:
        response = self._request('POST', f'/courses/{course_id}/enrollments')
        return Enrollment.model_validate(response.json())

    def cancel_enrollment(self, course_id: int) -> None:
        self._request('DELETE', f'/courses/{course_id}/enrollments/me')

    def my_enrollments(self) -> list[Enrollment]:
        return [
            Enrollment.model_validate(e)
            for e in self._request('GET', '/users/me/enrollments').json()
        ]

    # --- materials -----------------------------------------------------
    def upload_material(
        self, course_id: int, path: Path, *, title: str, content_type: str
    ) -> Material:
        with path.open('rb') as file:
            response = self._request(
                'POST',
                f'/courses/{course_id}/materials',
                data={'title': title},
                files={'file': (path.name, file, content_type)},
            )
        return Material.model_validate(response.json())

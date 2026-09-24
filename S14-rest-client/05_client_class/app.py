"""From loose requests to a reusable CLIENT CLASS.

Scripts full of `httpx.get(f'{API}/courses/{id}')` repeat the base URL, the
headers, the error checks... everywhere. A client class puts all of that in
one place and offers methods with names from the business:

    api = CoursesClient('http://127.0.0.1:8000')
    api.list_courses(q='python')

and returns typed objects instead of raw dicts. This file shows the first
version; the project turns it into a complete, tested client.

Needs the session 13 API running (see 04_bearer_auth).
"""

from dataclasses import dataclass
from types import TracebackType
from typing import Self

import httpx


@dataclass(frozen=True)
class Course:
    id: int
    title: str
    price: int


class CoursesClient:
    def __init__(self, base_url: str, timeout: float = 5.0) -> None:
        self._http = httpx.Client(base_url=base_url, timeout=timeout)

    # context manager: `with CoursesClient(...) as api:` closes the connections
    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc: type[BaseException] | BaseException | TracebackType | None) -> None:
        self._http.close()

    def list_courses(self, q: str | None = None) -> list[Course]:
        params = {'q': q} if q else {}
        response = self._http.get('/courses', params=params)
        response.raise_for_status()
        return [Course(c['id'], c['title'], c['price']) for c in response.json()['items']]

    def get_course(self, course_id: int) -> Course | None:
        response = self._http.get(f'/courses/{course_id}')
        if response.status_code == 404:
            return None
        response.raise_for_status()
        data = response.json()
        return Course(data['id'], data['title'], data['price'])


def main() -> None:
    with CoursesClient('http://127.0.0.1:8000') as api:
        for course in api.list_courses(q='python'):
            print(course)
        print(api.get_course(3))
        print(api.get_course(999))


if __name__ == '__main__':
    try:
        main()
    except httpx.ConnectError:
        print('Start the session 13 API first (see 04_bearer_auth).')

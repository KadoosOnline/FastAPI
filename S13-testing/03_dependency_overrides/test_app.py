"""`app.dependency_overrides`: swap a dependency for a fake one in tests.

    app.dependency_overrides[get_db] = lambda: FakeDatabase()
    app.dependency_overrides[get_current_user] = lambda: {'email': ..., 'role': 'student'}

Every endpoint that depends on `get_db` now receives the fake. This is
dependency injection paying off: the endpoint code does not change, only
what we inject. ALWAYS clear the overrides after the test.
"""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app import app, get_current_user, get_db


class FakeDatabase:
    def list_courses(self) -> list[str]:
        return ['Python', 'FastAPI']


@pytest.fixture
def client() -> Iterator[TestClient]:
    app.dependency_overrides[get_db] = FakeDatabase
    yield TestClient(app)
    app.dependency_overrides.clear()


def login_as(role: str) -> None:
    app.dependency_overrides[get_current_user] = lambda: {'email': f'{role}@x.com', 'role': role}


def test_student_sees_their_courses(client: TestClient) -> None:
    login_as('student')

    response = client.get('/my-courses')

    assert response.status_code == 200
    assert response.json() == {'user': 'student@x.com', 'courses': ['Python', 'FastAPI']}


def test_instructor_is_forbidden(client: TestClient) -> None:
    login_as('instructor')

    assert client.get('/my-courses').status_code == 403


def test_without_override_the_real_auth_runs(client: TestClient) -> None:
    assert client.get('/my-courses').status_code == 401

"""Testing an API with FastAPI's TestClient.

`TestClient(app)` sends real HTTP requests to the app IN THIS PROCESS -- no
server, no network. It has the same API as an HTTPX client:
    client.get(url, params=...)   client.post(url, json=... / data=... / files=...)
    response.status_code          response.json()          response.headers

Always check BOTH the status code and the body. Test failures on purpose:
invalid data (422), missing things (404).
"""

import pytest
from fastapi.testclient import TestClient

from app import COURSES, app


@pytest.fixture
def client() -> TestClient:
    COURSES.clear()  # every test starts with an empty "database"
    return TestClient(app)


def test_create_course(client: TestClient) -> None:
    response = client.post('/courses', json={'title': 'FastAPI', 'price': 4_800_000})

    assert response.status_code == 201
    assert response.json() == {'id': 1, 'title': 'FastAPI', 'price': 4_800_000}


def test_read_back_what_was_created(client: TestClient) -> None:
    created = client.post('/courses', json={'title': 'FastAPI', 'price': 1}).json()

    response = client.get(f'/courses/{created["id"]}')

    assert response.status_code == 200
    assert response.json()['title'] == 'FastAPI'


def test_missing_course_is_404(client: TestClient) -> None:
    response = client.get('/courses/999')

    assert response.status_code == 404
    assert response.json() == {'detail': 'Course not found'}


@pytest.mark.parametrize(
    ('body', 'bad_field'),
    [
        ({'title': 'ab', 'price': 1}, 'title'),
        ({'title': 'FastAPI', 'price': -5}, 'price'),
        ({'title': 'FastAPI'}, 'price'),
    ],
)
def test_validation_errors(client: TestClient, body: dict, bad_field: str) -> None:
    response = client.post('/courses', json=body)

    assert response.status_code == 422
    assert response.json()['detail'][0]['loc'] == ['body', bad_field]


def test_wrong_path_type_is_422(client: TestClient) -> None:
    assert client.get('/courses/abc').status_code == 422

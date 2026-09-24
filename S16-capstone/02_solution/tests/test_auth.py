import pytest
from httpx import AsyncClient

from tests.conftest import PASSWORD, UserFactory

pytestmark = pytest.mark.anyio


async def test_register_creates_a_student(client: AsyncClient) -> None:
    response = await client.post(
        '/auth/register',
        json={
            'email': 'New@Example.com',
            'full_name': 'New One',
            'password': 'Secret2026',
            'role': 'admin',
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body['email'] == 'new@example.com'
    assert body['role'] == 'student'  # the role in the request was ignored
    assert 'hashed_password' not in body


async def test_register_duplicate_email(client: AsyncClient, make_user: UserFactory) -> None:
    await make_user(email='taken@example.com')

    response = await client.post(
        '/auth/register',
        json={'email': 'TAKEN@example.com', 'full_name': 'Copy', 'password': 'Secret2026'},
    )

    assert response.status_code == 409


@pytest.mark.parametrize(
    ('field', 'value'),
    [
        ('email', 'not-an-email'),
        ('password', 'short1'),
        ('password', 'onlyletters'),
        ('full_name', 'A'),
    ],
)
async def test_register_validation(client: AsyncClient, field: str, value: str) -> None:
    body = {
        'email': 'ok@example.com',
        'full_name': 'Valid Name',
        'password': 'Secret2026',
        field: value,
    }

    response = await client.post('/auth/register', json=body)

    assert response.status_code == 422
    assert response.json()['detail'][0]['loc'] == ['body', field]


async def test_login_returns_a_bearer_token(client: AsyncClient, make_user: UserFactory) -> None:
    await make_user(email='sara@example.com')

    response = await client.post(
        '/auth/token', data={'username': 'sara@example.com', 'password': PASSWORD}
    )

    assert response.status_code == 200
    assert response.json()['token_type'] == 'bearer'
    assert response.json()['access_token'].count('.') == 2


@pytest.mark.parametrize(
    ('username', 'password'),
    [('sara@example.com', 'WrongPass1'), ('nobody@example.com', PASSWORD)],
    ids=['wrong-password', 'unknown-user'],
)
async def test_login_failures_look_the_same(
    client: AsyncClient, make_user: UserFactory, username: str, password: str
) -> None:
    await make_user(email='sara@example.com')

    response = await client.post('/auth/token', data={'username': username, 'password': password})

    assert response.status_code == 401
    assert response.json()['detail'] == 'Incorrect email or password'
    assert response.headers['www-authenticate'] == 'Bearer'


async def test_disabled_user_can_not_log_in(client: AsyncClient, make_user: UserFactory) -> None:
    await make_user(email='off@example.com', is_active=False)

    response = await client.post(
        '/auth/token', data={'username': 'off@example.com', 'password': PASSWORD}
    )

    assert response.status_code == 403


async def test_full_flow_login_then_me(client: AsyncClient, make_user: UserFactory) -> None:
    await make_user('instructor', email='ali@kadoos.ir')
    login = await client.post(
        '/auth/token', data={'username': 'ali@kadoos.ir', 'password': PASSWORD}
    )
    headers = {'Authorization': f'Bearer {login.json()["access_token"]}'}

    response = await client.get('/users/me', headers=headers)

    assert response.status_code == 200
    assert response.json()['role'] == 'instructor'


@pytest.mark.parametrize('header', [None, 'Bearer not-a-jwt', 'Basic abc'])
async def test_me_rejects_missing_or_bad_tokens(client: AsyncClient, header: str | None) -> None:
    headers = {'Authorization': header} if header else {}

    assert (await client.get('/users/me', headers=headers)).status_code == 401

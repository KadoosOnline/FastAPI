"""Log in to OUR API and use the token: the Bearer flow from the client side.

Start the session 13 project first (another terminal):
    cd ../../S13-testing/05_project
    alembic upgrade head && python seed.py && python main.py

Then:
    python app.py

    1. POST /auth/token with a FORM (username, password)  -> access_token
    2. send `Authorization: Bearer <token>` with every protected request

Two ways to send the header: by hand in `headers=`, or once for the whole
client with a small `httpx.Auth` class (used in the project).
"""

import httpx

API = 'http://127.0.0.1:8000'


class BearerAuth(httpx.Auth):
    """Adds the Authorization header to every request of a client."""

    def __init__(self, token: str) -> None:
        self.token = token

    def auth_flow(self, request: httpx.Request):  # type: ignore[no-untyped-def]
        request.headers['Authorization'] = f'Bearer {self.token}'
        yield request


def main() -> None:
    with httpx.Client(base_url=API, timeout=5) as client:
        print('without token:', client.get('/users/me').status_code)

        login = client.post(
            '/auth/token', data={'username': 'sara@example.com', 'password': 'Password123'}
        )
        login.raise_for_status()
        token = login.json()['access_token']
        print('token starts with', token[:20], '...')

        me = client.get('/users/me', headers={'Authorization': f'Bearer {token}'})
        print('by hand      :', me.json()['full_name'])

    with httpx.Client(base_url=API, timeout=5, auth=BearerAuth(token)) as client:
        print('with Auth    :', client.get('/users/me').json()['email'])
        print(
            'my courses   :',
            [e['course']['title'] for e in client.get('/users/me/enrollments').json()],
        )


if __name__ == '__main__':
    try:
        main()
    except httpx.ConnectError:
        print('Start the session 13 API first (see the docstring).')

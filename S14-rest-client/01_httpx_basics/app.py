"""HTTPX basics: the five methods from the CLIENT side.

Until now we built the server. A client is any program that sends requests:
a browser, a mobile app, Bruno -- or a Python script. HTTPX is to the client
what FastAPI is to the server.

    httpx.get(url)                          one-off request (opens and closes a connection)
    with httpx.Client(base_url=...) as c:   a session: connection pool, shared settings
        c.get('/posts/1')

requests vs httpx: almost the same API (`requests.get` <-> `httpx.get`).
HTTPX adds an async client (session 15), HTTP/2, and timeouts by default
(requests waits for ever unless you pass `timeout=`).

Needs internet: https://jsonplaceholder.typicode.com is a free fake REST API.
"""

import httpx

BASE_URL = 'https://jsonplaceholder.typicode.com'


def main() -> None:
    with httpx.Client(base_url=BASE_URL, timeout=10) as client:
        response = client.get('/posts/1')
        print('GET    ', response.status_code, response.json()['title'][:40])

        response = client.post('/posts', json={'title': 'FastAPI', 'body': 'course', 'userId': 1})
        print('POST   ', response.status_code, response.json())

        response = client.put('/posts/1', json={'id': 1, 'title': 'new', 'body': 'b', 'userId': 1})
        print('PUT    ', response.status_code, response.json()['title'])

        response = client.patch('/posts/1', json={'title': 'only the title'})
        print('PATCH  ', response.status_code, response.json()['title'])

        response = client.delete('/posts/1')
        print('DELETE ', response.status_code)


if __name__ == '__main__':
    try:
        main()
    except httpx.TransportError as error:
        print(f'No internet? {error!r}')

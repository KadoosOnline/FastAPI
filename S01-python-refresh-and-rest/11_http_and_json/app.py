"""HTTP, REST and JSON: talking to a real web API with HTTPX.

The client/server model: a CLIENT sends a REQUEST, a SERVER sends back a
RESPONSE. A request has:
    a method    GET (read), POST (create), PUT (replace), PATCH (change), DELETE
    a URL       https://jsonplaceholder.typicode.com/posts/1
    headers     Accept: application/json, Authorization: Bearer ...
    a body      (for POST/PUT/PATCH) usually JSON

A response has a STATUS CODE, headers and a body:
    2xx it worked          200 OK, 201 Created, 204 No Content
    4xx YOUR mistake       400, 401 not logged in, 403 not allowed,
                           404 not found, 409 conflict, 422 invalid data
    5xx the SERVER's fault 500, 502, 503

REST = resources (nouns) in the URL, actions in the method:
    GET    /posts        list       POST   /posts      create
    GET    /posts/1      one        PATCH  /posts/1    change part
    PUT    /posts/1      replace    DELETE /posts/1    remove

JSON is the text format of the body: `json.dumps(dict) -> str` and
`json.loads(str) -> dict`. HTTPX does both for us (`json=...`, `.json()`).

Why HTTPX and not `requests`? Same friendly API, plus async support and
timeouts everywhere. FastAPI's test client is built on it too.

    pip install -r ../requirements.txt
    python app.py          (needs internet)
"""

import json
from dataclasses import dataclass
from typing import Any

import httpx

BASE_URL = 'https://jsonplaceholder.typicode.com'


@dataclass(frozen=True)
class Post:
    id: int
    title: str

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> 'Post':
        return cls(id=data['id'], title=data['title'])


def main() -> None:
    # JSON is just text:
    text = json.dumps({'title': 'FastAPI', 'price': 4_800_000, 'tags': ['web']})
    print(text, '->', json.loads(text)['price'])

    # One Client = one connection pool, reused for every request.
    with httpx.Client(base_url=BASE_URL, timeout=5.0) as client:
        response = client.get('/posts', params={'userId': 1})
        print(response.request.method, response.request.url)
        print(response.status_code, response.headers['content-type'])
        posts = [Post.from_json(item) for item in response.json()]
        print(f'{len(posts)} posts, first: {posts[0].title!r}')

        created = client.post('/posts', json={'title': 'Hello', 'body': '...', 'userId': 1})
        print('POST ->', created.status_code, created.json())

        missing = client.get('/posts/999999')
        print('GET missing ->', missing.status_code)

        try:
            missing.raise_for_status()
        except httpx.HTTPStatusError as error:
            print('raise_for_status():', error.response.status_code)

    try:
        httpx.get(f'{BASE_URL}/posts', timeout=0.001)
    except httpx.TimeoutException:
        print('timeout: never wait for ever')


if __name__ == '__main__':
    try:
        main()
    except httpx.TransportError as error:
        print(f'No internet connection? ({error!r})')

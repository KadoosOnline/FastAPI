"""Query parameters, headers, JSON in and out, and reading a response.

    client.get('/comments', params={'postId': 1})    -> /comments?postId=1 (escaped for you)
    client.get(..., headers={'Accept-Language': 'fa'})
    client.post(..., json={...})                      -> body + Content-Type: application/json
    client.post(..., data={...})                      -> an HTML form (like /auth/token)

    response.status_code, response.headers, response.json(), response.text,
    response.request.url, response.elapsed

Needs internet.
"""

import httpx


def main() -> None:
    with httpx.Client(
        base_url='https://jsonplaceholder.typicode.com',
        headers={'User-Agent': 'kadoos-course-client/1.0'},  # sent with EVERY request
        timeout=10,
    ) as client:
        response = client.get('/comments', params={'postId': 1, '_limit': 3})
        print(response.request.url)
        print(response.status_code, response.headers['content-type'])
        print(f'took {response.elapsed.total_seconds() * 1000:.0f} ms')
        for comment in response.json():
            print(' -', comment['email'])

        response = client.post('/posts', json={'title': 'Hello', 'body': 'from httpx', 'userId': 7})
        print(response.request.headers['content-type'], '->', response.json())

        form = client.post('/posts', data={'title': 'as a form'})
        print(form.request.headers['content-type'])


if __name__ == '__main__':
    try:
        main()
    except httpx.TransportError as error:
        print(f'No internet? {error!r}')

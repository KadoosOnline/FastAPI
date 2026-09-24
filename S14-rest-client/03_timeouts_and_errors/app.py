"""Timeouts and errors: a client must expect failure.

Two very different kinds of failure:
1. NO answer at all -> an exception from HTTPX
       httpx.ConnectError       server down / wrong address
       httpx.TimeoutException   server too slow (ConnectTimeout, ReadTimeout...)
   Both are subclasses of httpx.TransportError.
2. An answer with an ERROR status (4xx, 5xx) -> NOT an exception by default!
       check `response.is_success`, or call `response.raise_for_status()`
       which raises httpx.HTTPStatusError

A good client turns all of this into ITS OWN exceptions (session 14 project):
callers catch `NotFound` or `ApiUnavailable`, never raw HTTPX details.

`httpx.MockTransport` returns fake responses, so this example needs no
server and no internet -- the same trick our tests use.
"""

import httpx


def fake_server(request: httpx.Request) -> httpx.Response:
    if request.url.path == '/slow':
        raise httpx.ReadTimeout('the server did not answer in time', request=request)
    if request.url.path == '/down':
        raise httpx.ConnectError('connection refused', request=request)
    if request.url.path == '/courses/1':
        return httpx.Response(200, json={'id': 1, 'title': 'FastAPI'})
    if request.url.path == '/broken':
        return httpx.Response(500, text='Internal Server Error')
    return httpx.Response(404, json={'detail': 'Not found'})


def fetch(client: httpx.Client, path: str) -> None:
    try:
        response = client.get(path)
        response.raise_for_status()
    except httpx.TimeoutException:
        print(f'{path:<12} timeout        -> try again later')
    except httpx.ConnectError:
        print(f'{path:<12} no connection  -> is the server running?')
    except httpx.HTTPStatusError as error:
        status = error.response.status_code
        kind = 'our mistake (4xx)' if status < 500 else 'server problem (5xx)'
        print(f'{path:<12} HTTP {status}       -> {kind}')
    else:
        print(f'{path:<12} OK             -> {response.json()}')


def main() -> None:
    timeout = httpx.Timeout(5.0, connect=2.0)  # 2 s to connect, 5 s for the rest
    with httpx.Client(
        base_url='http://api.test', transport=httpx.MockTransport(fake_server), timeout=timeout
    ) as client:
        for path in ['/courses/1', '/courses/99', '/broken', '/slow', '/down']:
            fetch(client, path)


if __name__ == '__main__':
    main()

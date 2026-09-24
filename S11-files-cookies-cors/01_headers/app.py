"""Headers: extra information around a request or a response.

Reading request headers:
    user_agent: Annotated[str | None, Header()] = None      # "User-Agent"
    x_request_id: Annotated[str | None, Header()] = None    # "X-Request-ID"
Python names use underscores; FastAPI converts them to dashes.

Setting response headers:
    * in one endpoint: declare `response: Response` and set `response.headers[...]`
    * for EVERY response: a middleware (runs around every request)

Typical real-world headers: Authorization, Content-Type, Accept-Language,
X-Request-ID (to follow one request through the logs), Cache-Control,
X-Process-Time.
"""

import time
import uuid
from collections.abc import Awaitable, Callable
from typing import Annotated

import uvicorn
from fastapi import FastAPI, Header, Request, Response

app = FastAPI()


@app.middleware('http')
async def add_timing_and_request_id(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    started = time.perf_counter()
    request_id = request.headers.get('x-request-id') or uuid.uuid4().hex[:12]
    response = await call_next(request)
    response.headers['X-Request-ID'] = request_id
    response.headers['X-Process-Time'] = f'{(time.perf_counter() - started) * 1000:.1f}ms'
    return response


GREETINGS = {'fa': 'Salam', 'en': 'Hello', 'de': 'Hallo'}


@app.get('/hello')
def hello(accept_language: Annotated[str | None, Header()] = None) -> dict[str, str]:
    language = (accept_language or 'en')[:2]
    return {'greeting': GREETINGS.get(language, GREETINGS['en']), 'language': language}


@app.get('/client')
def client_info(
    user_agent: Annotated[str | None, Header()] = None,
    x_forwarded_for: Annotated[str | None, Header()] = None,
) -> dict[str, str | None]:
    return {'user_agent': user_agent, 'x_forwarded_for': x_forwarded_for}


@app.get('/courses')
def courses(response: Response) -> list[str]:
    response.headers['Cache-Control'] = 'public, max-age=60'  # browsers may keep it 60 s
    return ['Python', 'FastAPI']


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)

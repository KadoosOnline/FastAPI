"""Lifespan: code that runs once at start-up and once at shutdown.

    @asynccontextmanager
    async def lifespan(app):
        ... create shared resources ...     # start-up
        yield
        ... close them ...                  # shutdown

    app = FastAPI(lifespan=lifespan)

Shared, expensive resources belong here: the database engine (its
connection pool), ONE httpx.AsyncClient reused by every request, caches...
Store them on `app.state` and reach them from a dependency via `request.app`.

Watch the console: "starting" once, "stopping" when you press Ctrl-C.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

import httpx
import uvicorn
from fastapi import Depends, FastAPI, Request


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    print('starting: opening one shared HTTP client')
    app.state.http = httpx.AsyncClient(base_url='https://jsonplaceholder.typicode.com', timeout=5)
    app.state.visits = 0
    yield
    print('stopping: closing it')
    await app.state.http.aclose()


app = FastAPI(lifespan=lifespan)


def get_http(request: Request) -> httpx.AsyncClient:
    return request.app.state.http


@app.get('/users/{user_id}/todos')
async def todos(user_id: int, http: Annotated[httpx.AsyncClient, Depends(get_http)]) -> dict:
    try:
        response = await http.get('/todos', params={'userId': user_id})
        response.raise_for_status()
    except httpx.HTTPError as error:
        return {'error': f'upstream API failed: {error!r}'}
    items = response.json()
    return {'user_id': user_id, 'done': sum(t['completed'] for t in items), 'total': len(items)}


@app.get('/visits')
async def visits(request: Request) -> dict[str, int]:
    request.app.state.visits += 1
    return {'visits': request.app.state.visits}


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)

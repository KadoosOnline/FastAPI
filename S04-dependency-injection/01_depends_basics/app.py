"""Dependency Injection: "FastAPI, please prepare this for me".

Two endpoints need the same pagination parameters. Instead of copying them,
we write ONE function and declare it as a dependency:

    def list_courses(page: dict = Depends(pagination)): ...

On every request FastAPI calls `pagination(...)` first -- reading its
parameters from the query string -- and passes the result to our endpoint.

A dependency is just a function (a higher-order idea from session 1: we hand
FastAPI a function, FastAPI decides when to call it). It can declare its own
query/path/header parameters, and those appear in /docs as if they belonged
to the endpoint.
"""

import uvicorn
from fastapi import Depends, FastAPI

app = FastAPI()

COURSES = [f'Course {n}' for n in range(1, 31)]
USERS = [f'user{n}@example.com' for n in range(1, 13)]


def pagination(page: int = 1, size: int = 10) -> dict[str, int]:
    size = min(size, 50)  # never more than 50 per page
    return {'offset': (page - 1) * size, 'limit': size}


@app.get('/courses')
def list_courses(paging: dict[str, int] = Depends(pagination)) -> list[str]:
    start = paging['offset']
    return COURSES[start : start + paging['limit']]


@app.get('/users')
def list_users(paging: dict[str, int] = Depends(pagination)) -> list[str]:
    start = paging['offset']
    return USERS[start : start + paging['limit']]


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)

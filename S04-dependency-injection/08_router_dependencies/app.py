"""Dependencies for a whole router, or for the whole app.

Some checks must run for MANY endpoints, and the endpoints do not need the
result: "is there a valid API key?", "log this request".

    admin = APIRouter(prefix='/admin', dependencies=[Depends(require_api_key)])
    app = FastAPI(dependencies=[Depends(log_request)])

Every endpoint of the `admin` router is now protected -- you can not forget it
on a new endpoint.
"""

from typing import Annotated

import uvicorn
from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Request


def log_request(request: Request) -> None:
    print(f'--> {request.method} {request.url.path}')


def require_api_key(x_api_key: Annotated[str | None, Header()] = None) -> None:
    if x_api_key != 'secret-admin-key':
        raise HTTPException(401, detail='Admin API key required')


app = FastAPI(dependencies=[Depends(log_request)])
public = APIRouter(prefix='/courses', tags=['public'])
admin = APIRouter(prefix='/admin', tags=['admin'], dependencies=[Depends(require_api_key)])


@public.get('')
def list_courses() -> list[str]:
    return ['Python', 'FastAPI']


@admin.get('/stats')
def stats() -> dict[str, int]:
    return {'users': 120, 'courses': 14}


@admin.delete('/cache')
def clear_cache() -> dict[str, str]:
    return {'cache': 'cleared'}


app.include_router(public)
app.include_router(admin)


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)

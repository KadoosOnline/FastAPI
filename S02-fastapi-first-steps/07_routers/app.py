"""Routers: split a growing API into files.

One file with 30 endpoints is hard to read. An `APIRouter` is a "mini app"
that holds the endpoints of ONE resource:

    routers/courses.py   router = APIRouter(prefix='/courses', tags=['courses'])
    routers/users.py     router = APIRouter(prefix='/users', tags=['users'])

`app.include_router(...)` plugs them into the main app. `prefix` is added in
front of every path, and `tags` groups the endpoints in /docs.

    python app.py      then look at /docs: two groups
"""

import uvicorn
from fastapi import FastAPI

from routers import courses, users

app = FastAPI(title='Training Center API')
app.include_router(courses.router)
app.include_router(users.router)


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)

"""Reading headers and cookies, and a first "authentication" dependency.

    user_agent: Annotated[str | None, Header()] = None
        reads the `User-Agent` header (underscores become dashes)
    theme: Annotated[str | None, Cookie()] = None
        reads the `theme` cookie that the browser sends back

`response.set_cookie(...)` asks the client to store a cookie.

The API-key dependency is the *concept* of authentication: a dependency that
reads a header and either returns "who is calling" or stops the request with
401. Sessions 9 and 10 replace the fixed key with real users and JWT tokens,
but the shape stays the same.
"""

from typing import Annotated

import uvicorn
from fastapi import Cookie, Depends, FastAPI, Header, HTTPException, Response, status

app = FastAPI()

API_KEYS = {'secret-admin-key': 'admin', 'secret-teacher-key': 'teacher'}


@app.get('/whoami')
def whoami(
    user_agent: Annotated[str | None, Header()] = None,
    accept_language: Annotated[str | None, Header()] = None,
) -> dict[str, str | None]:
    return {'user_agent': user_agent, 'language': accept_language}


@app.post('/preferences/theme/{theme}')
def set_theme(theme: str, response: Response) -> dict[str, str]:
    response.set_cookie('theme', theme, max_age=3600, httponly=True, samesite='lax')
    return {'saved': theme}


@app.get('/preferences')
def get_preferences(theme: Annotated[str | None, Cookie()] = None) -> dict[str, str]:
    return {'theme': theme or 'light (default)'}


def get_caller(x_api_key: Annotated[str | None, Header()] = None) -> str:
    if x_api_key not in API_KEYS:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail='Missing or invalid X-API-Key header'
        )
    return API_KEYS[x_api_key]


@app.delete('/courses/{course_id}')
def delete_course(course_id: int, caller: Annotated[str, Depends(get_caller)]) -> dict:
    return {'deleted': course_id, 'by': caller}


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)

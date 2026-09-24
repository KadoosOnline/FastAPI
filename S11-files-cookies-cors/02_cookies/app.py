"""Cookies: small values the BROWSER stores and sends back automatically.

    response.set_cookie('key', 'value', max_age=..., httponly=True, samesite='lax', secure=True)
    value: Annotated[str | None, Cookie()] = None
    response.delete_cookie('key')

Options that matter:
    httponly=True   JavaScript can not read it (protects against XSS stealing it)
    secure=True     only sent over HTTPS (turn off only on localhost)
    samesite='lax'  not sent with cross-site POSTs (protects against CSRF)
    max_age         seconds until it expires; without it: until the browser closes

Here: a "recently viewed courses" list kept in a cookie -- no login needed.
Cookies vs Bearer tokens: browsers send cookies automatically (convenient,
but needs CSRF care); mobile apps and scripts usually send Bearer tokens.
"""

from typing import Annotated

import uvicorn
from fastapi import Cookie, FastAPI, Response

app = FastAPI()
COURSES = {1: 'Python', 2: 'FastAPI', 3: 'SQL', 4: 'Git'}


@app.get('/courses/{course_id}')
def view_course(
    course_id: int, response: Response, recent: Annotated[str | None, Cookie()] = None
) -> dict:
    ids = [int(x) for x in recent.split('-') if x.isdigit()] if recent else []
    ids = [course_id] + [x for x in ids if x != course_id]
    response.set_cookie(
        'recent', '-'.join(map(str, ids[:3])), max_age=7 * 24 * 3600, httponly=True, samesite='lax'
    )
    return {'course': COURSES.get(course_id, '?')}


@app.get('/recently-viewed')
def recently_viewed(recent: Annotated[str | None, Cookie()] = None) -> list[str]:
    if not recent:
        return []
    return [COURSES.get(int(x), '?') for x in recent.split('-') if x.isdigit()]


@app.delete('/recently-viewed')
def forget(response: Response) -> dict[str, str]:
    response.delete_cookie('recent')
    return {'status': 'forgotten'}


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)

"""An app with two dependencies that are awkward in tests:
a "database" and the current user (normally from a JWT)."""

from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException


class Database:
    """Pretend this talks to PostgreSQL."""

    def list_courses(self) -> list[str]:
        raise RuntimeError('no database available in this demo!')


def get_db() -> Database:
    return Database()


def get_current_user(authorization: Annotated[str | None, Header()] = None) -> dict:
    if authorization is None:
        raise HTTPException(401, detail='Not authenticated')
    raise HTTPException(401, detail='Real token checking lives here')


app = FastAPI()


@app.get('/my-courses')
def my_courses(
    db: Annotated[Database, Depends(get_db)], user: Annotated[dict, Depends(get_current_user)]
) -> dict:
    if user['role'] != 'student':
        raise HTTPException(403, detail='Students only')
    return {'user': user['email'], 'courses': db.list_courses()}

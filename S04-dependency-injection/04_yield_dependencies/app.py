"""Dependencies with `yield`: set up, hand over, ALWAYS clean up.

This is a context manager (session 1) in dependency form:

    def get_db():
        db = open_connection()     # before the request
        try:
            yield db               # the endpoint runs here
        finally:
            db.close()             # after the response, even after an error

In session 5 this exact shape gives every request its own database session.
Watch the console: OPEN / CLOSE around every request, ROLLBACK on errors.
"""

from collections.abc import Iterator
from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI, HTTPException


class FakeSession:
    counter = 0

    def __init__(self) -> None:
        FakeSession.counter += 1
        self.number = FakeSession.counter
        print(f'[session {self.number}] OPEN')

    def rollback(self) -> None:
        print(f'[session {self.number}] ROLLBACK')

    def close(self) -> None:
        print(f'[session {self.number}] CLOSE')


def get_session() -> Iterator[FakeSession]:
    session = FakeSession()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


SessionDep = Annotated[FakeSession, Depends(get_session)]
app = FastAPI()


@app.get('/ok')
def ok(session: SessionDep) -> dict[str, int]:
    return {'session': session.number}


@app.get('/fail')
def fail(session: SessionDep) -> None:
    raise HTTPException(400, detail='something was wrong with the request')


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)

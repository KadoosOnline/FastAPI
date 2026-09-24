"""Status codes: the first thing a client reads.

    200 OK            the default
    201 Created       after POST created something   -> status_code=201
    204 No Content    after DELETE, nothing to send  -> status_code=204
    400 Bad Request   the request makes no sense
    404 Not Found     no such resource               -> HTTPException(404)
    409 Conflict      clashes with existing data (duplicate email)
    422               invalid data (FastAPI does this for us)

Use `fastapi.status` constants instead of bare numbers: easier to read.
"""

import uvicorn
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()


class NewUser(BaseModel):
    email: str
    full_name: str


USERS: dict[int, dict] = {1: {'id': 1, 'email': 'sara@example.com', 'full_name': 'Sara'}}


@app.post('/users', status_code=status.HTTP_201_CREATED)
def create_user(user: NewUser) -> dict:
    if any(u['email'] == user.email for u in USERS.values()):
        raise HTTPException(status.HTTP_409_CONFLICT, detail='Email already registered')
    new_id = max(USERS, default=0) + 1
    USERS[new_id] = {'id': new_id, **user.model_dump()}
    return USERS[new_id]


@app.delete('/users/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int) -> None:
    if user_id not in USERS:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='User not found')
    del USERS[user_id]


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)

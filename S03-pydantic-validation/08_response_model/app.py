"""Response models: control what LEAVES the API.

The stored user has a password hash. It must never be sent back. The
return type of the endpoint is a model WITHOUT that field:

    @app.get('/users/{user_id}')
    def get_user(user_id: int) -> UserRead: ...

FastAPI validates the outgoing data against `UserRead` and drops every field
that is not declared there. The documentation in /docs also shows exactly
this shape.

(`response_model=UserRead` in the decorator does the same thing; use it when
the function returns something of another type, e.g. a dict.)
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

USERS = {
    1: {'id': 1, 'email': 'sara@example.com', 'full_name': 'Sara', 'password_hash': 'x9$2...'},
}


class UserRead(BaseModel):
    id: int
    email: str
    full_name: str


@app.get('/users/{user_id}', response_model=UserRead)
def get_user(user_id: int) -> dict:
    if user_id not in USERS:
        raise HTTPException(404, detail='User not found')
    return USERS[user_id]  # the hash is in here, but it will be filtered out


@app.get('/users', response_model=list[UserRead])
def list_users() -> list[dict]:
    return list(USERS.values())


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)

"""The current-user dependency: from a Bearer token to a User.

    1. POST /auth/token  (form)  ->  {"access_token": "<JWT>", "token_type": "bearer"}
    2. GET  /users/me    with header  Authorization: Bearer <JWT>

`get_current_user` is the heart of it:
    OAuth2PasswordBearer reads the header (401 if missing)
    -> decode + verify the JWT (401 if invalid or expired)
    -> load the user from the "database" (401 if gone, 403 if disabled)

Every protected endpoint just asks for `CurrentUser`. That is all.
"""

from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pwdlib import PasswordHash
from pydantic import BaseModel

SECRET_KEY = 'change-me-this-must-be-a-long-random-secret-0123456789'
ALGORITHM = 'HS256'
password_hash = PasswordHash.recommended()


class User(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool = True
    hashed_password: str


USERS = {
    1: User(
        id=1,
        email='admin@kadoos.ir',
        role='admin',
        hashed_password=password_hash.hash('Password123'),
    ),
    2: User(
        id=2,
        email='sara@example.com',
        role='student',
        hashed_password=password_hash.hash('Password123'),
    ),
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')
app = FastAPI()

CREDENTIALS_ERROR = HTTPException(
    status.HTTP_401_UNAUTHORIZED,
    detail='Could not validate credentials',
    headers={'WWW-Authenticate': 'Bearer'},
)


@app.post('/auth/token')
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> dict[str, str]:
    user = next((u for u in USERS.values() if u.email == form.username.lower()), None)
    if user is None or not password_hash.verify(form.password, user.hashed_password):
        raise CREDENTIALS_ERROR
    expires = datetime.now(UTC) + timedelta(minutes=30)
    token = jwt.encode(
        {'sub': str(user.id), 'role': user.role, 'exp': expires}, SECRET_KEY, ALGORITHM
    )
    return {'access_token': token, 'token_type': 'bearer'}


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    try:
        claims = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:  # bad signature, expired, malformed...
        raise CREDENTIALS_ERROR from None
    user = USERS.get(int(claims['sub']))
    if user is None:
        raise CREDENTIALS_ERROR
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail='Account disabled')
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


@app.get('/users/me')
def read_me(user: CurrentUser) -> dict:
    return {'id': user.id, 'email': user.email, 'role': user.role}


@app.get('/public')
def public() -> dict[str, str]:
    return {'message': 'no token needed here'}


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)

"""OAuth2 "password flow": the standard way to log in to an API.

The client sends a FORM (not JSON) with `username` and `password` to a token
URL, and gets back an access token. Then it sends that token in every request:

    POST /auth/token        body: username=sara@example.com&password=...
    <- {"access_token": "...", "token_type": "bearer"}

    GET /users/me           header: Authorization: Bearer <access_token>

FastAPI helpers:
* `OAuth2PasswordRequestForm` reads the form (needs `python-multipart`).
  The field is called `username` even when it holds an e-mail: OAuth2 says so.
* `OAuth2PasswordBearer(tokenUrl=...)` is a dependency that reads the
  `Authorization: Bearer ...` header (401 if missing) AND puts an
  **Authorize** button in /docs.

The token here is a fake random string kept in a dict. Session 10 replaces
it with a signed JWT that needs no server-side storage.
"""

import secrets
from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()
USERS = {
    'sara@example.com': {
        'email': 'sara@example.com',
        'full_name': 'Sara Ahmadi',
        'hashed_password': password_hash.hash('Password123'),
    }
}
TOKENS: dict[str, str] = {}  # token -> email

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')
app = FastAPI()


@app.post('/auth/token')
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> dict[str, str]:
    user = USERS.get(form.username.lower())
    if user is None or not password_hash.verify(form.password, user['hashed_password']):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect email or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    token = secrets.token_urlsafe(32)
    TOKENS[token] = user['email']
    return {'access_token': token, 'token_type': 'bearer'}


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    email = TOKENS.get(token)
    if email is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    return USERS[email]


@app.get('/users/me')
def read_me(user: Annotated[dict, Depends(get_current_user)]) -> dict[str, str]:
    return {'email': user['email'], 'full_name': user['full_name']}


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)

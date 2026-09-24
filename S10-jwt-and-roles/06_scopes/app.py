"""OAuth2 scopes: fine-grained permissions INSIDE the token.

Roles are coarse ("admin", "student"). Scopes name single abilities:

    courses:read   courses:write   users:admin

The token lists the scopes it was granted, and each endpoint declares what it
needs with `Security(...)` instead of `Depends(...)`:

    def create_course(user: Annotated[User, Security(get_current_user, scopes=['courses:write'])])

FastAPI collects the required scopes in `SecurityScopes`, and they also show
up in /docs. Typical use: a third-party app gets a token with ONLY
`courses:read`, even when the person who approved it is an admin.

In this course we authorize with roles; scopes are shown so you recognise them.
"""

from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes

SECRET_KEY = 'change-me-this-must-be-a-long-random-secret-0123456789'
ROLE_SCOPES = {
    'admin': ['courses:read', 'courses:write', 'users:admin'],
    'student': ['courses:read'],
}
USERS = {'admin@kadoos.ir': 'admin', 'sara@example.com': 'student'}

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl='/auth/token',
    scopes={
        'courses:read': 'Read courses',
        'courses:write': 'Create and change courses',
        'users:admin': 'Manage users',
    },
)
app = FastAPI()


@app.post('/auth/token')
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> dict[str, str]:
    role = USERS.get(form.username)
    if role is None or form.password != 'Password123':
        raise HTTPException(401, detail='Incorrect email or password')
    allowed = ROLE_SCOPES[role]
    # The client may ask for FEWER scopes than the role allows (form.scopes)
    granted = [s for s in form.scopes if s in allowed] if form.scopes else allowed
    claims = {
        'sub': form.username,
        'scopes': granted,
        'exp': datetime.now(UTC) + timedelta(minutes=30),
    }
    return {'access_token': jwt.encode(claims, SECRET_KEY, 'HS256'), 'token_type': 'bearer'}


def get_current_user(
    security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]
) -> dict:
    try:
        claims = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.InvalidTokenError:
        raise HTTPException(401, detail='Invalid token') from None
    missing = [s for s in security_scopes.scopes if s not in claims['scopes']]
    if missing:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail=f'Missing scopes: {missing}',
            headers={'WWW-Authenticate': f'Bearer scope="{security_scopes.scope_str}"'},
        )
    return claims


@app.get('/courses')
def list_courses(
    user: Annotated[dict, Security(get_current_user, scopes=['courses:read'])],
) -> dict:
    return {'courses': ['FastAPI'], 'your scopes': user['scopes']}


@app.post('/courses')
def create_course(
    user: Annotated[dict, Security(get_current_user, scopes=['courses:write'])],
) -> dict:
    return {'created by': user['sub']}


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)

"""Login failures, done safely.

| Situation          | Answer | Message                          |
|--------------------|--------|----------------------------------|
| unknown e-mail     | 401    | "Incorrect email or password"    |
| wrong password     | 401    | "Incorrect email or password"    |
| disabled account   | 403    | "This account is disabled"       |
| too many failures  | 429    | "Too many attempts, wait..."     |

Why the SAME message for unknown e-mail and wrong password? Otherwise an
attacker can find out which e-mails are registered ("user enumeration").

Why hash a DUMMY password when the e-mail is unknown? Hashing takes ~50 ms.
Without it, "unknown user" answers much faster than "wrong password", and
the attacker learns the same thing from the TIMING.

The disabled check comes AFTER the password check: only the real owner
learns that the account is disabled.

`verify_and_update` also returns a new hash when the stored one was made
with older, weaker settings -- passwords get upgraded silently at login.
"""

import time
from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()
DUMMY_HASH = password_hash.hash('dummy-password')
MAX_FAILURES = 5

USERS = {
    'sara@example.com': {'hashed_password': password_hash.hash('Password123'), 'is_active': True},
    'old@example.com': {'hashed_password': password_hash.hash('Password123'), 'is_active': False},
}
FAILURES: dict[str, int] = {}

app = FastAPI()


def invalid_credentials() -> HTTPException:
    return HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        detail='Incorrect email or password',
        headers={'WWW-Authenticate': 'Bearer'},
    )


@app.post('/auth/login')
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> dict:
    started = time.perf_counter()
    email = form.username.lower()
    if FAILURES.get(email, 0) >= MAX_FAILURES:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, detail='Too many attempts, wait')

    user = USERS.get(email)
    if user is None:
        password_hash.verify(form.password, DUMMY_HASH)  # spend the same time
        raise invalid_credentials()

    valid, new_hash = password_hash.verify_and_update(form.password, user['hashed_password'])
    if not valid:
        FAILURES[email] = FAILURES.get(email, 0) + 1
        raise invalid_credentials()
    if not user['is_active']:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail='This account is disabled')
    if new_hash:
        user['hashed_password'] = new_hash
    FAILURES.pop(email, None)
    return {'login': 'ok', 'took_ms': round((time.perf_counter() - started) * 1000)}


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)

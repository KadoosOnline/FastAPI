"""Expiry: every access token must die.

A stolen token works until it expires -- the server has no list to delete it
from. So access tokens are short-lived (15-60 minutes). `exp` is a Unix
timestamp; PyJWT checks it automatically and raises `ExpiredSignatureError`.

`options={'require': [...]}` refuses tokens that lack a claim. `leeway`
tolerates small clock differences between servers.
"""

import time
from datetime import UTC, datetime, timedelta

import jwt

SECRET_KEY = 'change-me-this-must-be-a-long-random-secret-0123456789'


def create_token(user_id: int, minutes: float) -> str:
    now = datetime.now(UTC)
    claims = {'sub': str(user_id), 'iat': now, 'exp': now + timedelta(minutes=minutes)}
    return jwt.encode(claims, SECRET_KEY, algorithm='HS256')


def check(token: str, leeway: int = 0) -> str:
    try:
        claims = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=['HS256'],
            options={'require': ['exp', 'iat', 'sub']},
            leeway=leeway,
        )
    except jwt.ExpiredSignatureError:
        return 'EXPIRED -> 401, please log in again'
    except jwt.MissingRequiredClaimError as error:
        return f'INVALID -> {error}'
    expires = datetime.fromtimestamp(claims['exp'], UTC)
    return f'valid for user {claims["sub"]}, expires {expires:%H:%M:%S}'


def main() -> None:
    print(check(create_token(7, minutes=30)))
    short = create_token(7, minutes=1 / 60)  # one second
    print(check(short))
    time.sleep(1.5)
    print(check(short))
    print(check(short, leeway=5), '(with 5 s leeway)')
    print(check(jwt.encode({'sub': '7'}, SECRET_KEY, algorithm='HS256')))


if __name__ == '__main__':
    main()

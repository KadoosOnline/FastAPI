"""JSON Web Tokens (JWT): a signed "ID card" the client carries.

A JWT is three base64 parts separated by dots:

    header . payload . signature
    {"alg":"HS256"} . {"sub":"7","role":"student","exp":...} . <HMAC of both>

* The payload is only ENCODED, not encrypted: anybody can read it.
  Never put a password or a secret in it.
* The signature is made with the server's SECRET KEY. Change one letter of
  the payload and the signature no longer matches: the server rejects it.
* So the server does not need to store tokens: it checks the signature and
  trusts the claims inside.

Standard claims: `sub` (subject: who, as a STRING), `exp` (expires at),
`iat` (issued at). Plus our own: `role`.
"""

import base64
import json

import jwt

SECRET_KEY = 'change-me-this-must-be-a-long-random-secret-0123456789'
ALGORITHM = 'HS256'


def main() -> None:
    token = jwt.encode({'sub': '7', 'role': 'student'}, SECRET_KEY, algorithm=ALGORITHM)
    print(token)

    header, payload, signature = token.split('.')
    padded = payload + '=' * (-len(payload) % 4)
    print('anyone can read the payload:', json.loads(base64.urlsafe_b64decode(padded)))

    print('decoded by the server:', jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]))

    # A student makes themself admin by editing the payload...
    fake_payload = base64.urlsafe_b64encode(b'{"sub":"7","role":"admin"}').decode().rstrip('=')
    forged = f'{header}.{fake_payload}.{signature}'
    try:
        jwt.decode(forged, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidSignatureError as error:
        print('forged token rejected:', error)

    try:
        jwt.decode(token, 'another-server-with-another-secret-key-0000000', algorithms=[ALGORITHM])
    except jwt.InvalidSignatureError as error:
        print('wrong key rejected   :', error)

    # `algorithms=[...]` is a white list: never let the token choose ("alg": "none" attack)
    unsigned = jwt.encode({'sub': '1', 'role': 'admin'}, key=None, algorithm='none')
    try:
        jwt.decode(unsigned, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidAlgorithmError as error:
        print('alg=none rejected    :', error)


if __name__ == '__main__':
    main()

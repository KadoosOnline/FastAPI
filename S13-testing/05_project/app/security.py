"""Passwords (pwdlib + Argon2) and access tokens (PyJWT)."""

from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash
from pydantic import ValidationError

from app.config import Settings
from app.exceptions import AuthenticationError
from app.schemas import TokenPayload

password_hash = PasswordHash.recommended()
DUMMY_HASH = password_hash.hash('dummy-password-for-timing')


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> tuple[bool, str | None]:
    """Returns (is_valid, new_hash_or_None). A '!' placeholder never matches."""
    if not hashed.startswith('$'):
        password_hash.verify(password, DUMMY_HASH)
        return False, None
    return password_hash.verify_and_update(password, hashed)


def create_access_token(user_id: int, role: str, settings: Settings) -> str:
    now = datetime.now(UTC)
    claims = {
        'sub': str(user_id),
        'role': role,
        'iat': now,
        'exp': now + timedelta(minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(claims, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str, settings: Settings) -> TokenPayload:
    """Check signature and expiry; every problem becomes AuthenticationError (401)."""
    try:
        claims = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],  # a white list, never from the token
            options={'require': ['sub', 'exp', 'iat']},
        )
        return TokenPayload.model_validate(claims)
    except jwt.ExpiredSignatureError:
        raise AuthenticationError('Token has expired') from None
    except (jwt.InvalidTokenError, ValidationError):
        raise AuthenticationError('Could not validate credentials') from None

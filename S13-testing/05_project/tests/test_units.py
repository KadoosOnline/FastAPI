"""Unit tests: no HTTP, no database -- just functions."""

from datetime import UTC, datetime, timedelta

import jwt
import pytest
from pydantic import ValidationError

from app.config import Settings
from app.exceptions import AuthenticationError
from app.schemas import CourseQuery, UserRegister
from app.security import create_access_token, decode_access_token, hash_password, verify_password


def test_password_hash_round_trip() -> None:
    hashed = hash_password('Secret2026')

    assert hashed != 'Secret2026'
    assert verify_password('Secret2026', hashed)[0] is True
    assert verify_password('secret2026', hashed)[0] is False
    assert verify_password('anything', '!')[0] is False


def test_token_round_trip(settings: Settings) -> None:
    payload = decode_access_token(create_access_token(7, 'student', settings), settings)

    assert (payload.sub, payload.role) == ('7', 'student')


def test_expired_token(settings: Settings) -> None:
    old = datetime.now(UTC) - timedelta(hours=2)
    token = jwt.encode(
        {'sub': '1', 'role': 'admin', 'iat': old, 'exp': old + timedelta(minutes=5)},
        settings.jwt_secret_key,
        algorithm='HS256',
    )

    with pytest.raises(AuthenticationError, match='expired'):
        decode_access_token(token, settings)


def test_forged_token(settings: Settings) -> None:
    token = jwt.encode(
        {'sub': '1', 'role': 'admin', 'iat': 0, 'exp': 9_999_999_999},
        'a-different-secret-key-of-a-bad-person-0123456789',
        algorithm='HS256',
    )

    with pytest.raises(AuthenticationError):
        decode_access_token(token, settings)


@pytest.mark.parametrize('password', ['short1', '12345678', 'abcdefgh', 'Password123'])
def test_weak_passwords(password: str) -> None:
    with pytest.raises(ValidationError):
        UserRegister(email='a@b.com', full_name='Ab', password=password)


def test_course_query_rejects_reversed_prices() -> None:
    with pytest.raises(ValidationError, match='min_price'):
        CourseQuery(min_price=10, max_price=1)

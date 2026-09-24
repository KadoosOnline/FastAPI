"""Password hashing with pwdlib + Argon2. Plain passwords are never stored."""

from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

# Checked when the e-mail is unknown, so every failed login takes the same time.
DUMMY_HASH = password_hash.hash('dummy-password-for-timing')


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> tuple[bool, str | None]:
    """Returns (is_valid, new_hash_or_None). A '!' placeholder never matches."""
    if not hashed.startswith('$'):
        password_hash.verify(password, DUMMY_HASH)
        return False, None
    return password_hash.verify_and_update(password, hashed)

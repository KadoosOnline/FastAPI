"""Storing passwords: NEVER the password itself, only a slow, salted hash.

Authentication = "who are you?" (prove it with a password, a token...).
Authorization  = "what may you do?" (sessions 10-11).

If the database leaks, plain passwords are a disaster -- people reuse them
everywhere. A HASH is a one-way function: easy to compute, impossible to
reverse. To check a login we hash what the user typed and compare.

But not any hash:
* MD5 / SHA-256 are FAST: a graphics card tries billions per second.
* Password hashes (Argon2, bcrypt) are SLOW on purpose and use a random
  SALT, so the same password gives a different hash every time and
  pre-computed tables are useless.

We use `pwdlib` with Argon2 (the algorithm FastAPI's docs recommend).
The hash string contains the algorithm, its settings and the salt:
    $argon2id$v=19$m=65536,t=3,p=4$<salt>$<hash>
"""

import hashlib
import time

from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()  # Argon2 with sensible settings


def main() -> None:
    first = password_hash.hash('Password123')
    second = password_hash.hash('Password123')
    print(first)
    print('same password, same hash?', first == second)  # False: different salts

    print('correct password:', password_hash.verify('Password123', first))
    print('wrong password  :', password_hash.verify('password123', first))

    started = time.perf_counter()
    for _ in range(10):
        password_hash.hash('Password123')
    argon = (time.perf_counter() - started) / 10

    started = time.perf_counter()
    for _ in range(100_000):
        hashlib.sha256(b'Password123').hexdigest()
    sha = (time.perf_counter() - started) / 100_000

    print(f'argon2: {argon * 1000:.1f} ms per hash')
    print(f'sha256: {sha * 1_000_000:.2f} microseconds per hash ({argon / sha:,.0f}x faster!)')
    print('An attacker wants the FAST one. We choose the slow one.')


if __name__ == '__main__':
    main()

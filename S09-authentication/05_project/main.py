"""Training Center API — version 8 (session 9 project): authentication.

New since session 8:
* users.hashed_password (migration 0003) — Argon2 hashes via pwdlib, app/security.py
* POST /auth/register   public sign-up, ALWAYS a student, password rules
* POST /auth/login      OAuth2 password form; 401 for unknown e-mail or wrong
                        password (same message!), 403 for a disabled account
* POST /users           now admin-only, and creates users with a password and any role

Login answers "Login successful" + the user for now. Session 10 turns it into
a JWT access token and replaces the X-API-Key with real users and roles.

    alembic upgrade head
    python seed.py
    python main.py
"""

import uvicorn

if __name__ == '__main__':
    uvicorn.run('app.main:app', reload=True)

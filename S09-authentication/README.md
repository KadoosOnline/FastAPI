# Session 09 — Authentication and password security

**FastAPI course · 3 hours**

## Goal
Let people prove who they are. Store passwords the only acceptable way — a
slow, salted Argon2 hash — build registration and login with FastAPI's OAuth2
password-form tools, and handle every failure correctly: wrong password,
unknown user, existing e-mail, disabled account, weak password. The project
gets `/auth/register` and `/auth/login`; session 10 turns a successful login
into a JWT access token.

## Time plan
| Part | Minutes | What happens |
|------|---------|--------------|
| Concepts | 45 | authentication vs authorization, hashing vs encryption, the login flow |
| Practice | 110 | examples 01–04, then register / login in the project |
| Review | 25 | attack your own login from Bruno (enumeration, timing, brute force) |

**Practical share: about 75%.**

## Python you already know, used again
`Annotated` + `AfterValidator` (reusable password rule) · custom exceptions
(`AuthenticationError`, `PermissionDeniedError`) · `hashlib` and `time.perf_counter`
· `secrets` · dictionaries as small stores · services and composition ·
tuple returns and unpacking (`valid, new_hash = ...`).

## Install
```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
source .venv/bin/activate         # Linux / macOS
pip install -r requirements.txt
```

## Topics
* Authentication ("who are you?") vs authorization ("what may you do?")
* Why never plain text, why not MD5/SHA-256, what a salt is
* `pwdlib`: `PasswordHash.recommended()`, `hash`, `verify`, `verify_and_update`
* Password rules with `Annotated[str, Field(...), AfterValidator(...)]`
* Public registration never accepts a `role`
* The OAuth2 password flow: form fields `username` and `password`, `python-multipart`
* `OAuth2PasswordRequestForm`, `OAuth2PasswordBearer` and the **Authorize** button in /docs
* 401 with `WWW-Authenticate: Bearer`, 403 for a disabled account, 409, 422, 429
* User enumeration: one message for "unknown user" and "wrong password"
* Timing attacks and the dummy hash
* A simple brute-force limit
* A migration that adds a NOT NULL column to a table with users (`'!'` placeholder)

## Examples
| Folder | Topic |
|--------|-------|
| `01_password_hashing` | Argon2 vs SHA-256: salts, verification, speed |
| `02_register` | Registration: validate, hash, never return the hash |
| `03_oauth2_password_form` | Login form, bearer token, `/users/me`, the Authorize button |
| `04_login_errors` | Enumeration, timing, disabled users, too many attempts |
| `05_project` | **Project:** Training Center API v8 with register + login + Bruno |

## How to run
```bash
cd 01_password_hashing
python app.py
```
The project:
```bash
cd 05_project
alembic upgrade head      # 0003 adds users.hashed_password
python seed.py            # every demo password: Password123
python main.py
```
In /docs, the login endpoint is a form: try it there and in Bruno.

## Exercises
See `exercises.md`.

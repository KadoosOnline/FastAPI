# Session 10 — JWT, the current user and roles

**FastAPI course · 3 hours**

## Goal
Turn a successful login into a **JWT access token**, find out on every
request *who* is calling (`get_current_user`), and decide *what* they may do:
roles (admin, instructor, student) with a reusable dependency factory, and
data-based rules such as "an instructor may change only their own courses".
The temporary `X-API-Key` of sessions 4–9 disappears. Students spend most of
the session attacking the rules from Bruno: no token, a forged token, an
expired token, the wrong role, somebody else's course.

## Time plan
| Part | Minutes | What happens |
|------|---------|--------------|
| Concepts | 45 | JWT anatomy, signing vs encrypting, 401 vs 403, roles vs ownership |
| Practice | 110 | examples 01–06, then protect every endpoint of the project |
| Review | 25 | the permission table below: prove every line in Bruno |

**Practical share: about 75%.**

## Python you already know, used again
Higher-order functions and closures (`require_roles(...)` *returns* a
dependency) · `Annotated` aliases (`AdminUser`, `StaffUser`) · `datetime`,
`timedelta`, time zones · `base64` and `json` · exceptions and `raise ... from None`
· small permission functions that return `bool`.

## Install
```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
source .venv/bin/activate         # Linux / macOS
pip install -r requirements.txt
```

## Topics
* JWT: header, payload, signature; base64 is **not** encryption
* Claims: `sub` (a string!), `exp`, `iat`, and our `role`
* PyJWT: `jwt.encode`, `jwt.decode(..., algorithms=[...])`, `options={'require': [...]}`
* Forged tokens, a wrong key, `alg: none` — and why the algorithm list is a white list
* Expiry, `ExpiredSignatureError`, leeway; why access tokens are short-lived
* `OAuth2PasswordBearer(tokenUrl=...)`, the Authorize button in /docs
* `get_current_user`: token → claims → user (401 / 403)
* `require_roles(...)` and the aliases `AdminUser`, `StaffUser`, `StudentUser`
* 401 (who are you?) vs 403 (you may not)
* Ownership rules: `can_manage_course(course, user)` in `permissions.py`
* OAuth2 scopes with `Security(...)` and `SecurityScopes` (to recognise them)
* The secret key in `.env`, never in the code

## Permission table of the project
| Action | Who |
|--------|-----|
| browse courses | everybody |
| create a course | admin (chooses the instructor) or instructor (for themself) |
| change a course (PUT / PATCH) | admin, or the instructor **of that course** |
| delete a course, manage users | admin |
| see the students of a course | admin, or its instructor |
| enroll / cancel | the logged-in student, for themself |
| `/users/me`, `/users/me/enrollments` | any logged-in user |

## Examples
| Folder | Topic |
|--------|-------|
| `01_jwt_encode_decode` | Read a token, forge one, see it rejected |
| `02_token_expiry` | `exp`, expired tokens, required claims |
| `03_current_user` | Login → JWT → `get_current_user` → `/users/me` |
| `04_role_dependency` | `require_roles` factory, 401 vs 403 |
| `05_ownership_rules` | "Only your own courses" |
| `06_scopes` | OAuth2 scopes with `Security` |
| `07_project` | **Project:** Training Center API v9 with JWT and roles + Bruno |

## How to run
```bash
cd 04_role_dependency
python app.py
```
then **Authorize** in /docs with `admin@kadoos.ir`, `teacher@kadoos.ir` or
`sara@example.com` (password `Password123`).

The project:
```bash
cd 07_project
alembic upgrade head
python seed.py
python main.py
```
In Bruno, run the four login requests first: they store `adminToken`,
`teacherToken`, `teacher2Token` and `studentToken`, which the other requests use.

## Exercises
See `exercises.md`.

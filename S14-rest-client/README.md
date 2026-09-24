# Session 14 — Building a Python REST client with HTTPX

**FastAPI course · 3 hours**

## Goal
Change sides. We built the server; now we write a program that *uses* it.
Learn HTTPX from the client's point of view — methods, query parameters,
JSON and form bodies, headers, timeouts, bearer tokens, error handling — and
turn loose requests into a real, reusable, typed client class for the
Training Center API: `register`, `login`, `me`, list / create / update /
delete courses, `enroll`, and clean exceptions when anything goes wrong.

## Time plan
| Part | Minutes | What happens |
|------|---------|--------------|
| Concepts | 35 | the client's view of HTTP, requests vs httpx, what a good client class hides |
| Practice | 120 | examples 01–05, then the client in `06_project` against the real API |
| Review | 25 | test the client offline with `MockTransport`, homework |

**Practical share: about 80%.**

## Python you already know, used again
Classes and composition (the client *has* an `httpx.Client`) · context
managers (`with TrainingCenterClient() as api`) · generators (`iter_courses`
hides pagination) · custom exception hierarchies (`NotFound`, `ConflictError`)
· Pydantic models and generics (`Page[Course]`) · type hints everywhere ·
JSON serialization · keyword-only arguments and `**kwargs`.

## Install
```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
source .venv/bin/activate         # Linux / macOS
pip install -r requirements.txt
```

## The server
Examples 04, 05 and the project's `demo.py` talk to the API of session 13.
Start it in a **second terminal** first:
```bash
cd ../S13-testing/05_project
alembic upgrade head
python seed.py
python main.py
```

## Topics
* Client vs server; requests vs HTTPX
* `httpx.get(...)` vs `with httpx.Client(base_url=..., timeout=..., headers=...)`
* GET / POST / PUT / PATCH / DELETE from Python
* `params=`, `json=`, `data=` (forms), `files=` (uploads), `headers=`
* Reading a response: `status_code`, `headers`, `json()`, `text`, `elapsed`
* Timeouts: `httpx.Timeout(10, connect=3)`; never wait for ever
* Transport errors (no answer) vs HTTP error statuses (an answer that says no)
* `raise_for_status()` and why a client maps errors to its own exceptions
* Bearer tokens: log in with a form, keep the token, send it on every request (`httpx.Auth`)
* A client class: one connection pool, one `_request` method, typed return values
* Client-side models that ignore unknown fields
* A generator that walks every page for the caller
* Testing a client with `httpx.MockTransport` (no server, no network)

## Examples
| Folder | Topic |
|--------|-------|
| `01_httpx_basics` | The five methods against a public API |
| `02_params_headers_json` | Query parameters, headers, JSON vs form bodies |
| `03_timeouts_and_errors` | Every kind of failure, simulated with `MockTransport` |
| `04_bearer_auth` | Log in to our API and use the token |
| `05_client_class` | From loose requests to a small class |
| `06_project` | **Project:** `clients/training_center_client.py` + `demo.py` + tests |

## How to run
```bash
cd 03_timeouts_and_errors
python app.py
```
The project:
```bash
cd 06_project
pytest              # the client's tests: no server needed
python demo.py      # talks to the running API of session 13
```

## Exercises
See `exercises.md`.

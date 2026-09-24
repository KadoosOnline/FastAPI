# Session 13 — Automated API testing with pytest

**FastAPI course · 3 hours**

## Goal
Bruno checks the API when *you* click. Automated tests check it every time
anything changes. Learn pytest (assertions, parametrize, fixtures), FastAPI's
`TestClient`, async tests with `httpx.AsyncClient`, and dependency overrides
that swap the database and the current user for test versions. Then give the
Training Center project a real test suite — with at least as many
**failure** tests as happy-path tests.

## Time plan
| Part | Minutes | What happens |
|------|---------|--------------|
| Concepts | 35 | what to test, arrange/act/assert, fixtures, why overrides |
| Practice | 120 | examples 01–04, then write tests for the project |
| Review | 25 | break the code on purpose and watch the right test fail |

**Practical share: about 80%.**

## Python you already know, used again
Functions and `assert` · decorators (`@pytest.fixture`, `@pytest.mark.parametrize`)
· generators (`yield` fixtures with clean-up) · closures (factories) ·
`async`/`await` · context managers · dependency injection seen from the other
side: *we* choose what gets injected.

## Install
```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
source .venv/bin/activate         # Linux / macOS
pip install -r requirements.txt
```

## Topics
* pytest: test discovery, `assert`, `-v`, `-k`, `-x`
* `pytest.raises(..., match=...)`, `@pytest.mark.parametrize`, `ids=`
* Fixtures: plain, `yield` with clean-up, fixtures using fixtures, `tmp_path`
* `TestClient(app)`: status code, JSON body, headers
* FastAPI's testing tools are built on HTTPX (and Starlette 1.7 prefers the `httpx2` fork)
* Testing validation (422), missing things (404), conflicts (409)
* `app.dependency_overrides[...]` — fake database, fake current user; always `.clear()`
* Async tests: `pytest.mark.anyio`, `anyio_backend`, `httpx.AsyncClient(transport=ASGITransport(app))`
* A test database: a fresh SQLite file per test, `create_all`, a test `get_db`
* Factories for users and courses; creating auth headers without logging in
* Testing authentication (401) and authorization (403) boundaries
* Unit tests (functions) vs API tests (HTTP) vs manual tests (Bruno)

## Examples
| Folder | Topic |
|--------|-------|
| `01_pytest_basics` | Plain pytest on pricing functions |
| `02_testclient` | `TestClient`: 201, 404, 422 |
| `03_dependency_overrides` | Fake database and fake user |
| `04_async_tests` | `AsyncClient` + `ASGITransport`, concurrent requests in a test |
| `05_project` | **Project:** Training Center API v12 + 51 tests (`tests/`) |

## How to run
```bash
cd 01_pytest_basics
pytest -v
```
The project:
```bash
cd 05_project
pytest            # 51 tests, a few seconds, no server needed
```

## Exercises
See `exercises.md`.

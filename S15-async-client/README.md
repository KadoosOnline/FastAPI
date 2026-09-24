# Session 15 — Async client, retries and integration

**FastAPI course · 3 hours**

## Goal
Take the client of session 14 to the next level. Use `httpx.AsyncClient` to
run many requests at once (politely, with a limit), retry temporary failures
safely, map every error to a meaningful exception, and consume a third-party
API you do not control. Then write a small **client application** that logs
in, keeps its JWT, reads protected data concurrently, creates and updates a
course, and fails gracefully. Finally see the same API used by a completely
different client: a web page with JavaScript `fetch`.

## Time plan
| Part | Minutes | What happens |
|------|---------|--------------|
| Concepts | 35 | why async on the client, idempotency and retries, integration rules |
| Practice | 120 | examples 01–06, then `client_app` against the real API |
| Review | 25 | stop the server, break the network, see every failure handled |

**Practical share: about 80%.**

## Python you already know, used again
`async`/`await`, `asyncio.gather`, `asyncio.Semaphore` · async context managers
(`async with`) · async generators (`async for course in api.all_courses()`) ·
exception hierarchies · Pydantic models for external data · generics
(`fetch_list[T]`) · `argparse` · closures in tests.

## Install
```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
source .venv/bin/activate         # Linux / macOS
pip install -r requirements.txt
```

## The server
Examples 01, 06 and the project need the API of session 13 in a second terminal:
```bash
cd ../S13-testing/05_project
alembic upgrade head
python seed.py
python main.py
```

## Topics
* `httpx.AsyncClient`: the same API as `Client`, with `await`
* `asyncio.gather` for many requests; `asyncio.Semaphore` to limit them
* When concurrency helps (network latency) and when it does not (localhost)
* Retry rules: only idempotent methods, only temporary failures (transport, 502/503/504, 429)
* Exponential backoff and `Retry-After`
* Error mapping in one place; `ApiUnavailable` vs `ServerError`
* Event hooks for logging every request and response
* Authentication state inside the client; token stored after login
* Integration patterns for third-party APIs: minimal models, timeouts, validation, isolation
* The same REST API from a browser with `fetch` (CORS from session 11)
* Testing async clients with `MockTransport` and `pytest.mark.anyio`

## Examples
| Folder | Topic |
|--------|-------|
| `01_async_client` | `AsyncClient` against our API |
| `02_concurrent_requests` | Sequential vs `gather` vs limited, on a real network |
| `03_retry_and_backoff` | A flaky fake server; GET retried, POST not |
| `04_error_mapping` | Status → exception table, event hooks |
| `05_third_party_api` | A report from a public API, validated and isolated |
| `06_browser_fetch` | `index.html`: the same API from JavaScript |
| `07_project` | **Project:** `client_app/` — `main.py`, `api_client.py`, `models.py` + tests |

## How to run
```bash
cd 03_retry_and_backoff
python app.py
```
The project:
```bash
cd 07_project
pytest                                        # no server needed
python -m client_app.main                     # the teacher dashboard
python -m client_app.main --new-course "Git Basics"
python -m client_app.main --password wrong    # a clean error, no traceback
```
The browser client:
```bash
cd 06_browser_fetch
python -m http.server 5500                    # then open http://localhost:5500
```

## Exercises
See `exercises.md`.

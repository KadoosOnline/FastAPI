# Session 12 — Async FastAPI, async SQLAlchemy and the application lifespan

**FastAPI course · 3 hours**

## Goal
Connect `async`/`await` from the Advanced Python course to a real backend.
Measure when async helps (many requests waiting on I/O) and when it hurts
(blocking calls inside `async def`). Use `asyncio.gather` inside an endpoint,
switch SQLAlchemy to `AsyncEngine` / `AsyncSession`, manage shared resources
with a lifespan, and reproduce the classic async mistakes. Then convert the
whole Training Center project to async — the API must answer exactly as before.

## Time plan
| Part | Minutes | What happens |
|------|---------|--------------|
| Concepts | 40 | the event loop, `def` vs `async def` in FastAPI, what an async driver is |
| Practice | 115 | measure examples 01–05, then convert the project layer by layer |
| Review | 25 | replay the session 11 Bruno collection against the async project |

**Practical share: about 78%.**

## Python you already know, used again
`async def` / `await` / coroutines · `asyncio.gather`, `asyncio.timeout`,
`asyncio.to_thread` · async context managers (`async with`,
`@asynccontextmanager`) · async generators (`get_db`) · the GIL and CPU-bound
vs I/O-bound work · exceptions inside tasks (`return_exceptions=True`).

## Install
```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
source .venv/bin/activate         # Linux / macOS
pip install -r requirements.txt
```
For PostgreSQL with async, also `pip install asyncpg` and use
`postgresql+asyncpg://...` in `DATABASE_URL`.

## Topics
* The event loop; I/O-bound vs CPU-bound work
* FastAPI runs `async def` on the loop and `def` in a thread pool
* The blocking mistake: `time.sleep`, `requests`, sync drivers inside `async def`
* `asyncio.gather` inside one request: wait for the longest, not the sum
* `create_async_engine`, `async_sessionmaker(expire_on_commit=False)`, `AsyncSession`
* Async drivers: `aiosqlite`, `asyncpg`
* What is awaited (`commit`, `get`, `scalars`, `execute`, `delete`, `refresh`) and what is not (`add`)
* No lazy loading in async (`MissingGreenlet`): `selectinload`, `joinedload`, explicit queries
* `run_sync` for `create_all` and `inspect`
* Lifespan: start-up and shutdown, `app.state`, one shared `httpx.AsyncClient`
* One `AsyncSession` per task; never share it between concurrent tasks
* `asyncio.to_thread` for CPU-heavy or blocking code; `anyio` for files
* Async Alembic (`async_engine_from_config`)
* `DateTime(timezone=True)`: a bug SQLite hid and PostgreSQL + asyncpg found

## Examples
| Folder | Topic |
|--------|-------|
| `01_blocking_vs_async` | `async-good` vs `sync-ok` vs `async-bad`, measured with `load_test.py` |
| `02_concurrent_calls` | Three waits in one request: sequential vs `gather` |
| `03_async_sqlalchemy` | `AsyncSession`, `MissingGreenlet`, `selectinload` |
| `04_lifespan` | Start-up / shutdown, a shared HTTP client on `app.state` |
| `05_common_mistakes` | Missing `await`, blocked loop, shared session, CPU work |
| `06_project` | **Project:** Training Center API v11 — async from top to bottom + Bruno |

## How to run
```bash
cd 01_blocking_vs_async
python load_test.py
```
The project:
```bash
cd 06_project
alembic upgrade head
python seed.py
python main.py
```

## The bug PostgreSQL found
The models used `Mapped[datetime]`, which creates `TIMESTAMP WITHOUT TIME ZONE`,
while the code stores time-zone-aware UTC times. SQLite does not care, and the
sync `psycopg` driver quietly converts. `asyncpg` refuses:
*"can't subtract offset-naive and offset-aware datetimes"*. The fix is one line
on the `Base` class, now in every project since session 5:

```python
class Base(DeclarativeBase):
    type_annotation_map = {datetime: DateTime(timezone=True)}
```
Lesson: test on the database you deploy to.

## Exercises
See `exercises.md`.

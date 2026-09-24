# Session 12 — Exercises

## Measure
1. Run `01_blocking_vs_async/load_test.py` with 50 requests instead of 10.
   Why does `/sync-ok` start to slow down at some point? (Hint: the size of
   the thread pool.)
2. Add `/async-requests` that calls a slow URL with the `requests` library
   inside `async def`. Measure it. Fix it with `httpx.AsyncClient`.
3. In `02_concurrent_calls`, make `load_weather` fail. What happens to the
   whole request with `gather`? Change it so the page still loads without the
   weather (`return_exceptions=True` or `try` inside the helper).

## Async SQLAlchemy
4. In `03_async_sqlalchemy`, list every user with their courses using
   `selectinload(User.courses)`. Then try `joinedload` for the same thing and
   read the error you get without `.unique()`.
5. Remove `expire_on_commit=False` and read `ali.full_name` after the commit.
   Explain the error.

## Lifespan and mistakes
6. In `04_lifespan`, load a small JSON "course catalogue" file once at
   start-up into `app.state` and serve it from an endpoint.
7. In `05_common_mistakes`, time the CPU work with `asyncio.to_thread` for 1,
   2 and 4 parallel calls. Does it get faster with more threads? Why not?
   (The GIL.)

## The project
8. **Convert it yourself:** starting from `S11-files-cookies-cors/09_project`,
   convert one layer at a time (database → services → deps → routers → storage
   → alembic → seed). After each layer, run the Bruno collection. Compare
   with `06_project` only at the end.
9. Add `GET /courses/{id}/overview` that loads the course detail, its
   students and its materials **concurrently** with `asyncio.gather`. Why do
   you need three separate sessions for that?
10. Add a lifespan check that the upload folder is writable and that the
    database answers `SELECT 1`; refuse to start otherwise.
11. Run the project on PostgreSQL with `asyncpg` (see
    `S05-sqlalchemy-models/05_postgresql_with_docker`) and replay the Bruno
    collection.

## To think about
12. The API answers exactly the same as in session 11. So what did we gain?
    When would you *not* convert a project to async?
13. Why is `db.add(obj)` not awaited but `db.delete(obj)` is?
14. Where in the project is CPU-heavy work that blocks the loop? (Hint: Argon2.)
    How could you move it off the loop?

## Homework
Convert your **Library API** to async (aiosqlite), add a lifespan with a
shared `httpx.AsyncClient`, and add `GET /books/{isbn}/details` that combines
your own book row with data fetched concurrently from a public books API
(e.g. `https://openlibrary.org/isbn/<isbn>.json`), with a 3-second timeout and
a graceful answer when the public API is down.

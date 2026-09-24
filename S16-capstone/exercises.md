# Session 16 — Exercises

The main work of this session is `01_starting_project/TASKS.md`.
These are extra challenges for teams that finish early, and the homework.

## Extra challenges
1. Add `GET /courses/{id}/materials` pagination with the generic `Page[T]`.
2. Add a `completed` status: `POST /courses/{id}/complete/{student_id}` for
   the course's instructor, and a certificate endpoint that returns a small
   text file only for completed students.
3. Run the whole project on PostgreSQL with `asyncpg` and replay the Bruno
   collection. Did anything behave differently?
4. Measure: with `DATABASE_ECHO=true`, count the SQL statements of
   `GET /users/stats` before and after your refactoring.
5. Add a `--watch` option to the client dashboard that refreshes every
   10 seconds until Ctrl-C.

## Homework (final project)
Finish your **Library API** as a complete application in the same shape:
routers, schemas, services, dependencies, settings, SQLAlchemy models with
relationships, Alembic migrations, JWT with two roles, file uploads (covers),
pagination and filters, at least 30 tests, a Bruno collection and an async
Python client with a small dashboard. Present it with the questions of
`code-review.md`.

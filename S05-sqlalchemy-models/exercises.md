# Session 05 — Exercises

## Models
1. In `02_declarative_models`, add `phone: Mapped[str | None]` and
   `is_active: Mapped[bool]` with a default. Read the `CREATE TABLE` that
   `echo=True` prints: which one is `NOT NULL`?
2. Write the `Course` model of example 02 in the *old* style with
   `Column(...)`. Then, in VS Code, hover over `course.price` in both
   versions. What does the editor know in each case?
3. Add a `Room` model (`id`, `name` unique, `seats` > 0) with a foreign key
   from `Course.room_id` that may be `NULL`.

## Queries
4. In `03_insert_and_query`, print the most expensive course, the number of
   beginner courses, and all titles in alphabetical order — one `select` each.
5. What is the difference between `session.get(Course, 2)` and
   `session.scalar(select(Course).where(Course.id == 2))`? When does it matter?
6. Remove `session.commit()` from the first `with` block and run again. What
   happened to the data? Why?

## Constraints and errors
7. In `04_constraints_and_defaults`, forget the `session.rollback()` after the
   duplicate e-mail. Read the next error message carefully.
8. Remove the `PRAGMA foreign_keys=ON` listener. Which insert now succeeds
   although it should not?
9. **Debug the connection:** in `05_postgresql`, change the
   password, the port, then the database name in the URL. Write down the
   error for each case.

## The project
10. Add `GET /users/{user_id}/enrollments` using a `select` with a `where`.
11. Make `POST /courses` refuse a second course with exactly the same title
    by the same instructor (409), *before* touching the database.
12. Add a `CheckConstraint` to `Enrollment.status` so only `active`,
    `cancelled` and `completed` are allowed. Delete `training.db`, run
    `seed.py`, and prove the constraint works with a small script.
13. Set `DATABASE_ECHO=true` in `.env` and call `GET /courses/1/enrollments`
    from Bruno. How many SQL statements does one request run?
14. Point the project at PostgreSQL (the database of example 05) by changing only
    `.env`. Run `seed.py` and the Bruno collection again.

## To think about
15. Pydantic already checks `price >= 0`. Why do we *also* have a
    `CheckConstraint` in the database?
16. Why is the engine created once, but a session created per request?
17. `create_all` never changes an existing table. What happens if you add a
    column to a model today? (Session 8 answers with Alembic.)

## Homework
Move your **Library API** to SQLAlchemy: `Book`, `Member` and `Loan` models
in the typed style with sensible constraints (unique ISBN, `pages > 0`,
a loan can not end before it starts), a `get_db` dependency, a `seed.py`, and
the create / read endpoints working against SQLite. Bonus: run it on
PostgreSQL installed on your computer.

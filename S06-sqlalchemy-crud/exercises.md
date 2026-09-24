# Session 06 — Exercises

## Write the query (in `01_queries`, one new script)
For each requirement, write the `select` yourself, print it, then run it.
1. All active courses of Mina, most expensive first.
2. The titles of courses whose title contains "python" (any case) and cost
   less than 3 000 000.
3. How many courses each level has, but only levels with more than one course
   (`having`).
4. The instructor (full name) of the cheapest course — one query with `join`.
5. The second page of all courses ordered by title, 2 per page (`offset`, `limit`).

## Changes
6. Write `raise_prices(session, level, percent)` with a bulk `update()` and
   return the number of changed rows.
7. In `02_changes/03_transactions.py`, add a third step to `hand_over`: write
   a line into a new `AuditLog` table. Make the log insert fail and prove that
   the courses did not move.
8. In `05_session_lifecycle.py`, create the session with
   `Session(engine, expire_on_commit=False)`. Which SELECT disappears? When is
   that setting useful (think of returning objects after commit)?

## Refactor
9. **Fix `03_refactor_me`**: `get_db` with `yield`, Pydantic schemas for input
   and output, `select`/`get` instead of Python loops, parameters instead of
   f-strings, 404 / 204 / 409 with real status codes. Prove with Bruno that
   the SQL injection and the "one error breaks everything" bug are gone.

## The project
10. Add `GET /users/{user_id}/enrollments?status=active` (service + router).
11. Add `GET /courses/stats` that returns, per level, the number of active
    courses and the average price — computed by the database, not in Python.
12. Add `sort` to `GET /courses` (`title`, `price`, `-price`, `created_at`).
    Refuse unknown values with 422 (hint: a `Literal`).
13. Make `DELETE /courses/{id}` refuse to delete a course with active
    students (409) and add a `?force=true` query parameter that deletes anyway.
14. Remove the `_check_title_is_free` call from `create` and create the same
    course twice from Bruno. Which handler answers now, and what does the
    client see? Put the check back.

## To think about
15. Why do we `refresh()` after `commit()` in the services?
16. PATCH with `{"title": null}` is refused, PATCH with `{}` too. Why is each
    rule there?
17. When is a soft delete (`is_active = False`) better than a real DELETE for a
    training center?

## Homework
Finish the CRUD of your **Library API**: update / delete for books and
members, borrow and return a book inside **one transaction** (the loan row
and the `available` flag change together), a search endpoint with at least
four optional filters, and a `GET /stats` endpoint with counts per author.
Every error must have the right status code; add all requests to Bruno.

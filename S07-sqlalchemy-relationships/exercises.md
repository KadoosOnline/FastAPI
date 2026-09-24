# Session 07 — Exercises

## Relationships
1. In `01_one_to_many.py`, move *all* of Ali's courses to Mina using only the
   relationship attributes (no `instructor_id`).
2. Add a `Room` model and a one-to-many relationship `Room.courses` ↔
   `Course.room`, with `back_populates`. Put two courses in one room.
3. In `02_many_to_many.py`, add `grade: Mapped[int | None]` to `Enrollment`
   and print, for each course, the average grade of its active students with
   ONE query (`func.avg` + `group_by`).

## Seeing the SQL
4. Run `03_n_plus_1.py` with 40 courses instead of 4 (create them in a loop).
   How many queries does the lazy version run now?
5. Load every enrollment with its student AND its course. Try it lazily, then
   with two `joinedload`s, then with two `selectinload`s. Count the queries.
6. Why does `joinedload` on a *collection* (e.g. `Course.enrollments`) need
   `.unique()` on the result? Try it and read the error.

## Cascades and transactions
7. Remove `cascade='all, delete-orphan'` from `Course.enrollments` in
   `04_cascade.py`. What happens now when you delete a course?
8. In `05_multi_record_transaction.py`, forget the `session.flush()` in the
   loop and enroll into the same nearly-full course twice. Explain the result.

## The project
9. Turn on `DATABASE_ECHO=true` and call `GET /users/4/enrollments` in Bruno.
   Count the SELECT statements. Remove the `selectinload` and count again.
10. Add `GET /courses?with_instructor=true` that returns every course with a
    nested `instructor` — in at most two queries, whatever the number of courses.
11. Add `GET /users/{id}/classmates`: every other active student who shares
    at least one course with this student (a self-join or a sub-query).
12. Add `POST /courses/{id}/complete/{student_id}` that sets the status to
    `completed`. A completed student can not cancel any more (400).
13. Make `DELETE /users/{id}` work for instructors by first moving their
    courses to another instructor given in the query string — in one transaction.

## To think about
14. Why is `Enrollment` a full model and not just a `secondary` table?
15. `course.students` is `viewonly=True`. What would go wrong if you could
    `course.students.append(user)`?
16. When would you prefer `joinedload` and when `selectinload`?

## Homework
Add relationships to your **Library API**: `Author ──< Book`, and
`Member ──< Loan >── Book` with `borrowed_at` / `returned_at` on the loan.
Endpoints: a book with its author (one query), a member's current loans with
their books (no N+1 — prove it with `echo=True`), and "borrow three books at
once" as a single transaction.

# Session 08 — Exercises

## Alembic
1. In `01_alembic_basics`, do part B of its README: add a `capacity` column,
   autogenerate, read the file, upgrade, downgrade, upgrade.
2. Add a NOT NULL column **without** a `server_default` and upgrade a database
   that already has rows. Read the error, then fix the revision.
3. Rename `price` to `price_toman` in the model. What does autogenerate
   produce? Why is that dangerous for the data, and how do you write the
   revision by hand (`batch_op.alter_column(..., new_column_name=...)`)?
4. Run `alembic upgrade head --sql` in the project. What is it good for?

## Pagination and filters
5. In `01_pagination.py`, remove the `order_by`. Is the result still correct?
   Why can it break on PostgreSQL?
6. Add `?level=` to `03_reusable_paginate.py` without touching `paginate()`.
7. Implement **cursor** pagination in a new endpoint `/courses/feed?after=17&size=10`
   that returns `{"items": [...], "next_cursor": 27}`.

## The project
8. Add a migration `0003` that creates an index on `courses.level`. Check it
   with `alembic check` afterwards.
9. Add `GET /courses/{id}/students` pagination with the same `Page[T]`.
10. Add `sort=students` (number of active students, most first). You will
    need a sub-query or an outer join with `group_by`.
11. Add `GET /users?q=` that searches in full name *and* email.
12. Make the default sort of `/courses` the start date (courses without a
    date at the end). Hint: `Course.start_date.asc().nulls_last()`.
13. Add every new query to the Bruno collection, plus one 422 for each rule.

## To think about
14. Why does the API return `total` and `pages`? Who uses them?
15. A client sends `?sort=price; DROP TABLE courses`. What happens, and why
    is our API safe?
16. Why should the migration files be committed together with the model change?

## Homework
Put your **Library API** under Alembic (initial revision + one revision that
adds `Book.language`), and make `GET /books` a real list endpoint: pagination
with `Page[T]`, search in title and author, filters by year range, language
and availability, and sorting by title, year and `-year`. Everything in one
`BookQuery` model with `extra='forbid'`.

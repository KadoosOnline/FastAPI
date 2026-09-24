# Alembic in five minutes

`Base.metadata.create_all()` only creates tables that do not exist. It never
changes an existing table, and it keeps no history. **Alembic** keeps the
history of the database schema as numbered Python files ("revisions"), like
Git does for code:

```
alembic/versions/0001_create_courses.py      create the table
alembic/versions/0002_add_course_level.py    add a column
```

Each revision has an `upgrade()` (go forward) and a `downgrade()` (go back).
The database remembers which revision it is at, in a small table called
`alembic_version`.

## A. Replay the history that is already here
```bash
alembic upgrade head        # run 0001 then 0002 -> school.db is created
alembic current             # which revision is the database at?
alembic history             # the list of revisions
alembic downgrade -1        # undo the last one (level disappears)
alembic upgrade head        # and forward again
alembic downgrade base      # back to an empty database
```
Open `school.db` in a SQLite viewer between the steps and watch the table change.

## B. Make your own revision
1. `alembic upgrade head`
2. Add a column to `Course` in `models.py`, for example
   `capacity: Mapped[int] = mapped_column(server_default='20')`
3. `alembic revision --autogenerate -m "add course capacity"`
4. **Read the generated file** in `alembic/versions/`. Autogenerate is a
   helper, not magic: always check what it wrote.
5. `alembic upgrade head`, then `alembic downgrade -1`, then `upgrade head` again.

## How this folder was set up (you do this once per project)
```bash
alembic init alembic
```
then two edits in `alembic/env.py`:
* `target_metadata = Base.metadata` — so autogenerate can compare the models with the database
* `config.set_main_option('sqlalchemy.url', DATABASE_URL)` — one URL for app and migrations

and, because this is SQLite, `render_as_batch=True` in `context.configure(...)`:
SQLite can not `ALTER` most things, so Alembic rebuilds the table in "batch" mode.

## Rules
* Never edit a revision that has already been applied on someone else's database; write a new one.
* A new NOT NULL column on a table with rows needs a `server_default` (or a data migration).
* Commit the `alembic/versions/` files to Git together with the model change.

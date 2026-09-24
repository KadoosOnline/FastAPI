# Session 05 — SQLAlchemy 2.x: engine, session and typed models

**FastAPI course · 3 hours**

## Goal
Give the Training Center a real memory. Learn the modern, *typed* way of
SQLAlchemy 2.x — `DeclarativeBase`, `Mapped[...]`, `mapped_column(...)`,
`select(...)` — create the `User`, `Course` and `Enrollment` tables, insert
and read rows, let the database enforce its own rules, and plug one session
per request into FastAPI. SQLite in class (nothing to install), PostgreSQL in
one example (installed on your own computer; only the URL changes).

## Time plan
| Part | Minutes | What happens |
|------|---------|--------------|
| Concepts | 45 | why a relational database, engine vs session, the typed model style |
| Practice | 115 | examples 01–06 with `echo=True`, then the database in `07_project` |
| Review | 20 | read the generated SQL, break constraints on purpose, homework |

**Practical share: about 75%.**

## Python you already know, used again
Classes and inheritance (`Base` → `User`) · type hints *become* the columns
(`Mapped[str | None]`) · context managers (`with Session(...)`) · generators
(`yield` in `get_db`) · exceptions (`IntegrityError`, rollback) · environment
variables · dataclass-like models.

## Install
```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
source .venv/bin/activate         # Linux / macOS
pip install -r requirements.txt
```
Optional, for example 05 and later sessions: **PostgreSQL** installed on your
computer (Windows 11 or Ubuntu). Step-by-step instructions: `05_postgresql/README.md`.

A free viewer for `.db` files: **DB Browser for SQLite** (<https://sqlitebrowser.org>)
or the *SQLite Viewer* extension of VS Code.

## Topics
* Why a relational database; tables, rows, primary and foreign keys
* Connection URLs: `sqlite:///training.db`, `postgresql+psycopg://user:pass@host/db`
* `create_engine(..., echo=True)` and reading the SQL it prints
* `Session`: open, work, `commit()`, close — always with `with`
* `class Base(DeclarativeBase)`, `__tablename__`
* `Mapped[int]`, `Mapped[str | None]` (nullable), `mapped_column(String(200), unique=True, index=True)`
* Why the typed style beats the old `Column(...)` style: the editor knows the types
* `Base.metadata.create_all(engine)` (until Alembic in session 8)
* `add`, `add_all`, `commit`, `get`, `select(...).where(...).order_by(...)`, `scalars`, `scalar`
* Constraints: `unique`, `CheckConstraint`, `ForeignKey`, `UniqueConstraint`
* Defaults: `default=`, `server_default=func.now()`, `onupdate=`, timestamps
* `IntegrityError` and `rollback()`; SQLite's `PRAGMA foreign_keys=ON`
* Installing PostgreSQL on Windows 11 and Ubuntu, a user and a database, `psql`; reading connection errors
* `get_db` with `yield`, `DbSession = Annotated[Session, Depends(get_db)]`
* ORM model → Pydantic schema with `from_attributes=True`; `db.refresh()`

## Examples
| Folder | Topic |
|--------|-------|
| `01_engine_and_session` | Engine, Session, raw SQL with `text()` |
| `02_declarative_models` | `DeclarativeBase`, `Mapped`, `mapped_column`, `create_all` |
| `03_insert_and_query` | `add`, `commit`, `get`, `select`, `scalars` |
| `04_constraints_and_defaults` | The database says no: `IntegrityError` |
| `05_postgresql` | Install PostgreSQL (Windows / Ubuntu), `setup.sql`, same code on PostgreSQL |
| `06_fastapi_with_database` | One session per request, ORM → schema |
| `07_project` | **Project:** Training Center API v4 on a database + Bruno |

## How to run
```bash
cd 03_insert_and_query
python app.py
```
Each example creates its own `training.db` next to `app.py`; delete it to start over.

The project:
```bash
cd 07_project
python seed.py        # demo users and courses
python main.py
```
Open `07_project/bruno` in Bruno. Run `seed.py` again after deleting `training.db`.

## Exercises
See `exercises.md`.

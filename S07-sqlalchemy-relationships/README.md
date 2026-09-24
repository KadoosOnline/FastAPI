# Session 07 — SQLAlchemy relationships and efficient loading

**FastAPI course · 3 hours**

## Goal
Connect the tables in Python the way they are connected in the database. An
instructor has courses; students and courses meet through enrollments, a
link that carries its own data. Learn `relationship()` and `back_populates`,
the association-object pattern, cascades, and — most important for a real
API — how to **see** the SQL your code runs and how to avoid the N+1 query
problem with `selectinload` and `joinedload`.

## Time plan
| Part | Minutes | What happens |
|------|---------|--------------|
| Concepts | 40 | one-to-many, many-to-many with data, lazy loading, N+1 on the board |
| Practice | 115 | the five scripts of `01_relationships`, then the project |
| Review | 25 | count queries with `DATABASE_ECHO=true`, fix a slow endpoint, homework |

**Practical share: about 78%.**

## Python you already know, used again
Classes and object references · type hints with forward references
(`Mapped[list['Course']]`) · lists and comprehensions · `lambda` and `sorted(key=)` ·
event hooks (callbacks, a higher-order idea) · context managers and transactions ·
tuple unpacking (`for enrollment, user in rows`) · **shadowing built-ins**
(see the note below).

## Install
```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
source .venv/bin/activate         # Linux / macOS
pip install -r requirements.txt
```

## Topics
* Foreign key (what the database stores) vs relationship (what Python sees)
* One-to-many: `Course.instructor` ↔ `User.courses_taught` with `back_populates`
* Setting either side; `instructor_id` is filled at flush time
* Many-to-many through an association object (`Enrollment` with `status`, `created_at`)
* `secondary=..., viewonly=True` shortcuts such as `course.students`
* Joins: `select(Enrollment, User).join(Enrollment.student)` and `.tuples()`
* Lazy loading, the identity map, and the **N+1 problem**
* `selectinload` (collections), `joinedload` (many-to-one), nested loading
* Counting SQL statements with an engine event; `echo=True`
* Cascades: `all, delete-orphan`; why instructors have *no* cascade
* One transaction for many rows: `flush()` inside, rollback on the first failure

## Examples
| Folder / file | Topic |
|---------------|-------|
| `01_relationships/models.py` | User, Course, Enrollment with relationships + demo data |
| `01_relationships/01_one_to_many.py` | Instructor ↔ courses |
| `01_relationships/02_many_to_many.py` | Students ↔ courses through `Enrollment` |
| `01_relationships/03_n_plus_1.py` | Count the queries: lazy vs `selectinload` vs `joinedload` |
| `01_relationships/04_cascade.py` | Orphans, cascading deletes, a delete that must fail |
| `01_relationships/05_multi_record_transaction.py` | Enroll in many courses: all or nothing |
| `02_project` | **Project:** Training Center API v6 with relationships + Bruno |

## How to run
```bash
cd 01_relationships
python 03_n_plus_1.py
```
The project:
```bash
cd 02_project
python seed.py
python main.py
```

## A bug worth remembering
While writing this session's project, a service class had a method called
`list` and, further down, an annotation `-> list[Course]`. Inside the class
body the name `list` now meant *the method*, and Python crashed with
`TypeError: 'function' object is not subscriptable`. The methods are now
called `list_courses` and `list_users`. Never name anything after a built-in.

## Exercises
See `exercises.md`.

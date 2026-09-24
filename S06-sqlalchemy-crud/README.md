# Session 06 — Real CRUD with SQLAlchemy 2.x

**FastAPI course · 3 hours**

## Goal
Write the queries yourself. Select with conditions, choose between `scalar`,
`scalars` and `execute`, count and group in the database, update and delete
safely, keep several changes in one transaction, and turn missing rows and
broken constraints into clean 404 and 409 answers. Then finish the full CRUD
of the Training Center and end with a refactoring exercise.

## Time plan
| Part | Minutes | What happens |
|------|---------|--------------|
| Concepts | 40 | the life of a session, `scalar` vs `scalars` vs `execute`, transactions |
| Practice | 115 | scripts of `01_queries` and `02_changes`, then CRUD in `04_project` |
| Review | 25 | `03_refactor_me`: find and fix six problems, homework |

**Practical share: about 78%.**

## Python you already know, used again
Classes and composition (services) · context managers (`with Session(...)`,
`session.begin()`) · exceptions and re-raising with `from` · `setattr` and
`**kwargs` · comprehensions · type hints on query results · refactoring.

## Install
```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
source .venv/bin/activate         # Linux / macOS
pip install -r requirements.txt
```

## Topics
* `select(Model).where(...).order_by(...)`, `and` (several `where` arguments), `or_`, `in_`, `ilike`
* `print(stmt)`: every query is SQL you can read
* `scalars()` for objects, `scalar()` for one value, `execute()` for rows of columns
* `get()` by primary key; `scalar_one()` / `scalar_one_or_none()`
* `func.count / avg / min / sum`, `group_by`, a `join` for a report
* Building a search query step by step from optional filters; why parameters stop SQL injection
* UPDATE: change attributes + `commit`; `setattr` for PATCH; bulk `update()`
* DELETE: `session.delete`, bulk `delete()`, soft delete with `is_active`
* Transactions: `session.begin()`, rollback of everything; the "already begun" mistake
* `IntegrityError`: check first *and* keep the database as safety net; `rollback()`
* Session lifecycle: identity map, `flush`, `commit`, expire, `refresh`, `rollback`
* Missing rows → 404; duplicates → 409; broken business rules → 400

## Examples
| Folder / file | Topic |
|---------------|-------|
| `01_queries/models.py` | Shared models + `reset_database()` demo data |
| `01_queries/01_select_and_where.py` | `select`, `where`, `or_`, `in_`, `ilike` |
| `01_queries/02_scalar_scalars_execute.py` | Which result method, when |
| `01_queries/03_aggregates_and_groups.py` | `count`, `avg`, `group_by`, `join` |
| `01_queries/04_search_and_filter.py` | A search function from optional filters |
| `02_changes/01_update.py` | ORM update, PATCH-style `setattr`, bulk update |
| `02_changes/02_delete.py` | Delete, bulk delete, soft delete |
| `02_changes/03_transactions.py` | All-or-nothing with `session.begin()` |
| `02_changes/04_integrity_errors.py` | Duplicates: check first, catch `IntegrityError` |
| `02_changes/05_session_lifecycle.py` | Identity map, flush, commit, rollback |
| `03_refactor_me` | A "working" CRUD with six serious problems |
| `04_project` | **Project:** Training Center API v5 — full CRUD + Bruno |

## How to run
```bash
cd 01_queries
python 01_select_and_where.py
```
Every script rebuilds its small database, so you can run them in any order.

The project:
```bash
cd 04_project
python seed.py
python main.py
```
Delete `training.db` and run `seed.py` again before running the whole Bruno collection.

## Exercises
See `exercises.md`.

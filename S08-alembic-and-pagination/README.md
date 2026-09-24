# Session 08 — Alembic migrations, pagination, filtering and sorting

**FastAPI course · 3 hours**

## Goal
Two things every real backend needs. First, **migrations**: the database
schema changes over time, and Alembic records every change as a revision you
can apply and undo — `create_all` is retired. Second, **list endpoints that
scale**: pagination with a total count, search, filters and sorting, all
designed as validated query parameters and written once as reusable code.
After this session `GET /courses` looks like a real product API.

## Time plan
| Part | Minutes | What happens |
|------|---------|--------------|
| Concepts | 40 | why migrations, revision / upgrade / downgrade; designing list parameters |
| Practice | 115 | `01_alembic_basics`, the three list apps, then the project |
| Review | 25 | make and roll back your own migration, break the list API from Bruno |

**Practical share: about 78%.**

## Python you already know, used again
Generics (`Page[T]`, `paginate[S]`) · Pydantic models as *query* parameters ·
`Literal` as a white list · dictionaries as lookup tables (`SORT_COLUMNS`) ·
`math.ceil` · modules and packages (`alembic/env.py` imports your models) ·
refactoring duplicated code into one function.

## Install
```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
source .venv/bin/activate         # Linux / macOS
pip install -r requirements.txt
```

## Topics
* Why `create_all` is not enough; migrations as "Git for the schema"
* `alembic init`, `env.py` (`target_metadata`, the URL from settings), `alembic.ini`
* `alembic revision --autogenerate -m "..."` — and *reading* what it generated
* `alembic upgrade head`, `downgrade -1`, `downgrade base`, `current`, `history`, `check`
* Adding a column to a table with data: nullable or `server_default`
* SQLite and `render_as_batch=True`
* Offset pagination: `page`, `size`, `total`, `pages`; always `order_by` something unique
* Cursor pagination (concept)
* All list options as one Pydantic model: `Annotated[CourseQuery, Query()]`, `extra='forbid'`
* A query model must be the *only* query parameter of its endpoint
* Search with `ilike`, combined filters, a validated price range
* Sorting from a white list (`Literal` + a dict of columns), `-price` for descending
* A generic `Page[T]` and a reusable `paginate()` helper

## Examples
| Folder / file | Topic |
|---------------|-------|
| `01_alembic_basics` | Two real revisions; replay, undo, make your own (see its README) |
| `02_list_api/database.py` | 45 generated courses for the list examples |
| `02_list_api/01_pagination.py` | `page` / `size` / `total` / `pages` |
| `02_list_api/02_filter_and_sort.py` | Search, filters, white-listed sorting as a query model |
| `02_list_api/03_reusable_paginate.py` | Generic `Page[T]` + `paginate()` for two resources |
| `03_project` | **Project:** Training Center API v7 with Alembic and a real list API + Bruno |

## How to run
```bash
cd 01_alembic_basics
alembic upgrade head
```
```bash
cd 02_list_api
python 02_filter_and_sort.py
```
The project:
```bash
cd 03_project
alembic upgrade head      # creates training.db from the migrations
python seed.py
python main.py
```

## Exercises
See `exercises.md`.

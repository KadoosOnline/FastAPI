# Session 16 — Capstone: integration, debugging, refactoring and code review

**FastAPI course · 3 hours**

## Goal
No lecture today. You receive the Training Center API in a state every
developer knows: *almost* finished. Some tests fail, some bugs have no test,
two endpoints are missing, one endpoint is ugly, and the client is behind.
Working in teams of two, you use everything of the course to make it
correct, complete and clean — and then you defend your code in a review.

## Time plan
| Part | Minutes | What happens |
|------|---------|--------------|
| Briefing | 10 | how to read `TASKS.md`, forming teams |
| Practice | 125 | tasks A–E of `01_starting_project/TASKS.md` |
| Review | 45 | team presentations and `code-review.md` questions |

**Practical share: about 95%** (the review is practice too: reading and explaining code).

## Python you already know, used again
Everything: type hints and `Annotated`, classes and composition, decorators,
generators, context managers, exceptions, async/await, generics, dataclasses,
modules and packages, testing and refactoring.

## Install
```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
source .venv/bin/activate         # Linux / macOS
pip install -r requirements.txt
```

## What the final application contains
FastAPI with routers · Pydantic schemas · Dependency Injection · settings from
`.env` · SQLAlchemy 2.x typed models and relationships · Alembic migrations ·
SQLite (or PostgreSQL) · CRUD · pagination, filtering, sorting ·
registration, Argon2, JWT · roles and ownership · file uploads · CORS ·
async all the way · pytest suite · Bruno collection · an async Python client.

## Folders
| Folder | What it is |
|--------|------------|
| `01_starting_project` | **Your starting point.** Read `TASKS.md` first |
| `02_solution` | One complete solution — open it only after the review |
| `code-review.md` | The questions of the final review |

## How to run
```bash
cd 01_starting_project
alembic upgrade head
python seed.py
pytest                       # 10 failures to begin with
python main.py
python -m client_app.main    # the client (with the server running)
```

## Exercises
See `exercises.md`.

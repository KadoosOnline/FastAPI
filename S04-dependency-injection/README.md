# Session 04 — Dependency Injection, structure, errors and settings

**FastAPI course · 3 hours**

## Goal
Learn FastAPI's most powerful idea: **dependencies**. A function declares what
it needs — paging, a service, the settings, "the caller must have a key" — and
FastAPI prepares it. Then use that idea to turn the single-folder project into
a small, clean package: settings from `.env`, services with the business rules,
one central place that turns business errors into HTTP answers, and thin
routers.

## Time plan
| Part | Minutes | What happens |
|------|---------|--------------|
| Concepts | 45 | what a dependency is, the dependency tree, `yield`, why split files |
| Practice | 110 | examples 01–08, then refactor the project into `09_project` |
| Review | 25 | trace one request through every file, homework |

**Practical share: about 75%.**

## Python you already know, used again
Higher-order functions (FastAPI calls *your* function) · `Annotated` · classes
and composition (services) · dataclasses · generators and context managers
(`yield` dependencies) · custom exceptions and a hierarchy · `functools.lru_cache`
· modules and packages · refactoring.

## Install
```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
source .venv/bin/activate         # Linux / macOS
pip install -r requirements.txt
```

## Topics
* `Depends(func)` and the modern `Annotated[Type, Depends(func)]` aliases
* Dependencies with their own parameters, sub-dependencies, one call per request
* Classes as dependencies, `Depends()` with no argument
* Services as dependencies — the endpoint does not know how they are built
* `yield` dependencies: setup / teardown, rollback on error (the DB session of session 5)
* `Header()`, `Cookie()`, `response.set_cookie()`
* An authentication *dependency* (API key) → 401; the shape of sessions 9–10
* `@app.exception_handler`, one JSON error shape for the whole API
* `pydantic-settings`: `BaseSettings`, `.env`, `lru_cache`, required values
* Dependencies on a router or on the whole app: `dependencies=[...]`
* A project structure: `config`, `exceptions`, `schemas`, `services`, `deps`, `routers`

## Examples
| Folder | Topic |
|--------|-------|
| `01_depends_basics` | One pagination function for two endpoints |
| `02_annotated_dependencies` | `Annotated` aliases, sub-dependencies, caching |
| `03_class_dependencies` | A filter class and a service as dependencies |
| `04_yield_dependencies` | Open / close / rollback around every request |
| `05_headers_and_cookies` | `Header`, `Cookie`, `set_cookie`, an API-key check |
| `06_exception_handlers` | Business exceptions → JSON errors in one place |
| `07_settings` | `BaseSettings` and `.env` |
| `08_router_dependencies` | Protect a whole router at once |
| `09_project` | **Project:** Training Center API v3 as a package + Bruno |

## How to run
```bash
cd 01_depends_basics
python app.py
```
Example 07 needs a `.env` file: copy `.env.example` to `.env` first.

The project:
```bash
cd 09_project
python main.py
```
In Bruno, open `09_project/bruno`; the environment **local** holds the
`adminKey` that is sent in the `X-API-Key` header.

## Exercises
See `exercises.md`.

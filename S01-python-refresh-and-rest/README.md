# Session 01 — Advanced Python refresh, HTTP and REST

**FastAPI course · 3 hours**

## Goal
FastAPI is "just Python" — but it is Python used at full strength. It reads
your **type hints** to validate requests, it uses **`Annotated`** to attach
rules to types, it calls your functions for you (**higher-order functions**),
registers routes with **decorators**, runs dependencies as **context
managers**, and serves thousands of clients with **async/await**.

So before we write a single endpoint, we refresh exactly those tools on
backend-flavoured examples, learn how HTTP and REST work, send our first
requests with **Bruno**, and build the pure-Python core of the project we
will grow for sixteen sessions: the **Training Center API**.

## Time plan
| Part | Minutes | What happens |
|------|---------|--------------|
| Concepts | 50 | type hints, `Annotated`, generics, HTTP/REST/JSON — short, on the board |
| Practice | 110 | examples 01–12 as guided exercises, Bruno, the project |
| Review | 20 | refactor review (example 12), questions, homework |

**Practical share: about 72%.**

## Python you already know, used again
Type hints · `Annotated` · generics and `Protocol` · dataclasses and enums ·
higher-order functions, closures, `lambda`, `partial` · decorators with
`ParamSpec` · custom exception hierarchies · context managers ·
generators · `async`/`await` · packages and modules · refactoring.

## Install
```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
source .venv/bin/activate         # Linux / macOS
pip install -r requirements.txt
```
Then install **Bruno** from <https://www.usebruno.com/downloads>.

## Topics
* Modern type hints: `list[str]`, `dict[str, int]`, `str | None`, `Literal`,
  type aliases — and why FastAPI *reads* them
* `Annotated[type, metadata]` — the syntax of every modern FastAPI signature
* Generic classes and functions (`class Repository[T]`), `Protocol`
* Dataclasses: `slots`, `frozen`, `kw_only`, `default_factory`, `__post_init__`
* Higher-order functions and closures: the idea behind `Depends(...)`
* Decorators done right: `functools.wraps`, `ParamSpec`, decorator factories
* Custom exceptions: a hierarchy named after the business, `raise ... from`
* Context managers: class-based and `@contextmanager`; the "transaction" idea
* Generators: lazy pipelines and hiding pagination
* `async`/`await`, `asyncio.gather`, timeouts, and the *blocking mistake*
* HTTP: client/server, methods, URL, headers, body, **status codes**
* REST: resources in the URL, actions in the method; JSON
* HTTPX: `Client`, `params=`, `json=`, `.json()`, `timeout=`, `raise_for_status()`
* Bruno: collections, environments, variables, tests

## Examples
| Folder | Topic |
|--------|-------|
| `01_type_hints` | Modern hints, `Literal`, aliases, `X \| None` |
| `02_annotated` | Attach rules to types and read them back — FastAPI in miniature |
| `03_generics` | `Repository[T]`, `Protocol`, generic functions |
| `04_dataclasses` | Typed models, `StrEnum`, frozen value objects |
| `05_higher_order_functions` | Closures, combining filters, `partial`, `reduce` |
| `06_decorators` | `@log_calls`, `@timed`, `@retry(times=3)` |
| `07_custom_exceptions` | An error hierarchy that will become HTTP status codes |
| `08_context_managers` | `Timer`, and a transaction with commit / rollback |
| `09_generators` | Walking a paginated source lazily |
| `10_async_await` | Sequential vs `gather`, the blocking mistake, timeouts |
| `11_http_and_json` | A real REST API with HTTPX (needs internet) |
| `12_refactor_me` | Working but bad code — **refactor it** (exercise 12) |
| `13_bruno_first_requests` | Your first Bruno collection |
| `14_project` | **Project:** the Training Center core in plain Python |

## How to run
```bash
cd 01_type_hints
python app.py
```
The project:
```bash
cd 14_project
python main.py
```
For Bruno, open the folder `13_bruno_first_requests` as a collection (see its README).

## The project from here on
```
Session 01  plain Python core (today)        Session 09  register, login, password hashing
Session 02  first FastAPI endpoints          Session 10  JWT and roles
Session 03  Pydantic validation              Session 11  files, cookies, CORS
Session 04  dependencies and structure       Session 12  async all the way
Session 05  SQLAlchemy models + database     Session 13  automated tests
Session 06  real CRUD                        Session 14  a Python client
Session 07  relationships (enrollments)      Session 15  an async client app
Session 08  migrations, pagination, filters  Session 16  capstone
```

## Exercises
See `exercises.md`.

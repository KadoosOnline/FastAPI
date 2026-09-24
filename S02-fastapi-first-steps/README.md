# Session 02 — FastAPI first steps

**FastAPI course · 3 hours**

## Goal
Write real endpoints: read path and query parameters, accept a JSON body,
answer with the right status code, and organise the API with routers. By the
end of the session the Training Center has its first web API — courses and
users with a complete CRUD — tested request by request in Bruno.

## Time plan
| Part | Minutes | What happens |
|------|---------|--------------|
| Concepts | 40 | request → route → function → response; the five methods; status codes |
| Practice | 115 | examples 01–07 together, then students build `08_project` |
| Review | 25 | break the API on purpose in Bruno, read the errors, homework |

**Practical share: about 78%.**

## Python you already know, used again
Decorators (`@app.get`) · type hints (FastAPI *reads* them) · `X | None` ·
dictionaries and comprehensions · exceptions (`HTTPException`) · modules and
packages (routers) · `lambda` and `key=` functions.

## Install
```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
source .venv/bin/activate         # Linux / macOS
pip install -r requirements.txt
```

## Topics
* `FastAPI()`, `uvicorn`, `reload=True`
* Path operations: `@app.get`, `@app.post`, `@app.put`, `@app.patch`, `@app.delete`
* Path parameters and automatic conversion (`/courses/abc` → 422)
* Route order: `/courses/cheapest` before `/courses/{course_id}`
* Query parameters: required, optional, default values
* A JSON request body with a small Pydantic model (details in session 3)
* Status codes: `status_code=201`, `204`, `HTTPException(404)`, `409`, the `status` constants
* PUT (replace everything) vs PATCH (change a part, `exclude_unset=True`)
* `APIRouter`, `prefix`, `tags`, `include_router`
* Swagger UI (`/docs`) and ReDoc (`/redoc`)
* Testing every endpoint in Bruno, including the failing ones

## Examples
| Folder | Topic |
|--------|-------|
| `01_first_app` | The smallest API, `/docs` and `/redoc` |
| `02_path_parameters` | `/courses/{course_id}`, 404, 422, route order |
| `03_query_parameters` | Filters: `?level=&max_price=&q=` |
| `04_request_body` | `POST` with JSON |
| `05_status_codes` | 201, 204, 404, 409 |
| `06_put_patch_delete` | A complete CRUD on one resource |
| `07_routers` | Split the API into `routers/` |
| `08_project` | **Project:** Training Center API v1 + Bruno collection |

## How to run
```bash
cd 01_first_app
python app.py
```
then open <http://127.0.0.1:8000/docs>. Stop the server with Ctrl-C.

The project:
```bash
cd 08_project
python main.py
```
and open the folder `08_project/bruno` in Bruno (environment **local**).

The same server can also be started with the uvicorn command:
```bash
uvicorn main:app --reload
```

## Exercises
See `exercises.md`.

# Session 11 — Real-world FastAPI: headers, cookies, forms, files and CORS

**FastAPI course · 3 hours**

## Goal
The features every real API ends up needing: reading and setting headers,
cookies and their security flags, HTML form data, file uploads that are
validated properly (type, real content, size), private downloads, public
static files, CORS for browser clients, and response types beyond JSON. The
project gets **course materials**: instructors upload files, enrolled students
list and download them, and nobody else can.

## Time plan
| Part | Minutes | What happens |
|------|---------|--------------|
| Concepts | 40 | request/response anatomy, multipart, why uploads are dangerous, CORS |
| Practice | 115 | examples 01–08, then materials in the project |
| Review | 25 | upload attacks from Bruno (fake PDF, huge file, `../` names), homework |

**Practical share: about 78%.**

## Python you already know, used again
Generators (streaming CSV, chunked reading) · context managers (`with open`) ·
`pathlib` (`Path(...).name` against `../` tricks) · `uuid` · bytes and
slicing (magic numbers) · exceptions with cleanup in `except BaseException` ·
dependencies and services · SQLAlchemy relationships and cascades.

## Install
```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
source .venv/bin/activate         # Linux / macOS
pip install -r requirements.txt
```

## Topics
* Request headers with `Header()`; response headers; a timing / request-id middleware
* `Cache-Control`, `Accept-Language`, `X-Request-ID`
* Cookies: `set_cookie`, `Cookie()`, `delete_cookie`; `httponly`, `secure`, `samesite`, `max_age`
* Cookies vs Bearer tokens
* Form data: `Form()`, a Pydantic model as a form, HTML forms, `python-multipart`
* `UploadFile`: `filename`, `content_type`, `size`, chunked `read`, several files
* Upload security: white-listed types, magic bytes, size limits (413), 415, generated names
* `StaticFiles` (public) vs `FileResponse` behind a permission check (private)
* `Content-Disposition: attachment; filename=...`
* CORS: origins, preflight `OPTIONS`, `CORSMiddleware`; why curl and Bruno ignore it
* `JSONResponse`, `RedirectResponse`, `PlainTextResponse`, `StreamingResponse`, 202, `response_model_exclude_none`

## Examples
| Folder | Topic |
|--------|-------|
| `01_headers` | Read and set headers, a middleware for every response |
| `02_cookies` | "Recently viewed courses" kept in a cookie |
| `03_form_data` | An HTML form posting to FastAPI |
| `04_file_upload` | `UploadFile`, chunks, several files |
| `05_file_validation` | Type + magic bytes + size, safe names, 413 / 415 |
| `06_static_files` | Public folder vs protected download |
| `07_cors` | A page on another origin calling the API (`page.html`) |
| `08_responses` | Redirect, text, 202, streaming CSV |
| `09_project` | **Project:** Training Center API v10 with course materials + Bruno |

## How to run
```bash
cd 05_file_validation
python app.py
```
then use `/docs` to upload files. For example 07 read its docstring (two terminals).

The project:
```bash
cd 09_project
alembic upgrade head      # 0004 adds course_materials
python seed.py
python main.py
```
Uploaded files go to `09_project/uploads/` (never committed to Git). In Bruno,
the upload requests use the sample files in `09_project/bruno/files/`.

## Exercises
See `exercises.md`.

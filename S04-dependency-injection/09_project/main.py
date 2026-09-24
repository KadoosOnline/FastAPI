"""Training Center API — version 3 (session 4 project): a real structure.

    09_project/
    ├── main.py              starts the server
    ├── .env.example         copy to .env
    └── app/
        ├── main.py          creates the FastAPI app
        ├── config.py        Settings (pydantic-settings)
        ├── exceptions.py    business errors + the handler that turns them into JSON
        ├── schemas.py       Pydantic models (from session 3)
        ├── store.py         in-memory data (a database in session 5)
        ├── services.py      business rules, no HTTP
        ├── deps.py          dependencies: settings, services, paging, admin key
        └── routers/         thin HTTP layer: read the request, call a service

Why this split? Each file answers ONE question, so you know where to look.
It is not the only good structure -- but every file here will still exist,
with the same job, at the end of the course.

    python main.py
"""

import uvicorn

if __name__ == '__main__':
    uvicorn.run('app.main:app', reload=True)

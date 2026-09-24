"""Training Center API — the complete capstone (session 16 solution).

Everything of the course in one project:
    FastAPI, routers, Pydantic schemas, dependency injection, settings
    SQLAlchemy 2.x typed models + relationships, Alembic migrations (0001-0004)
    CRUD, pagination, filtering, sorting
    registration, Argon2 passwords, JWT, roles and ownership rules
    file uploads, CORS, middleware, async all the way
    tests/            pytest suite (API + units + the client)
    bruno/            the request collection
    client_app/       an async Python client and a small dashboard

New in the capstone:
    PATCH /users/me             change your own name (never your role)
    POST  /users/me/password    change your password (old one required)
    GET   /users/stats          admin numbers, computed with GROUP BY

    alembic upgrade head && python seed.py && python main.py
    pytest
    python -m client_app.main
"""

import uvicorn

if __name__ == '__main__':
    uvicorn.run('app.main:app', reload=True)

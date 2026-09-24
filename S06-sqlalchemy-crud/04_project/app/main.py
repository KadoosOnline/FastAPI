from fastapi import FastAPI

from app import models  # noqa: F401  (registers the tables on Base.metadata)
from app.config import get_settings
from app.database import Base, engine
from app.exceptions import register_exception_handlers
from app.routers import courses, enrollments, users


def create_app() -> FastAPI:
    # Create missing tables. Session 8 replaces this line with Alembic migrations.
    Base.metadata.create_all(engine)

    app = FastAPI(title=get_settings().app_name, version='5.0.0')
    register_exception_handlers(app)
    app.include_router(courses.router)
    app.include_router(users.router)
    app.include_router(enrollments.router)
    return app


app = create_app()

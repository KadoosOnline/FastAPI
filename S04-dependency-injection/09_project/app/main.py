from fastapi import FastAPI

from app.config import get_settings
from app.exceptions import register_exception_handlers
from app.routers import courses, enrollments, users


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version='3.0.0')
    register_exception_handlers(app)
    app.include_router(courses.router)
    app.include_router(users.router)
    app.include_router(enrollments.router)
    return app


app = create_app()

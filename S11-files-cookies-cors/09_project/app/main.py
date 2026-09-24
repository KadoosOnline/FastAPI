import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.exceptions import register_exception_handlers
from app.routers import auth, courses, enrollments, materials, users


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version='10.0.0')

    # Browsers on these origins may call the API (see example 07_cors).
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
        expose_headers=['X-Request-ID', 'X-Process-Time'],
    )

    @app.middleware('http')
    async def request_id_and_timing(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        started = time.perf_counter()
        response = await call_next(request)
        response.headers['X-Request-ID'] = request.headers.get(
            'x-request-id', uuid.uuid4().hex[:12]
        )
        response.headers['X-Process-Time'] = f'{(time.perf_counter() - started) * 1000:.1f}ms'
        return response

    register_exception_handlers(app)
    for module in (auth, courses, users, enrollments, materials):
        app.include_router(module.router)
    return app


app = create_app()

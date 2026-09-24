"""Custom exception handlers: business errors become HTTP answers in ONE place.

In session 1 our service raised `NotFoundError`, `ConflictError`... The
service must not know about HTTP. So we teach FastAPI how to translate:

    @app.exception_handler(AppError)
    def handle(request, error): return JSONResponse(status_code=..., content=...)

Now any code, however deep, can `raise NotFoundError(...)`, and the client
always receives the same JSON shape: {"detail": "...", "code": "not_found"}.
"""

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    status_code = 400
    code = 'app_error'

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(AppError):
    status_code = 404
    code = 'not_found'


class ConflictError(AppError):
    status_code = 409
    code = 'conflict'


app = FastAPI()


@app.exception_handler(AppError)
def handle_app_error(request: Request, error: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=error.status_code, content={'detail': error.message, 'code': error.code}
    )


# --- business code: no HTTP anywhere ---
ENROLLED = {(1, 2)}


def enroll(student_id: int, course_id: int) -> None:
    if course_id > 10:
        raise NotFoundError(f'Course {course_id} not found')
    if (student_id, course_id) in ENROLLED:
        raise ConflictError('Already enrolled')
    ENROLLED.add((student_id, course_id))


@app.post('/courses/{course_id}/students/{student_id}', status_code=201)
def enroll_endpoint(course_id: int, student_id: int) -> dict[str, int]:
    enroll(student_id, course_id)
    return {'student_id': student_id, 'course_id': course_id}


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)

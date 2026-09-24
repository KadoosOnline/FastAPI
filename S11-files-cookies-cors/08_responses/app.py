"""Response types beyond JSON, and controlling the response.

    JSONResponse(content, status_code=..., headers=...)   full control
    RedirectResponse('/new-url', status_code=307)          "go over there"
    PlainTextResponse('ok')                                text/plain
    HTMLResponse('<h1>..</h1>')                            text/html
    StreamingResponse(generator, media_type='text/csv')    send while producing
    status_code=202                                        "accepted, will do it later"
    response_model_exclude_none=True                       drop null fields

The CSV export streams rows from a GENERATOR (session 1): even a huge table
never has to fit in memory.
"""

import csv
import io
from collections.abc import Iterator

import uvicorn
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse, PlainTextResponse, RedirectResponse, StreamingResponse
from pydantic import BaseModel

app = FastAPI()
COURSES = [
    {'id': 1, 'title': 'Python', 'price': 2_500_000, 'note': None},
    {'id': 2, 'title': 'FastAPI', 'price': 4_800_000, 'note': 'full'},
]


class Course(BaseModel):
    id: int
    title: str
    price: int
    note: str | None = None


@app.get('/courses', response_model_exclude_none=True)
def list_courses() -> list[Course]:
    return [Course(**c) for c in COURSES]  # the null `note` disappears from the JSON


@app.get('/old-courses')
def old_address() -> RedirectResponse:
    return RedirectResponse('/courses', status_code=status.HTTP_308_PERMANENT_REDIRECT)


@app.get('/ping', response_class=PlainTextResponse)
def ping() -> str:
    return 'pong'


@app.post('/reports', status_code=status.HTTP_202_ACCEPTED)
def start_report() -> JSONResponse:
    return JSONResponse({'status': 'queued'}, status_code=202, headers={'Location': '/reports/42'})


def csv_rows() -> Iterator[str]:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(['id', 'title', 'price'])
    for course in COURSES:
        writer.writerow([course['id'], course['title'], course['price']])
        yield buffer.getvalue()
        buffer.seek(0)
        buffer.truncate()
    yield buffer.getvalue()


@app.get('/courses.csv')
def export_csv() -> StreamingResponse:
    return StreamingResponse(
        csv_rows(),
        media_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="courses.csv"'},
    )


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)

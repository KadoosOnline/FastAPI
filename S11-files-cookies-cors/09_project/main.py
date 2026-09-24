"""Training Center API — version 10 (session 11 project): files, headers, CORS.

New since session 10:
* CourseMaterial model (migration 0004) + app/storage.py (safe local storage)
* POST   /courses/{id}/materials      multipart upload: file + title (admin or the instructor)
                                      white-listed types, magic bytes checked, size limit
* GET    /courses/{id}/materials      staff of the course or its students
* GET    /materials/{id}/download     FileResponse with the original file name
* DELETE /materials/{id}              removes the row AND the file
* CORS for the origins in CORS_ORIGINS; X-Request-ID and X-Process-Time on every response

    alembic upgrade head
    python seed.py
    python main.py
"""

import uvicorn

if __name__ == '__main__':
    uvicorn.run('app.main:app', reload=True)

"""Training Center API — version 4 (session 5 project): a real database.

New since session 4:
    app/database.py   engine, SessionLocal, Base, get_db
    app/models.py     User, Course, Enrollment (typed SQLAlchemy 2.x models)
    seed.py           demo data
    store.py          gone! services now receive a Session

Create and read work for courses, users and enrollments. Updating and
deleting with SQLAlchemy is the subject of session 6.

    python seed.py
    python main.py
"""

import uvicorn

if __name__ == '__main__':
    uvicorn.run('app.main:app', reload=True)

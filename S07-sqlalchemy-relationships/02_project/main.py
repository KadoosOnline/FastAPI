"""Training Center API — version 6 (session 7 project): relationships.

New since session 6:
* models.py: relationship() + back_populates on User, Course, Enrollment
* GET /courses/{id}                 course + instructor in ONE query (joinedload)
                                    + number of active students
* GET /courses/{id}/students        students of a course, one JOIN query
* GET /users/{id}/enrollments       a student's courses, selectinload (2 queries, not 1+N)
* POST /users/{id}/enrollments      enroll in several courses: all or nothing
* GET /users/{id}/courses-taught    an instructor's courses through the relationship

Set DATABASE_ECHO=true in .env to watch the SQL of every request.

    python seed.py
    python main.py
"""

import uvicorn

if __name__ == '__main__':
    uvicorn.run('app.main:app', reload=True)

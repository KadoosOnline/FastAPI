"""Training Center API — version 9 (session 10 project): JWT and roles.

New since session 9:
* POST /auth/token returns a signed JWT access token (PyJWT, app/security.py)
* get_current_user + CurrentUser; require_roles() -> AdminUser, StaffUser, StudentUser
* The X-API-Key is gone. Who may do what:
      browse courses                      everybody
      create a course                     admin (chooses the instructor) or instructor (own)
      change a course                     admin, or the instructor OF THAT course
      delete a course, manage users       admin
      see the students of a course        admin, or its instructor
      enroll / cancel                     the logged-in student, for themself
      /users/me ...                       any logged-in user

    alembic upgrade head
    python seed.py
    python main.py      then click "Authorize" in /docs
"""

import uvicorn

if __name__ == '__main__':
    uvicorn.run('app.main:app', reload=True)

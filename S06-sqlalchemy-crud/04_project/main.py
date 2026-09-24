"""Training Center API — version 5 (session 6 project): full CRUD on the database.

New since session 5:
* courses: PUT (replace), PATCH (change part), DELETE, and search with
  q / level / min_price / max_price / is_active
* users: PATCH and DELETE (409 while the user still teaches a course)
* enrollments: DELETE cancels (status = cancelled); enrolling again re-activates
* business checks first (friendly 404 / 409 / 400), and an IntegrityError
  handler as the last safety net

    python seed.py
    python main.py
"""

import uvicorn

if __name__ == '__main__':
    uvicorn.run('app.main:app', reload=True)

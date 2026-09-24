"""Training Center API — version 7 (session 8 project): migrations and a real list API.

New since session 7:
* Alembic: `alembic/` + `alembic.ini`; tables are created by migrations, not create_all
      0001_initial_tables        users, courses, enrollments
      0002_add_course_start_date a new nullable column (schema evolution)
* GET /courses returns a Page: {items, total, page, size, pages}
      search   ?q=python
      filters  ?level= &instructor_id= &min_price= &max_price= &starts_after= &is_active=
      sort     ?sort=price | -price | title | -title | start_date | -start_date | id | -id
* GET /users is paginated too, with the same generic Page[T] and paginate()

    alembic upgrade head
    python seed.py
    python main.py
"""

import uvicorn

if __name__ == '__main__':
    uvicorn.run('app.main:app', reload=True)

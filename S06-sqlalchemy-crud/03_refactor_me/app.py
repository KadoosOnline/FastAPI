"""REFACTOR ME: a CRUD API that "works" -- until two things go wrong.

Run it, try it in /docs, then read the list below and fix every problem
(exercise 9). Keep the same URLs.

1. ONE global session shared by every request. After a single failed
   commit (register the same email twice) the session is broken and EVERY
   following request fails with "PendingRollbackError". Use a `get_db`
   dependency with `yield` instead.
2. `search` glues user input into the SQL text: SQL injection.
   Try  /courses/search?q=%' OR is_hidden=1 --  and see the hidden course.
3. `get_course` loads ALL courses and loops in Python to find one.
4. A missing course returns 200 with {"error": ...}; delete returns
   {"ok": false}. Use real status codes (404, 204).
5. `update_course` takes a raw dict: no validation, and a client can change
   `id` or any column. Use a Pydantic schema and `exclude_unset=True`.
6. There is no response schema: every column is sent to the client.
"""

import uvicorn
from fastapi import FastAPI
from sqlalchemy import String, create_engine, select, text
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

engine = create_engine('sqlite:///refactor.db')


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)


class Course(Base):
    __tablename__ = 'courses'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    price: Mapped[int]
    is_hidden: Mapped[bool] = mapped_column(default=False)


Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
session = Session(engine)
session.add_all([Course(title='Python', price=1), Course(title='Secret', price=2, is_hidden=True)])
session.commit()

app = FastAPI()


@app.post('/users')
def register(email: str):
    user = User(email=email)
    session.add(user)
    session.commit()
    return {'id': user.id, 'email': user.email}


@app.get('/courses/search')
def search(q: str):
    sql = f"SELECT id, title FROM courses WHERE is_hidden = 0 AND title LIKE '%{q}%'"
    return [dict(row._mapping) for row in session.execute(text(sql))]


@app.get('/courses/{course_id}')
def get_course(course_id: int):
    for course in session.scalars(select(Course)).all():
        if course.id == course_id:
            return course.__dict__ | {'_sa_instance_state': None}
    return {'error': 'not found'}


@app.patch('/courses/{course_id}')
def update_course(course_id: int, data: dict):
    course = session.get(Course, course_id)
    for key, value in data.items():
        setattr(course, key, value)
    session.commit()
    return {'ok': True}


@app.delete('/courses/{course_id}')
def delete_course(course_id: int):
    course = session.get(Course, course_id)
    if course:
        session.delete(course)
        session.commit()
        return {'ok': True}
    return {'ok': False}


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)

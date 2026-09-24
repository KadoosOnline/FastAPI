"""Path parameters: a variable part of the URL.

    GET /courses/2      ->  course_id = 2

`course_id: int` is a type hint, and FastAPI uses it:
* `/courses/2`   -> converted to the int 2
* `/courses/abc` -> 422 Unprocessable Entity, with a clear error message.
  Our function is never even called.

A course that does not exist is the client's mistake: `HTTPException(404)`.
Never return 200 with {"error": ...} inside.

Order matters: `/courses/cheapest` must be declared BEFORE
`/courses/{course_id}`, otherwise "cheapest" is taken as a course id.
"""

import uvicorn
from fastapi import FastAPI, HTTPException

app = FastAPI()

COURSES = {
    1: {'id': 1, 'title': 'Python Basics', 'price': 2_500_000},
    2: {'id': 2, 'title': 'FastAPI', 'price': 4_800_000},
    3: {'id': 3, 'title': 'HTML and CSS', 'price': 1_900_000},
}


@app.get('/courses/cheapest')
def cheapest_course() -> dict:
    return min(COURSES.values(), key=lambda course: course['price'])


@app.get('/courses/{course_id}')
def get_course(course_id: int) -> dict:
    if course_id not in COURSES:
        raise HTTPException(status_code=404, detail=f'Course {course_id} not found')
    return COURSES[course_id]


@app.get('/users/{username}/courses/{course_id}')
def user_course(username: str, course_id: int) -> dict:
    """Two path parameters in one URL."""
    return {'username': username, 'course_id': course_id}


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)

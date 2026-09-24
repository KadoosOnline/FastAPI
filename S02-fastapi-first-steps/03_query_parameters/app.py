"""Query parameters: the part after `?` in the URL.

    GET /courses?level=beginner&max_price=3000000&limit=2

Any function parameter that is NOT in the path is a query parameter.
* with a default value  -> optional       (`limit: int = 10`)
* with `| None = None`  -> optional, "not given" is None
* without a default     -> required       (missing -> 422)

Path parameter = WHICH resource (`/courses/2`).
Query parameter = HOW to show a list (filter, sort, page).
"""

import uvicorn
from fastapi import FastAPI

app = FastAPI()

COURSES = [
    {'id': 1, 'title': 'Python Basics', 'price': 2_500_000, 'level': 'beginner'},
    {'id': 2, 'title': 'FastAPI', 'price': 4_800_000, 'level': 'advanced'},
    {'id': 3, 'title': 'HTML and CSS', 'price': 1_900_000, 'level': 'beginner'},
    {'id': 4, 'title': 'SQL', 'price': 2_900_000, 'level': 'intermediate'},
]


@app.get('/courses')
def list_courses(
    level: str | None = None,
    max_price: int | None = None,
    q: str | None = None,
    limit: int = 10,
) -> list[dict]:
    result = COURSES
    if level is not None:
        result = [c for c in result if c['level'] == level]
    if max_price is not None:
        result = [c for c in result if c['price'] <= max_price]
    if q:
        result = [c for c in result if q.lower() in c['title'].lower()]
    return result[:limit]


@app.get('/search')
def search(q: str) -> dict:
    """`q` has no default, so it is required: /search without ?q= gives 422."""
    return {'you searched for': q}


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)

"""Classes as dependencies, and services as dependencies.

Anything *callable* can be a dependency -- including a class. FastAPI reads
the parameters of its `__init__`:

    class CourseFilters:
        def __init__(self, level: str | None = None, max_price: int | None = None): ...

A more important use: a SERVICE object that holds the business logic.
The endpoint only asks for it:

    def list_courses(service: Annotated[CourseService, Depends(get_course_service)]): ...

The endpoint does not know how the service is built. Today it uses a list;
in session 5 it will use a database session -- and the endpoint will not
change. That is dependency inversion in practice.
"""

from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI

app = FastAPI()

COURSES = [
    {'title': 'Python Basics', 'price': 2_500_000, 'level': 'beginner'},
    {'title': 'FastAPI', 'price': 4_800_000, 'level': 'advanced'},
    {'title': 'HTML and CSS', 'price': 1_900_000, 'level': 'beginner'},
]


class CourseFilters:
    def __init__(self, level: str | None = None, max_price: int | None = None) -> None:
        self.level = level
        self.max_price = max_price

    def matches(self, course: dict) -> bool:
        if self.level and course['level'] != self.level:
            return False
        return self.max_price is None or course['price'] <= self.max_price


class CourseService:
    def __init__(self, storage: list[dict]) -> None:
        self.storage = storage

    def search(self, filters: CourseFilters) -> list[dict]:
        return [course for course in self.storage if filters.matches(course)]


def get_course_service() -> CourseService:
    return CourseService(COURSES)


@app.get('/courses')
def list_courses(
    filters: Annotated[CourseFilters, Depends()],  # Depends() = "use the type itself"
    service: Annotated[CourseService, Depends(get_course_service)],
) -> list[dict]:
    return service.search(filters)


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)

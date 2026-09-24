"""The N+1 query problem -- and how to see it and fix it.

Lazy loading is convenient: `course.enrollments` runs a SELECT the first time
you touch it. In a loop over N courses that is 1 query for the list + N
queries for the enrollments = N+1. With 1000 courses: 1001 round trips.

Fixes: tell the FIRST query to load the relationship too.
    selectinload(Course.enrollments)  -> 1 extra query: "... WHERE course_id IN (...)"
    joinedload(Course.instructor)     -> the same query, with a JOIN
                                         (best for many-to-one: one parent per row)

Note the first test: only 3 queries for 4 courses, because the session's
identity map remembers each instructor after loading it once. With many
different instructors it would be N+1 again.

We count the SQL statements with an engine event.
"""

from collections.abc import Callable

from sqlalchemy import event, select
from sqlalchemy.orm import Session, joinedload, selectinload

from models import Course, Enrollment, User, engine, reset_database

queries: list[str] = []


@event.listens_for(engine, 'before_cursor_execute')
def count_query(conn, cursor, statement, parameters, context, executemany) -> None:  # type: ignore[no-untyped-def]
    queries.append(statement)


def run(label: str, options: list, describe: Callable[[Course], str]) -> None:  # type: ignore[type-arg]
    queries.clear()
    with Session(engine) as session:
        courses = session.scalars(select(Course).options(*options)).all()
        lines = [describe(course) for course in courses]
    print(f'{label:<34} {len(queries)} queries   {lines[:2]} ...')


def main() -> None:
    reset_database()
    teacher = lambda c: f'{c.title} by {c.instructor.full_name}'  # noqa: E731
    size = lambda c: f'{c.title}: {len(c.enrollments)} students'  # noqa: E731

    run('instructor, lazy', [], teacher)
    run('instructor, joinedload', [joinedload(Course.instructor)], teacher)
    run('enrollments, lazy (N+1)', [], size)
    run('enrollments, selectinload', [selectinload(Course.enrollments)], size)

    # Two levels deep: every student -> enrollments -> course
    queries.clear()
    with Session(engine) as session:
        stmt = (
            select(User)
            .where(User.role == 'student')
            .options(selectinload(User.enrollments).selectinload(Enrollment.course))
        )
        for student in session.scalars(stmt):
            _ = [e.course.title for e in student.enrollments]
    print(f'{"students -> courses, nested":<34} {len(queries)} queries:')
    for sql in queries:
        print('   ', ' '.join(sql.split())[:90])


if __name__ == '__main__':
    main()

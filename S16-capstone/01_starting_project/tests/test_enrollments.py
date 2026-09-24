from collections.abc import Callable

import pytest
from httpx import AsyncClient

from app.models import User
from tests.conftest import CourseFactory, UserFactory

pytestmark = pytest.mark.anyio
Auth = Callable[[User], dict[str, str]]


async def test_student_enrolls_and_sees_it(
    client: AsyncClient, make_user: UserFactory, make_course: CourseFactory, auth: Auth
) -> None:
    teacher, student = await make_user('instructor'), await make_user('student')
    course = await make_course(teacher)

    response = await client.post(f'/courses/{course.id}/enrollments', headers=auth(student))
    mine = await client.get('/users/me/enrollments', headers=auth(student))

    assert response.status_code == 201
    assert [e['course']['title'] for e in mine.json()] == ['FastAPI']


async def test_enroll_twice_is_a_conflict(
    client: AsyncClient, make_user: UserFactory, make_course: CourseFactory, auth: Auth
) -> None:
    course = await make_course(await make_user('instructor'))
    student = await make_user('student')
    await client.post(f'/courses/{course.id}/enrollments', headers=auth(student))

    response = await client.post(f'/courses/{course.id}/enrollments', headers=auth(student))

    assert response.status_code == 409


async def test_full_course(
    client: AsyncClient, make_user: UserFactory, make_course: CourseFactory, auth: Auth
) -> None:
    course = await make_course(await make_user('instructor'), capacity=1)
    first, second = await make_user('student'), await make_user('student')

    assert (
        await client.post(f'/courses/{course.id}/enrollments', headers=auth(first))
    ).status_code == 201
    response = await client.post(f'/courses/{course.id}/enrollments', headers=auth(second))

    assert response.status_code == 409
    assert response.json()['detail'] == 'Course is full'


async def test_cancel_and_come_back(
    client: AsyncClient, make_user: UserFactory, make_course: CourseFactory, auth: Auth
) -> None:
    course = await make_course(await make_user('instructor'))
    student = await make_user('student')
    await client.post(f'/courses/{course.id}/enrollments', headers=auth(student))

    cancel = await client.delete(f'/courses/{course.id}/enrollments/me', headers=auth(student))
    again = await client.delete(f'/courses/{course.id}/enrollments/me', headers=auth(student))
    back = await client.post(f'/courses/{course.id}/enrollments', headers=auth(student))

    assert (cancel.status_code, again.status_code, back.status_code) == (204, 404, 201)


async def test_instructor_can_not_enroll(
    client: AsyncClient, make_user: UserFactory, make_course: CourseFactory, auth: Auth
) -> None:
    teacher = await make_user('instructor')
    course = await make_course(teacher)

    assert (
        await client.post(f'/courses/{course.id}/enrollments', headers=auth(teacher))
    ).status_code == 403


async def test_enroll_many_is_all_or_nothing(
    client: AsyncClient, make_user: UserFactory, make_course: CourseFactory, auth: Auth
) -> None:
    teacher = await make_user('instructor')
    open_course = await make_course(teacher, title='Open')
    full_course = await make_course(teacher, title='Full', capacity=1)
    await client.post(
        f'/courses/{full_course.id}/enrollments', headers=auth(await make_user('student'))
    )
    student = await make_user('student')

    response = await client.post(
        '/users/me/enrollments',
        json={'course_ids': [open_course.id, full_course.id]},
        headers=auth(student),
    )
    mine = await client.get('/users/me/enrollments', headers=auth(student))

    assert response.status_code == 409
    assert mine.json() == []  # the first enrollment was rolled back


async def test_students_list_is_for_the_owner_only(
    client: AsyncClient, make_user: UserFactory, make_course: CourseFactory, auth: Auth
) -> None:
    owner, other = await make_user('instructor'), await make_user('instructor')
    course = await make_course(owner)
    student = await make_user('student')
    await client.post(f'/courses/{course.id}/enrollments', headers=auth(student))

    mine = await client.get(f'/courses/{course.id}/students', headers=auth(owner))
    theirs = await client.get(f'/courses/{course.id}/students', headers=auth(other))

    assert [s['email'] for s in mine.json()] == [student.email]
    assert theirs.status_code == 403

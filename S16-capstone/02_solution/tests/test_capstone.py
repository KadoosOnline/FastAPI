"""Tests written during the capstone: new features and the bugs that were found."""

from collections.abc import Callable

import pytest
from httpx import AsyncClient

from app.models import User
from tests.conftest import PASSWORD, CourseFactory, UserFactory

pytestmark = pytest.mark.anyio
Auth = Callable[[User], dict[str, str]]


# ----- new features -----
async def test_update_me(client: AsyncClient, make_user: UserFactory, auth: Auth) -> None:
    user = await make_user('student')

    response = await client.patch('/users/me', json={'full_name': 'Sara A.'}, headers=auth(user))

    assert response.status_code == 200
    assert response.json()['full_name'] == 'Sara A.'


async def test_update_me_can_not_change_role(
    client: AsyncClient, make_user: UserFactory, auth: Auth
) -> None:
    user = await make_user('student')

    response = await client.patch(
        '/users/me', json={'full_name': 'Sneaky', 'role': 'admin'}, headers=auth(user)
    )

    assert response.json()['role'] == 'student'


async def test_change_password(client: AsyncClient, make_user: UserFactory, auth: Auth) -> None:
    user = await make_user('student', email='pw@example.com')

    wrong_old = await client.post(
        '/users/me/password',
        json={'old_password': 'nope', 'new_password': 'NewPass2026'},
        headers=auth(user),
    )
    weak_new = await client.post(
        '/users/me/password',
        json={'old_password': PASSWORD, 'new_password': 'weak'},
        headers=auth(user),
    )
    ok = await client.post(
        '/users/me/password',
        json={'old_password': PASSWORD, 'new_password': 'NewPass2026'},
        headers=auth(user),
    )
    login = await client.post(
        '/auth/token', data={'username': 'pw@example.com', 'password': 'NewPass2026'}
    )

    assert (wrong_old.status_code, weak_new.status_code, ok.status_code) == (401, 422, 204)
    assert login.status_code == 200


async def test_stats_for_admin_only(
    client: AsyncClient, make_user: UserFactory, make_course: CourseFactory, auth: Auth
) -> None:
    admin, teacher, student = (
        await make_user('admin'),
        await make_user('instructor'),
        await make_user('student'),
    )
    course = await make_course(teacher, title='Popular')
    await client.post(f'/courses/{course.id}/enrollments', headers=auth(student))

    forbidden = await client.get('/users/stats', headers=auth(teacher))
    response = await client.get('/users/stats', headers=auth(admin))

    assert forbidden.status_code == 403
    body = response.json()
    assert body['users_per_role'] == {'admin': 1, 'instructor': 1, 'student': 1}
    assert body['active_courses'] == 1
    assert body['top_courses'] == [{'title': 'Popular', 'students': 1}]


# ----- rules that were broken in the capstone's starting version -----
async def test_disabled_user_token_stops_working(
    client: AsyncClient, make_user: UserFactory, auth: Auth
) -> None:
    admin, student = await make_user('admin'), await make_user('student')
    headers = auth(student)
    assert (await client.get('/users/me', headers=headers)).status_code == 200

    await client.patch(f'/users/{student.id}', json={'is_active': False}, headers=auth(admin))

    assert (await client.get('/users/me', headers=headers)).status_code == 403


async def test_cancelled_student_loses_the_materials(
    client: AsyncClient, make_user: UserFactory, make_course: CourseFactory, auth: Auth
) -> None:
    teacher, student = await make_user('instructor'), await make_user('student')
    course = await make_course(teacher)
    await client.post(f'/courses/{course.id}/enrollments', headers=auth(student))
    assert (
        await client.get(f'/courses/{course.id}/materials', headers=auth(student))
    ).status_code == 200

    await client.delete(f'/courses/{course.id}/enrollments/me', headers=auth(student))

    assert (
        await client.get(f'/courses/{course.id}/materials', headers=auth(student))
    ).status_code == 403


async def test_min_price_filter(
    client: AsyncClient, make_user: UserFactory, make_course: CourseFactory
) -> None:
    teacher = await make_user('instructor')
    await make_course(teacher, title='Cheap', price=100)
    await make_course(teacher, title='Expensive', price=900)

    body = (await client.get('/courses', params={'min_price': 500})).json()

    assert [c['title'] for c in body['items']] == ['Expensive']


async def test_capacity_can_not_be_negative_in_patch(
    client: AsyncClient, make_user: UserFactory, make_course: CourseFactory, auth: Auth
) -> None:
    teacher = await make_user('instructor')
    course = await make_course(teacher)

    response = await client.patch(
        f'/courses/{course.id}', json={'capacity': -3}, headers=auth(teacher)
    )

    assert response.status_code == 422


async def test_second_page_starts_after_the_first(
    client: AsyncClient, make_user: UserFactory, make_course: CourseFactory
) -> None:
    teacher = await make_user('instructor')
    for number in range(5):
        await make_course(teacher, title=f'Course {number}')

    first = (await client.get('/courses', params={'size': 2, 'page': 1, 'sort': 'title'})).json()
    second = (await client.get('/courses', params={'size': 2, 'page': 2, 'sort': 'title'})).json()

    assert [c['title'] for c in first['items']] == ['Course 0', 'Course 1']
    assert [c['title'] for c in second['items']] == ['Course 2', 'Course 3']

from collections.abc import Callable

import pytest
from httpx import AsyncClient

from app.models import User
from tests.conftest import CourseFactory, UserFactory

pytestmark = pytest.mark.anyio
Auth = Callable[[User], dict[str, str]]
NEW_COURSE = {'title': 'Git', 'price': 3_000_000, 'capacity': 15}


async def test_anybody_can_browse(
    client: AsyncClient, make_user: UserFactory, make_course: CourseFactory
) -> None:
    teacher = await make_user('instructor')
    await make_course(teacher, title='Python')
    await make_course(teacher, title='FastAPI')

    response = await client.get('/courses', params={'sort': 'title'})

    assert response.status_code == 200
    body = response.json()
    assert body['total'] == 2
    assert [c['title'] for c in body['items']] == ['FastAPI', 'Python']


async def test_instructor_creates_own_course(
    client: AsyncClient, make_user: UserFactory, auth: Auth
) -> None:
    teacher = await make_user('instructor')

    response = await client.post('/courses', json=NEW_COURSE, headers=auth(teacher))

    assert response.status_code == 201
    assert response.json()['instructor_id'] == teacher.id


async def test_student_can_not_create(
    client: AsyncClient, make_user: UserFactory, auth: Auth
) -> None:
    student = await make_user('student')

    response = await client.post('/courses', json=NEW_COURSE, headers=auth(student))

    assert response.status_code == 403


async def test_anonymous_can_not_create(client: AsyncClient) -> None:
    assert (await client.post('/courses', json=NEW_COURSE)).status_code == 401


async def test_admin_must_choose_an_instructor(
    client: AsyncClient, make_user: UserFactory, auth: Auth
) -> None:
    admin, teacher = await make_user('admin'), await make_user('instructor')

    without = await client.post('/courses', json=NEW_COURSE, headers=auth(admin))
    with_id = await client.post(
        '/courses', json=NEW_COURSE | {'instructor_id': teacher.id}, headers=auth(admin)
    )

    assert without.status_code == 400
    assert with_id.status_code == 201


async def test_only_the_owner_edits(
    client: AsyncClient, make_user: UserFactory, make_course: CourseFactory, auth: Auth
) -> None:
    owner, other = await make_user('instructor'), await make_user('instructor')
    course = await make_course(owner)

    by_other = await client.patch(f'/courses/{course.id}', json={'price': 1}, headers=auth(other))
    by_owner = await client.patch(f'/courses/{course.id}', json={'price': 1}, headers=auth(owner))

    assert by_other.status_code == 403
    assert by_owner.status_code == 200
    assert by_owner.json()['price'] == 1


async def test_only_admin_deletes(
    client: AsyncClient, make_user: UserFactory, make_course: CourseFactory, auth: Auth
) -> None:
    owner, admin = await make_user('instructor'), await make_user('admin')
    course = await make_course(owner)

    assert (await client.delete(f'/courses/{course.id}', headers=auth(owner))).status_code == 403
    assert (await client.delete(f'/courses/{course.id}', headers=auth(admin))).status_code == 204
    assert (await client.get(f'/courses/{course.id}')).status_code == 404


@pytest.mark.parametrize(
    'params',
    [
        {'size': 0},
        {'size': 500},
        {'sort': 'popularity'},
        {'min_price': 9, 'max_price': 1},
        {'levle': 'x'},
    ],
)
async def test_bad_list_parameters(client: AsyncClient, params: dict) -> None:
    assert (await client.get('/courses', params=params)).status_code == 422


@pytest.mark.parametrize(
    ('body', 'status'),
    [({'title': 'ab'}, 422), ({'price': -1}, 422), ({}, 422), ({'title': None}, 422)],
)
async def test_patch_validation(
    client: AsyncClient,
    make_user: UserFactory,
    make_course: CourseFactory,
    auth: Auth,
    body: dict,
    status: int,
) -> None:
    owner = await make_user('instructor')
    course = await make_course(owner)

    response = await client.patch(f'/courses/{course.id}', json=body, headers=auth(owner))

    assert response.status_code == status

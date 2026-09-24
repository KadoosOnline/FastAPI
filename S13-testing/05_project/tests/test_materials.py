from collections.abc import Callable

import pytest
from httpx import AsyncClient

from app.models import User
from tests.conftest import CourseFactory, UserFactory

pytestmark = pytest.mark.anyio
Auth = Callable[[User], dict[str, str]]
PDF = b'%PDF-1.4\n% test\n%%EOF\n'


async def test_upload_list_download(
    client: AsyncClient, make_user: UserFactory, make_course: CourseFactory, auth: Auth
) -> None:
    teacher, student = await make_user('instructor'), await make_user('student')
    course = await make_course(teacher)
    await client.post(f'/courses/{course.id}/enrollments', headers=auth(student))

    upload = await client.post(
        f'/courses/{course.id}/materials',
        data={'title': 'Syllabus'},
        files={'file': ('syllabus.pdf', PDF, 'application/pdf')},
        headers=auth(teacher),
    )
    listing = await client.get(f'/courses/{course.id}/materials', headers=auth(student))
    download = await client.get(f'/materials/{upload.json()["id"]}/download', headers=auth(student))

    assert upload.status_code == 201
    assert [m['title'] for m in listing.json()] == ['Syllabus']
    assert download.content == PDF
    assert 'syllabus.pdf' in download.headers['content-disposition']


@pytest.mark.parametrize(
    ('filename', 'content', 'content_type', 'status'),
    [
        ('fake.pdf', b'not a pdf', 'application/pdf', 415),
        ('virus.exe', b'MZ', 'application/x-msdownload', 415),
        ('big.txt', b'a' * (1024 * 1024 + 1), 'text/plain', 413),
    ],
    ids=['lying-type', 'forbidden-type', 'too-big'],
)
async def test_upload_is_validated(
    client: AsyncClient,
    make_user: UserFactory,
    make_course: CourseFactory,
    auth: Auth,
    filename: str,
    content: bytes,
    content_type: str,
    status: int,
) -> None:
    teacher = await make_user('instructor')
    course = await make_course(teacher)

    response = await client.post(
        f'/courses/{course.id}/materials',
        data={'title': 'Some file'},
        files={'file': (filename, content, content_type)},
        headers=auth(teacher),
    )

    assert response.status_code == status


async def test_outsiders_can_not_read(
    client: AsyncClient, make_user: UserFactory, make_course: CourseFactory, auth: Auth
) -> None:
    course = await make_course(await make_user('instructor'))
    outsider = await make_user('student')

    assert (
        await client.get(f'/courses/{course.id}/materials', headers=auth(outsider))
    ).status_code == 403

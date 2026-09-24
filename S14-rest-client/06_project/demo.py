"""Use the client against the real API.

Terminal 1 (the server of session 13):
    cd ../../S13-testing/05_project
    alembic upgrade head && python seed.py && python main.py
Terminal 2:
    python demo.py
"""

import uuid

from clients import (
    ApiConnectionError,
    ApiError,
    ConflictError,
    PermissionDenied,
    TrainingCenterClient,
)

API = 'http://127.0.0.1:8000'


def main() -> None:
    with TrainingCenterClient(API) as api:
        print('Catalogue (all pages, cheapest first):')
        for course in api.iter_courses(sort='price', size=2):
            print(f'  #{course.id:<3} {course.title:<22} {course.price:>12,} Toman')

        email = f'demo_{uuid.uuid4().hex[:6]}@example.com'
        user = api.register(email, 'Demo Student', 'Secret2026')
        api.login(email, 'Secret2026')
        print(f'\nRegistered and logged in as {api.me().full_name} ({user.role})')

        enrollment = api.enroll(1)
        print(f'Enrolled in course {enrollment.course_id}: {enrollment.status}')
        try:
            api.enroll(1)
        except ConflictError as error:
            print(f'Second time -> {error.status_code}: {error.detail}')
        try:
            api.create_course(title='Not allowed', price=1, capacity=1)
        except PermissionDenied as error:
            print(f'Student creates a course -> {error.status_code}: {error.detail}')

        api.logout()
        api.login('teacher@kadoos.ir', 'Password123')
        course = api.create_course(title=f'Client Course {user.id}', price=990_000, capacity=5)
        course = api.update_course(course.id, price=1_200_000)
        print(f'\nTeacher created #{course.id} and changed its price to {course.price:,}')
        print('Detail:', api.get_course(course.id).instructor)


if __name__ == '__main__':
    try:
        main()
    except ApiConnectionError as error:
        print(f'The API is not running? {error}')
    except ApiError as error:
        print(f'Unexpected API error: {error}')

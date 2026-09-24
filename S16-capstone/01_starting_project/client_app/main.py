"""A small "teacher dashboard" that uses the Training Center API.

    python -m client_app.main
    python -m client_app.main --email teacher2@kadoos.ir --new-course "Git Basics"
    python -m client_app.main --email sara@example.com          (the student view)

It authenticates, receives a JWT, stores and uses it, reads protected data
concurrently, creates and updates a course, and turns every failure into a
clear message instead of a traceback. The API of session 13 must be running.
"""

import argparse
import asyncio
import sys

from client_app.api_client import (
    ApiError,
    ApiUnavailable,
    AuthenticationFailed,
    Conflict,
    PermissionDenied,
    TrainingCenterApi,
)


async def dashboard(args: argparse.Namespace) -> None:
    async with TrainingCenterApi(args.base_url) as api:
        await api.login(args.email, args.password)
        me = await api.me()
        print(f'Hello {me.full_name} ({me.role})\n')
        # TODO (capstone): a student view -- my courses + enroll in the cheapest free course

        courses = [course async for course in api.all_courses(instructor_id=me.id, sort='title')]
        students = await api.students_of_many([course.id for course in courses])
        print(f'{"course":<24}{"price":>12}{"seats":>9}')
        for course in courses:
            active = sum(s.status == 'active' for s in students[course.id])
            print(f'{course.title:<24}{course.price:>12,}{active:>5}/{course.capacity:<3}')

        if args.new_course:
            try:
                course = await api.create_course(
                    title=args.new_course, price=2_000_000, capacity=12
                )
                course = await api.update_course(course.id, price=2_200_000)
                print(f'\ncreated #{course.id} {course.title!r} for {course.price:,} Toman')
            except Conflict as error:
                print(f'\nnot created: {error.detail}')


def main() -> int:
    parser = argparse.ArgumentParser(description='Teacher dashboard for the Training Center API')
    parser.add_argument('--base-url', default='http://127.0.0.1:8000')
    parser.add_argument('--email', default='teacher@kadoos.ir')
    parser.add_argument('--password', default='Password123')
    parser.add_argument('--new-course', default=None, help='title of a course to create')
    args = parser.parse_args()
    try:
        asyncio.run(dashboard(args))
    except ApiUnavailable:
        print('The API does not answer. Is the server running?', file=sys.stderr)
    except AuthenticationFailed:
        print('Wrong e-mail or password.', file=sys.stderr)
    except PermissionDenied as error:
        print(f'Not allowed: {error.detail}', file=sys.stderr)
    except ApiError as error:
        print(f'The API refused the request: {error}', file=sys.stderr)
    else:
        return 0
    return 1


if __name__ == '__main__':
    raise SystemExit(main())

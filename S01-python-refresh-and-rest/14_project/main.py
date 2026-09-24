"""Session 1 project: run the Training Center core end to end.

python main.py
"""

import logging

from training_center.exceptions import TrainingCenterError
from training_center.models import Course, Role, User
from training_center.reports import format_report, report_lines, total_revenue
from training_center.repository import InMemoryRepository
from training_center.services import TrainingCenterService
from training_center.transactions import transaction


def main() -> None:
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')

    users: InMemoryRepository[User] = InMemoryRepository('User')
    courses: InMemoryRepository[Course] = InMemoryRepository('Course')
    service = TrainingCenterService(users, courses)

    teacher = service.register_user('teacher@kadoos.ir', 'Ali Teacher', Role.INSTRUCTOR)
    sara = service.register_user('sara@example.com', 'Sara Ahmadi')
    reza = service.register_user('reza@example.com', 'Reza Karimi')

    python = service.create_course(teacher.id, title='Python', price=2_500_000, capacity=20)
    fastapi = service.create_course(teacher.id, title='FastAPI', price=4_800_000, capacity=1)

    service.enroll(sara.id, python.id)
    service.enroll(reza.id, python.id)
    service.enroll(sara.id, fastapi.id)

    # Every business rule failure is a TrainingCenterError subclass.
    for student_id, course_id in [(reza.id, fastapi.id), (sara.id, python.id), (sara.id, 99)]:
        try:
            service.enroll(student_id, course_id)
        except TrainingCenterError as error:
            print(f'refused -> {type(error).__name__}: {error}')

    # Students can not create courses.
    try:
        service.create_course(sara.id, title='Hacking', price=0, capacity=5)
    except TrainingCenterError as error:
        print(f'refused -> {type(error).__name__}: {error}')

    # All-or-nothing: the half-finished registration is rolled back.
    try:
        with transaction(users, courses):
            service.register_user('temp@example.com', 'Temporary')
            raise RuntimeError('the payment gateway failed')
    except RuntimeError:
        print(f'rolled back: still {len(users)} users')

    print([student.full_name for student in service.students_of(python.id)])
    print([course.title for course in service.search_courses('py', max_price=3_000_000)])

    lines = list(report_lines(courses))
    print(format_report(lines))
    print(f'total revenue: {total_revenue(lines):,} IRT')


if __name__ == '__main__':
    main()

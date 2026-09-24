"""Custom exceptions: name your errors after your business.

A service should never return `None` or `-1` or `"error"` to say "that went
wrong". It raises an exception that says exactly WHAT went wrong:

    TrainingCenterError            <- catch all of ours at once
    ├── NotFoundError              <- later becomes HTTP 404
    ├── ConflictError              <- later becomes HTTP 409 (duplicate, full)
    └── PermissionDeniedError      <- later becomes HTTP 403

In session 4 we register ONE exception handler in FastAPI that turns these
into HTTP responses. The business code will never know about HTTP -- that is
separation of concerns.

Also shown here:
* extra attributes on an exception (`entity`, `entity_id`)
* `raise ... from error` -- keep the original cause in the traceback
* `raise ... from None` -- hide an irrelevant internal cause (KeyError)
* `try / except / else / finally`
"""

from dataclasses import dataclass, field


class TrainingCenterError(Exception):
    """Base class of all our expected errors."""

    status_code = 400


class NotFoundError(TrainingCenterError):
    status_code = 404

    def __init__(self, entity: str, entity_id: int) -> None:
        super().__init__(f'{entity} {entity_id} was not found')
        self.entity = entity
        self.entity_id = entity_id


class ConflictError(TrainingCenterError):
    status_code = 409


class PermissionDeniedError(TrainingCenterError):
    status_code = 403


@dataclass
class Course:
    id: int
    title: str
    capacity: int
    students: set[int] = field(default_factory=set)


COURSES = {1: Course(1, 'FastAPI', capacity=1)}


def get_course(course_id: int) -> Course:
    try:
        return COURSES[course_id]
    except KeyError:
        # The KeyError is an implementation detail: hide it.
        raise NotFoundError('Course', course_id) from None


def enroll(student_id: int, course_id: int) -> None:
    course = get_course(course_id)
    if student_id in course.students:
        raise ConflictError(f'student {student_id} is already enrolled')
    if len(course.students) >= course.capacity:
        raise ConflictError(f'course {course.title!r} is full')
    course.students.add(student_id)


def load_price(text: str) -> int:
    try:
        return int(text)
    except ValueError as error:
        # Keep the cause: the traceback will show both errors.
        raise TrainingCenterError(f'invalid price {text!r}') from error


def main() -> None:
    attempts = [(1, 1), (1, 1), (2, 1), (1, 42)]
    for student_id, course_id in attempts:
        try:
            enroll(student_id, course_id)
        except NotFoundError as error:
            print(f'[{error.status_code}] missing {error.entity}: {error}')
        except TrainingCenterError as error:
            print(f'[{error.status_code}] {type(error).__name__}: {error}')
        else:
            print(f'student {student_id} enrolled in course {course_id}')
        finally:
            print('   (attempt logged)')

    try:
        load_price('12,000')
    except TrainingCenterError as error:
        print(error, '<- caused by', repr(error.__cause__))


if __name__ == '__main__':
    main()

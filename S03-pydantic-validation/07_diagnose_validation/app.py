"""Diagnose it: will each payload pass or fail, and WHY?

Before running this file, write your prediction for every case on paper
(pass / fail + which field). Then run it and compare. Exercise 7 asks you to
explain the surprising ones.

Hints: Pydantic's default ("lax") mode converts values when it is safe;
`strict=True` on a field turns conversion off.
"""

from pydantic import BaseModel, Field, ValidationError


class Enrollment(BaseModel):
    student_id: int
    course_id: int = Field(gt=0)
    paid: bool = False
    amount: int = Field(default=0, ge=0)
    note: str | None = None
    strict_code: int | None = Field(default=None, strict=True)


CASES = [
    {'student_id': 1, 'course_id': 2},
    {'student_id': '1', 'course_id': '2'},
    {'student_id': 1.0, 'course_id': 2},
    {'student_id': 1.5, 'course_id': 2},
    {'student_id': 1, 'course_id': 0},
    {'student_id': 1, 'course_id': 2, 'paid': 'yes'},
    {'student_id': 1, 'course_id': 2, 'paid': 'maybe'},
    {'student_id': 1, 'course_id': 2, 'amount': '-1'},
    {'student_id': 1, 'course_id': 2, 'note': 42},
    {'student_id': 1, 'course_id': 2, 'strict_code': '7'},
    {'student_id': 1, 'course_id': 2, 'unknown_field': 'x'},
    {'course_id': 2},
]


def main() -> None:
    for number, case in enumerate(CASES, start=1):
        try:
            result = Enrollment(**case)
            print(f'{number:>2}. PASS  {case}  ->  {result.model_dump(exclude_defaults=True)}')
        except ValidationError as error:
            reasons = '; '.join(f'{e["loc"][0]}: {e["msg"]}' for e in error.errors())
            print(f'{number:>2}. FAIL  {case}  ->  {reasons}')


if __name__ == '__main__':
    main()

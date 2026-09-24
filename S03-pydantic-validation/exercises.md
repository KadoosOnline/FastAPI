# Session 03 — Exercises

## Reading errors
1. In `01_basemodel`, create a `Course` from `{"id": "7.0", "title": 12, "price": "4,800,000"}`.
   Predict the result for each field before running.
2. Add `model_config = ConfigDict(extra='forbid')` to `Course`. What changes
   for a payload with an unknown field? When is that useful?

## Rules
3. In `02_field_constraints`, add `start_date: date` that must be in the future
   (a `field_validator`), and `hours: int` between 3 and 120.
4. Write `Phone = Annotated[str, Field(pattern=...)]` for Iranian mobile numbers
   (`09` + 9 digits) and use it in a `StudentProfile` model.
5. In `05_custom_validators`, add `password_repeat` to `UserCreate` and check
   with a `model_validator` that both passwords are equal.

## Diagnose
6. Run `07_diagnose_validation` *after* writing your predictions. For every case
   you got wrong, write one sentence that explains Pydantic's decision.
7. Case 11 passes although it contains an unknown field. Change the model so it
   fails. Case 10 fails although `'7'` looks like a number. Why?
8. A student says: "my PATCH sets the description to null when I only send the
   price". Show the bug with `model_dump()` and fix it with `exclude_unset=True`.

## The project
9. Add `CourseDetail(CourseRead)` with a nested `instructor: UserRead` and return
   it from `GET /courses/{course_id}`.
10. Add `@computed_field seats_left` to the course that `GET /courses/{id}`
    returns (count the active enrollments).
11. Add `PUT /courses/{course_id}` with a `CourseReplace` schema. Which fields
    must it contain, and why is `instructor_id` a special case?
12. Make `?max_price=` refuse negative numbers. (Hint: `Annotated[int | None, Query(ge=0)]`.)
13. Add `DELETE /courses/{course_id}/enrollments/{student_id}` that sets the
    status to `cancelled` (404 if there is no active enrollment).
14. Add one Bruno request for every new endpoint, plus one failing request
    for every new validation rule.

## To think about
15. Why must `UserCreate` never have a `role` field in a *public* registration
    endpoint? (Session 9 comes back to this.)
16. `CourseRead` has `created_at`, `CourseCreate` does not. Who sets it, and why
    must the client not be able to?
17. Is validation in the Pydantic model enough, or does the database (session 5)
    need its own rules too?

## Homework
Extend your **Library API** from the last homework with schemas: `BookCreate`,
`BookUpdate`, `BookRead` and `MemberCreate` / `MemberRead`. Rules: ISBN of 10
or 13 digits, year between 1450 and the current year, a real e-mail for
members, and a `model_validator` that refuses a book whose `pages` is smaller
than its `chapters`. Return only `Read` models from every endpoint and add a
failing Bruno request for every rule.

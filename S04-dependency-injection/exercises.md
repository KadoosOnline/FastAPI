# Session 04 — Exercises

## Dependencies
1. In `01_depends_basics`, make `pagination` refuse `page=0` with a 422
   instead of silently fixing it. (Hint: `Annotated[int, Query(ge=1)]`.)
2. In `02_annotated_dependencies`, add a dependency `get_request_id` that
   returns a new `uuid4()` string, use it in the endpoint *and* inside
   `get_paging`, and prove that both receive the same value.
3. In `03_class_dependencies`, add `sort: str = 'title'` to `CourseFilters`
   and make the service sort by `title` or `price`.
4. In `04_yield_dependencies`, make `/fail` raise a `ZeroDivisionError`
   instead. Is the rollback still printed? What does the client receive?

## Headers, cookies, errors
5. In `05_headers_and_cookies`, add `POST /logout` that deletes the `theme`
   cookie (`response.delete_cookie`). Check it in Bruno's cookie tab.
6. Make `get_caller` return a small dataclass `Caller(name, is_admin)` and
   allow `DELETE` only for admins (403 for teachers).
7. In `06_exception_handlers`, add `CourseFullError` with status 409 and code
   `course_full`. Do you need a new handler? Why not?

## Settings
8. In `07_settings`, add `allowed_origins: list[str]` and set it from `.env` as
   a JSON list. Start the app without `SECRET_KEY` and read the error.

## The project
9. Trace `POST /courses/2/enrollments` through the project: write down every
   file and function that runs, in order.
10. Add `GET /users/{user_id}/enrollments` (which router? which service?).
11. Add `DELETE /courses/{course_id}/enrollments/{student_id}` that cancels an
    enrollment; a missing enrollment is a `NotFoundError` raised by the service.
12. Move the "a student can not enroll in more than 3 courses" rule into
    `EnrollmentService` and raise `BusinessRuleError`. Add a Bruno request that
    breaks the rule.
13. Add a `X-Process-Time` header to every response with a middleware or an
    app-level dependency. Which one works, and why?
14. Replace `store = Store()` in a test script by a fresh `Store()` using
    `app.dependency_overrides[get_store] = ...`. (Session 13 relies on this.)

## To think about
15. The routers contain no `if`. Where did all the decisions go, and why is
    that good?
16. Why does `CourseService` not raise `HTTPException`?
17. `AdminOnly` checks a fixed key from `.env`. List three problems with this
    kind of authentication (sessions 9 and 10 solve them).

## Homework
Refactor your **Library API** into the same structure (`config.py`,
`exceptions.py`, `schemas.py`, `store.py`, `services.py`, `deps.py`,
`routers/`). Add a `LIBRARY_NAME` and `MAX_LOANS_PER_MEMBER` setting in `.env`,
enforce the loan limit in the service, and protect every write endpoint with
an `X-API-Key` dependency on the router.

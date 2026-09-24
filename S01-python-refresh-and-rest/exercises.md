# Session 01 — Exercises

## Type hints and Annotated
1. Run `pip install mypy` and `mypy app.py` in `01_type_hints`. Uncomment the
   last line of `main()` and read the error. Then add a function
   `cheapest(prices: dict[str, int]) -> str | None` and make mypy happy.
2. In `02_annotated`, add a rule `Pattern(regex: str)` and a type
   `Email = Annotated[str, Pattern(r'^[^@]+@[^@]+\.[a-z]+$')]`. Use it in a new
   function `register(email: Email, full_name: Title)` and extend
   `validate_call` so the rule is checked.
3. Explain in one sentence why FastAPI prefers
   `page: Annotated[int, Query(ge=1)] = 1` to a custom class `PageNumber(int)`.

## Generics and dataclasses
4. Add a method `update(item_id: int, **changes: object) -> T` to the
   `Repository` of `03_generics`. What should happen for an unknown id? For an
   unknown field name?
5. Add `@dataclass(slots=True)` to `User` in `03_generics` and try
   `user.emial = 'x'`. What happens with and without `slots`?
6. In `04_dataclasses`, make `Course.capacity` validated in `__post_init__`
   (must be 1–500) and add a `@property is_full`.

## Functions and decorators
7. In `05_higher_order_functions`, write `make_title_filter(text: str)` that
   matches case-insensitively, and combine it with the price filter using
   `all_of`.
8. Write a decorator `@require_role('admin')` that expects the first argument
   of the wrapped function to be a `User` and raises `PermissionError` if the
   role does not match. (In session 10 FastAPI does this with a dependency.)
9. Make `@retry` accept the exception types to retry on:
   `@retry(times=3, on=(ConnectionError, TimeoutError))`.

## Exceptions, context managers, generators, async
10. Add a `CourseClosedError` to `07_custom_exceptions` for courses with
    `is_active = False`. Which status code should it get, and why not 404?
11. Turn `Timer` of `08_context_managers` into a `@contextmanager` function.
    Which version do you prefer?
12. **Refactor `12_refactor_me/app.py`.** Keep the printed output identical.
    Use a dataclass, type hints, small functions, a generator, integer money,
    no global, no bare `except`, no mutable default. (Compare with
    `14_project/training_center/reports.py` *after* you finish.)
13. In `10_async_await`, add a function that fetches seats for 20 courses
    but never more than 5 at a time (`asyncio.Semaphore`). Time it.

## HTTP and Bruno
14. In Bruno, add a request that **updates** post 1 with `PATCH` and one that
    **deletes** it. Which status codes do you get?
15. In `11_http_and_json`, list the titles of all posts of user 3 that contain
    the word `qui`. Print how long the request took.
16. Add a Bruno test to `03-create-post.bru` that checks the returned `id`
    is a number.

## The project
17. Add `unenroll(student_id, course_id)` to `TrainingCenterService`. It must
    raise `NotFoundError` if the student is not in the course.
18. Add `deactivate_user(actor_id, user_id)`: only an admin may do it, and a
    deactivated student can no longer enroll (the check already exists — find it).
19. Add `courses_of(student_id) -> list[Course]` sorted by title.
20. Wrap a "register and enroll in one step" operation in `transaction()` so
    that a full course also removes the newly created user.

## To think about
21. The service raises `CourseFullError`; it does not print anything and does
    not know about HTTP. Why is that important for the next sessions?
22. `InMemoryRepository` is generic. Which part of it will change when we use
    a database in session 5, and which part of the *service* will not change?
23. Why did `blocking_mistake` in example 10 take two seconds even with
    `gather`?

## Homework
Write `14_project/api_report.py`: using HTTPX, download all users and todos
from <https://jsonplaceholder.typicode.com> and print, for each user, the
name and the percentage of finished todos, sorted from best to worst.
Requirements: dataclasses for `User` and `Todo`, full type hints, a timeout,
a custom `ApiUnavailableError` raised on network problems, and a
`@timed` decorator on the main function. Save your Bruno requests for
`/users` and `/todos` in the session collection.

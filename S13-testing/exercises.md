# Session 13 — Exercises

## pytest
1. In `01_pytest_basics`, add `apply_coupon(price, code)` to `pricing.py`
   (`KADOOS10` = 10%, `STUDENT20` = 20%, unknown code → `PricingError`) and
   write its tests *first*, then the code.
2. Make one test fail on purpose and read pytest's output. Which line tells
   you the actual and the expected value?

## TestClient and overrides
3. In `02_testclient`, add `DELETE /courses/{id}` and test 204, then 404 on
   the second delete.
4. In `03_dependency_overrides`, write a test where the fake database raises
   an exception. What status code does the client see? Should it?
5. Why must `app.dependency_overrides.clear()` run even when a test fails?
   How does the `yield` fixture guarantee it?

## The project
6. Read `tests/conftest.py` and draw how a request in a test reaches the
   database. Which real code is replaced, which is not?
7. **Write negative tests** (each one in a new test function):
   * PUT a course with a missing field → 422
   * a teacher changes the capacity below the number of active students → 400
   * a deactivated user's old token → 403
   * `/users` as an instructor → 403
   * download a material of a course you are not in → 403
8. Test pagination: create 25 courses with a loop and check `total`, `pages`
   and the size of the last page.
9. Test `DELETE /users/{id}` for an instructor who still teaches: 409.
10. **Break the code:** comment out `ensure_can_manage_course` in
    `CourseService.update`. Which tests fail? If none, write the missing one.
11. Add the `pytest-cov` package and run `pytest --cov=app`. Which service
    functions are never tested? Test one of them.

## To think about
12. The tests create users directly in the database instead of calling
    `/auth/register`. Why? When is it better to go through the API?
13. Why does every test get its own database file?
14. Bruno collection vs pytest suite: what is each one best for?

## Homework
Write a pytest suite for your **Library API**: a `conftest.py` with a test
database and dependency overrides, factories, and at least 20 tests — half
of them failure cases (401, 403, 404, 409, 422, 413/415 for covers). All
tests must pass with a single `pytest` command and no running server.

# Capstone tasks

This is the Training Center API as a colleague left it: almost finished,
with bugs, missing pieces and one ugly endpoint. Your job, in teams of two:
make it correct, complete and clean. The tasks are described by their
**symptoms**, the way a bug report reaches you.

Start here:
```bash
alembic upgrade head
python seed.py
pytest                 # 10 tests fail -- that is your first to-do list
python main.py         # and open bruno/ in Bruno
```

## A. Make the test suite green (bugs the tests already catch)
1. "The course catalogue is empty although there are courses."
2. "A course with capacity 2 accepted a third student."
3. "The registration answer shows something it never should."
4. "`GET /users/me/enrollments` crashes with a 500."
5. "Passwords like `12345678` are accepted."
6. "An instructor deleted a course."
7. "Any logged-in teacher can see the students of every course."

## B. Bugs nobody has a test for yet (find them, then write the test)
8. "Filtering with `min_price=3000000` shows the CHEAP courses."
9. "We disabled a user, but their app still works until the token expires."
10. "A student who cancelled still downloads the course materials."
11. "An instructor set the capacity of a course to -3."

## C. Complete the missing features
12. `PATCH /users/me` — a user changes their own full name (never role or `is_active`).
13. `POST /users/me/password` — `old_password` + `new_password`; wrong old
    password → 401, weak new password → 422, success → 204.
14. Add both to the Bruno collection (success and failure requests).

## D. Refactor
15. `GET /users/stats` works, but look at it: business logic in the router,
    whole tables loaded into Python, nested loops. Move it into the service
    and let the database count with `GROUP BY`. The JSON answer must not change
    (there is a response you can compare with in Bruno before you start).

## E. Tests and client
16. Write a test for every bug of part B and every feature of part C.
17. In `client_app/api_client.py` add `update_me`, `change_password`,
    `my_enrollments` and `enroll`, with tests using `MockTransport`.
18. In `client_app/main.py` add the student view: when a student logs in,
    print their courses and enroll them in the cheapest course they do not
    take yet.

## Done means
* `pytest` is green, with your new tests;
* every request of the Bruno collection gives the expected status;
* `python -m client_app.main --email sara@example.com` shows the student view;
* you can answer every question of `../code-review.md` about YOUR code.

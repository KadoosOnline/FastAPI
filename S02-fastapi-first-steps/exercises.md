# Session 02 — Exercises

## Parameters
1. In `02_path_parameters`, add `GET /courses/most-expensive`. Put it *after*
   `/courses/{course_id}` first, call it, and explain the error. Then fix the order.
2. In `03_query_parameters`, add `min_price` and a `sort` parameter that
   accepts `price` or `title`. What does your API do with `sort=banana`?
   (Session 3 gives a clean answer with `Literal`.)
3. Add a `limit` of at most 50: what should happen if the client asks for 1000?

## Body and status codes
4. In `04_request_body`, the `POST` answers `200`. Change it to `201`.
5. In `05_status_codes`, add `GET /users/{user_id}` with a 404, and
   `PATCH /users/{user_id}` that changes only the full name.
6. Send, from Bruno, a body that is not JSON at all (choose "Text" and type
   `hello`). Which status code do you get, and who produced it?

## The project
7. Add `GET /courses/{course_id}/seats` that returns
   `{"capacity": 20, "enrolled": 0, "seats_left": 20}` (enrolled is always 0
   for now).
8. Refuse to create a course whose `price` is negative or whose `capacity`
   is 0: raise `HTTPException(400)` with a clear message. (Session 3 does
   this better, with Pydantic.)
9. Add `PUT /users/{user_id}` and `PATCH /users/{user_id}`, with 404 and 409
   (email already used by *another* user).
10. Add a `router` for **enrollments**: `POST /courses/{course_id}/students/{user_id}`
    stores the pair in a list in `data.py`; enrolling twice is a 409, an
    unknown course or user is a 404.
11. Add a request to the Bruno collection for every new endpoint, including
    at least one failing request for each.
12. Move the `get_or_404` helper so both routers can use it. Where should it live?

## To think about
13. Why is `/courses/abc` a 422 and not a 404?
14. `DELETE /courses/3` twice: what do you get the second time, and is that correct?
15. The data disappears when the server restarts. Which session fixes that,
    and which files of the project will change most?

## Homework
Build a tiny **Library API** in a new folder, the same shape as `08_project`:
books (`title`, `author`, `year`, `available`) with the full CRUD, a
`?available=true&author=...` filter, a `POST /books/{id}/borrow` endpoint that
returns 409 if the book is not available, and a Bruno collection with at least
ten requests (four of them failing on purpose).

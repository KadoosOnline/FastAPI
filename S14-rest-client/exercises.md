# Session 14 — Exercises

## HTTPX
1. In `01_httpx_basics`, rewrite `main()` with the `requests` library.
   What had to change? What would you lose by staying with `requests`?
2. In `02_params_headers_json`, print the full URL for
   `params={'q': 'fast api & more'}`. Who took care of the escaping?
3. In `03_timeouts_and_errors`, add a `/rate-limited` path that answers 429
   with a `Retry-After: 2` header and handle it separately.

## Tokens
4. In `04_bearer_auth`, set `ACCESS_TOKEN_EXPIRE_MINUTES=1` on the server,
   wait, and call `/users/me` again. Which error do you get? Make the script
   log in again automatically when that happens.
5. Why does logging in use `data=` and not `json=`?

## The client
6. Add `update_me(full_name=...)` (if you added `PATCH /users/me` in session
   10) or `my_courses_taught()` to the client, with a test.
7. Add `download_material(material_id, target: Path)` that streams the file to
   disk (`client.stream('GET', ...)` + `iter_bytes()`), with a test.
8. Make `get_course()` accept a `with_detail: bool` argument. Which endpoint
   gives you the instructor?
9. **Build a client method from a requirement:** "list the titles of all
   advanced courses under 4 000 000 Toman, cheapest first" — one method,
   using `iter_courses`.
10. Add a `retries` option: repeat GET requests that end with
    `ApiConnectionError` up to N times. Why only GET?
11. Write a test that proves the client sends the `User-Agent` header.

## To think about
12. The client has its own `models.py` instead of importing the server's
    schemas. What would break if it imported them?
13. What is the difference between `ApiConnectionError` and `ServerError`, and
    why should a user interface show different messages for them?
14. The client keeps the token in memory. Where would a mobile app keep it?

## Homework
Write `library_client.py` for your **Library API**: a `LibraryClient` class
with login, search books (all pages, as a generator), borrow, return and my
loans; typed models; its own exceptions; timeouts; and at least eight tests
with `MockTransport` (half of them for failures). Then write a short script
that borrows the cheapest available book of an author given on the command line.

# Session 15 — Exercises

## Async and concurrency
1. In `02_concurrent_requests`, fetch 100 posts with limits of 1, 5, 20 and
   100. Draw a small table of the times. What do you conclude?
2. Point `02_concurrent_requests` at our local API (`/courses/{id}`). Why is
   the difference between sequential and concurrent so small?

## Retries and errors
3. In `03_retry_and_backoff`, add random "jitter" to the waiting time
   (`random.uniform(0, 0.1)`). Why do large systems add jitter?
4. Make the retry function also retry 429, respecting `Retry-After`.
5. In `04_error_mapping`, add a request-id header to every request with an
   event hook, and print it in the response hook.

## Integration
6. In `05_third_party_api`, simulate a change in the external API: rename the
   `completed` field in a MockTransport response. Which error does our code
   raise, and where?
7. Write a second third-party integration of your choice (weather, exchange
   rates...) with a 3-second timeout and a clear fallback message.

## The project
8. Add `--export report.csv` to `client_app.main` that saves the dashboard
   table as CSV.
9. Add `api.enroll(course_id)` and a `--student` mode that shows a student's
   courses and enrolls them in the cheapest course they are not in yet.
10. When the token expires during a long run, log in again automatically once
    and repeat the request. Where in `api_client.py` does this belong?
11. Add a test that proves `students_of_many` returns the right students for
    each course even when the fake server answers in a random order.
12. Stop the API server while the dashboard is fetching (add a `sleep` to make
    it slow). What does the user see?
13. Open `06_browser_fetch` from port 8080 instead of 5500. What breaks, and
    which setting on the server fixes it?

## To think about
14. Why must a POST never be retried automatically, but a PUT may be?
15. Browser client, Python client, Bruno: the server treats them all the
    same. What does that tell you about good API design?
16. Where would you store the token in a desktop app? In a browser?

## Homework
Write an async **Library dashboard** for your Library API: log in as a
librarian, list every book (all pages), fetch the current loans of every
member concurrently with a limit of 5, print the members who have a book
overdue, and handle every failure with a clear message. Include at least six
tests with `MockTransport`.

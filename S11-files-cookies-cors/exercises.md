# Session 11 — Exercises

## Headers and cookies
1. In `01_headers`, answer `/hello` in Persian, English or German depending on
   `Accept-Language`, and send back a `Content-Language` header.
2. In `02_cookies`, set `secure=True` and test on `http://127.0.0.1`. What
   happens in the browser, and why?
3. Write the three cookie flags and, for each, one attack it protects against.

## Forms and files
4. In `03_form_data`, add a `phone` field with validation. Show the error
   in the HTML page instead of a JSON 422 (hint: catch it and return HTML).
5. In `04_file_upload`, upload a file called `../../hack.txt`. Where is it
   saved, and which line protects you?
6. In `05_file_validation`, add `image/webp` (magic bytes: `RIFF....WEBP`).
7. Change the size check so it rejects a big file *before* reading it, when
   the client sends a `Content-Length` header. Why must you still count bytes
   while reading?

## CORS and responses
8. Run the two-terminal experiment of `07_cors`. Then call the same URL from
   Bruno with the page's origin blocked. Why does Bruno still work?
9. In `08_responses`, stream a CSV of 100 000 generated rows. Watch the
   memory of the Python process while downloading.

## The project
10. Add `GET /courses/{id}/materials.zip` that returns all materials of a
    course as one ZIP file (module `zipfile`), for the same users who may
    download them.
11. Add a maximum of 20 materials per course (400 when full).
12. Add `PATCH /materials/{id}` to rename the title (owner or admin only).
13. Add `GET /courses/export.csv` (admin only) that streams every course with
    its number of active students.
14. Make the upload limit different per type: 20 MB for ZIP, 5 MB for the rest.
15. Prove in Bruno that a cancelled student can no longer download materials.

## To think about
16. Why are the files stored on disk and not in the database? When would you
    use object storage (S3-like) instead?
17. Why are materials served with `FileResponse` behind a permission check
    and not with `StaticFiles`?
18. What happens to the files when a course is deleted? Find the problem and
    propose a fix.

## Homework
Add **book covers** to your **Library API**: librarians upload a JPEG or PNG
cover (max 2 MB, magic bytes checked, stored under a random name), everybody
can download it, and uploading a new cover deletes the old file. Add a
`GET /books/export.csv` stream for librarians and Bruno requests for every
failure (wrong type, too big, not a librarian).

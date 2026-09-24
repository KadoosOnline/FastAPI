# Session 09 — Exercises

## Hashes
1. In `01_password_hashing`, print the three parts of an Argon2 hash string
   (settings, salt, hash). Which part is secret? (Trick question.)
2. Why can the server check a password although it can not "decrypt" the hash?
   Explain it to your neighbour in three sentences.

## Registration and login
3. In `02_register`, add a `password_repeat` field and a `model_validator`
   that compares the two. Make sure `password_repeat` is not stored.
4. Add a rule: the password must not contain the user's e-mail name
   (`sara` in `sara@example.com`). Where must this rule live, and why can it
   not be a simple `AfterValidator` on the password field?
5. In `03_oauth2_password_form`, add `POST /auth/logout` that deletes the
   token from `TOKENS`. Why is logging out harder with JWTs (next session)?
6. Click **Authorize** in `/docs` of example 03, log in, and call `/users/me`.
   Open the browser's network tab: where is the token sent?

## Attacks and defences
7. In `04_login_errors`, remove the dummy-hash line. Measure the time of 20
   logins with an unknown e-mail and 20 with a wrong password (a small httpx
   script). What can an attacker learn?
8. Change the brute-force limit so it resets after 5 minutes (store the time
   of the first failure).
9. Why is the "disabled" check *after* the password check?

## The project
10. Add `POST /auth/change-password` with `email`, `old_password` and
    `new_password` (JSON). Wrong old password → 401. Use the service.
11. Add a `last_login_at` column (a new migration `0004`) and set it in
    `authenticate`.
12. Log every failed login with `logging` (e-mail and time, **never** the password).
13. Create a user with plain SQL in the database whose `hashed_password` is
    `'!'` and try to log in. Explain what happens and why that is safe.
14. Add Bruno requests for exercises 10 and 11, including the failures.

## To think about
15. Why does `/auth/login` take a form and not JSON?
16. What is the difference between 401 and 403? Give one project example of each.
17. The login endpoint answers in ~50 ms because of Argon2. Is that a problem
    for the server? For an attacker?

## Homework
Add members' accounts to your **Library API**: `POST /auth/register`
(members only), `POST /auth/login` with the OAuth2 form, Argon2 hashes, the
same error message for unknown e-mail and wrong password, 403 for blocked
members, and a password rule of your choice. Write the Bruno requests for
every success and every failure.

# Session 10 — Exercises

## Tokens
1. Paste a token from the project into <https://jwt.io>. What can you read?
   What would you need to change it without being caught?
2. In `01_jwt_encode_decode`, add a claim `"email"`. Should it be there?
   What about `"password_hash"`? Explain.
3. **Debug a JWT failure:** set `ACCESS_TOKEN_EXPIRE_MINUTES=1` in the
   project's `.env`, log in, wait, and call `/users/me`. Read the answer.
   Then change `JWT_SECRET_KEY` and restart: what happens to the tokens that
   were already issued? Why is that sometimes useful?
4. Make `decode_access_token` accept 10 seconds of clock difference.

## Roles and ownership
5. In `04_role_dependency`, add a role `support` that may read the list of
   users but not delete anything.
6. In `05_ownership_rules`, let an instructor rename a course only if it has
   not started yet (add `start_date`). Which status code for "too late"?
7. In `06_scopes`, log in as admin but request only `courses:read` (in /docs,
   untick the other scopes). Try to create a course.

## The project
8. Add `PATCH /users/me` (change `full_name`) and `POST /users/me/password`
   (old + new password). The new password must follow the same rules as
   registration.
9. Let an instructor see the list of students **only for courses that have
   started**. Where does this rule go?
10. A disabled user still holds a valid token. Prove with Bruno that the
    API already refuses it, and find the line of code that does it.
11. Add a role check so an admin can not deactivate *themself*
    (`PATCH /users/{id}` with their own id). Return 400.
12. Write down, for every endpoint, which Bruno request proves the
    permission table. Add the missing ones.

## To think about
13. Why is the token's `sub` a string and not the integer id?
14. JWTs can not be "logged out" on the server. List two ways real systems
    deal with that (short expiry, a deny list, refresh tokens...).
15. Where should the decision "instructors manage only their own courses"
    live: router, service, or database? Why?

## Homework
Protect your **Library API** with JWT: `/auth/token`, `get_current_user`,
roles `librarian` and `member`, and these rules: members borrow and return
books for themselves only; librarians manage books and see every loan; a
member can see only their own loans. Add Bruno requests for every "403" case.

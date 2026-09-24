# Capstone code review

Each team presents its project for 5–7 minutes, then answers questions from
another team. Answer with *your* code open on the screen: point at the file
and the line.

## Structure
1. Walk us through one request — `POST /courses/{id}/enrollments` — from the
   router to the database and back. Which files does it touch, and why is each
   one a separate file?
2. Why are the routers so short? What would go wrong if the business rules
   lived in them?

## Data
3. Why do we have Pydantic schemas **and** SQLAlchemy models for the same
   course? Show one field that exists in only one of them, and explain why.
4. What do the typed mappings (`Mapped[int]`, `Mapped[str | None]`) give us
   compared with the old `Column(...)` style?
5. Show a query that avoids the N+1 problem. How would you prove it?
6. Why is the database schema changed with Alembic and not with `create_all`?

## Dependencies and async
7. Show three places where Dependency Injection is used. Which one did the
   tests replace, and how?
8. Where does async actually help this API, and where does it not? What would
   happen if someone called `time.sleep()` in a service?

## Security
9. Explain the login flow from the form to the JWT. What is inside the token,
   what is not, and why?
10. How does the API know the difference between 401 and 403? Show both.
11. Which rule stops an instructor from editing another instructor's course?
12. How are uploaded files validated, and where are they stored?

## Quality
13. How do your tests protect the API? Show one test for a failure case you
    are proud of.
14. How does the Python client talk to the API, and what happens in it when
    the server is down?
15. If you had one more day, what would you improve first?

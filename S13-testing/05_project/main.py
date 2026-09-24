"""Training Center API — version 12 (session 13 project): the same API, now with tests.

New since session 12: the `tests/` folder and `pytest.ini`.

    tests/conftest.py         fixtures: temporary database, dependency overrides,
                              an async HTTPX client, user / course factories, auth headers
    tests/test_auth.py        register, login, every login failure, /users/me
    tests/test_courses.py     browsing, create / edit / delete permissions, 422s
    tests/test_enrollments.py enroll, full course, cancel, all-or-nothing, owner-only lists
    tests/test_materials.py   upload validation, who may read, download
    tests/test_units.py       passwords, tokens and schemas without HTTP

    pytest              run everything (no server, no training.db needed)
    pytest -k login     only tests with "login" in the name

    alembic upgrade head && python seed.py && python main.py    to run the API itself
"""

import uvicorn

if __name__ == '__main__':
    uvicorn.run('app.main:app', reload=True)

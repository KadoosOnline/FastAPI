"""CORS: may a web page from ANOTHER origin call this API from the browser?

An "origin" = scheme + host + port. http://localhost:5500 and
http://127.0.0.1:8000 are different origins. Browsers block JavaScript from
reading responses of another origin UNLESS the API answers with
`Access-Control-Allow-Origin` for that origin. For some requests the browser
first sends an OPTIONS "preflight" to ask.

CORS is a BROWSER rule. curl, Bruno and Python clients ignore it completely.

Try it:
    terminal 1:  python app.py                                 (the API on :8000)
    terminal 2:  python -m http.server 5500                    (serves page.html)
    browser:     http://localhost:5500/page.html  -> works
    then remove 5500 from ALLOWED_ORIGINS, restart the API, reload the page -> blocked
    (open the browser console to read the CORS error)
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

ALLOWED_ORIGINS = ['http://localhost:5500', 'http://127.0.0.1:5500']

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # never ['*'] together with allow_credentials=True
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'PATCH', 'DELETE'],
    allow_headers=['Authorization', 'Content-Type'],
)


@app.get('/courses')
def courses() -> list[dict[str, str | int]]:
    return [{'id': 1, 'title': 'Python'}, {'id': 2, 'title': 'FastAPI'}]


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)

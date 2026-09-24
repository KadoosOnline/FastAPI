"""Your first FastAPI application.

    python app.py

then open:
    http://127.0.0.1:8000/          the JSON answer
    http://127.0.0.1:8000/docs      Swagger UI: try every endpoint in the browser
    http://127.0.0.1:8000/redoc     ReDoc: the same documentation, for reading

What happens:
* `app = FastAPI()` creates the application.
* `@app.get('/')` is a decorator (session 1): "when a GET request for `/`
  arrives, call this function".
* The function returns a dict; FastAPI turns it into JSON.
* `uvicorn` is the web server that receives the requests and passes them to
  the app. `reload=True` restarts it every time you save the file.
"""

import uvicorn
from fastapi import FastAPI

app = FastAPI(title='Training Center API', version='0.1.0')


@app.get('/')
def home() -> dict[str, str]:
    return {'message': 'Welcome to the Training Center API'}


@app.get('/about')
def about() -> dict[str, str | int]:
    """This docstring appears in /docs."""
    return {'institute': 'Kadoos', 'city': 'Rasht', 'sessions': 16}


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)

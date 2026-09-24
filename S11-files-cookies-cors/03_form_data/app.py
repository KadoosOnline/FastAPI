"""Form data: what an HTML <form> sends (not JSON).

    Content-Type: application/x-www-form-urlencoded     name=Sara&email=...
    Content-Type: multipart/form-data                   the same, plus files (example 04)

Read single fields with `Form()`, or a whole Pydantic model:

    def contact(data: Annotated[ContactForm, Form()]): ...

Needs `python-multipart`. Remember the login of session 9: OAuth2 also uses
a form. Open http://127.0.0.1:8000/ for a real HTML form that posts here.
"""

from typing import Annotated

import uvicorn
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr, Field

app = FastAPI()
MESSAGES: list[dict] = []


class ContactForm(BaseModel):
    name: str = Field(min_length=2)
    email: EmailStr
    message: str = Field(min_length=10, max_length=1000)
    newsletter: bool = False


@app.get('/', response_class=HTMLResponse)
def page() -> str:
    return """
    <form method="post" action="/contact">
      <input name="name" placeholder="name"><br>
      <input name="email" placeholder="email"><br>
      <textarea name="message" placeholder="at least 10 characters"></textarea><br>
      <label><input type="checkbox" name="newsletter" value="true"> newsletter</label><br>
      <button>Send</button>
    </form>"""


@app.post('/contact', status_code=201)
def contact(data: Annotated[ContactForm, Form()]) -> dict:
    MESSAGES.append(data.model_dump())
    return {'received': data.model_dump(), 'total_messages': len(MESSAGES)}


@app.post('/quick-note')
def quick_note(title: Annotated[str, Form()], body: Annotated[str, Form()] = '') -> dict:
    return {'title': title, 'body': body}


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)

"""Training Center API — version 1 (session 2 project).

Everything lives in memory (the dictionaries in data.py), so a restart
resets the data. That is fine for now: in session 5 a real database arrives.

    python main.py      then open http://127.0.0.1:8000/docs
"""

import uvicorn
from fastapi import FastAPI

from routers import courses, users

app = FastAPI(
    title='Training Center API',
    version='1.0.0',
    description='Kadoos FastAPI course project, session 2.',
)
app.include_router(courses.router)
app.include_router(users.router)


@app.get('/', tags=['home'])
def home() -> dict[str, str]:
    return {'message': 'Training Center API', 'docs': '/docs'}


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)

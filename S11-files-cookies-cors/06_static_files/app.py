"""Static files and downloads.

`StaticFiles` serves a whole folder as it is -- images, CSS, public PDFs:

    app.mount('/static', StaticFiles(directory='static'), name='static')
    GET /static/logo.txt

It is PUBLIC: no authentication. Private files (course materials that only
enrolled students may read) must go through an endpoint that checks
permissions and then returns a `FileResponse`:

    return FileResponse(path, media_type='application/pdf', filename='syllabus.pdf')

`filename=` adds `Content-Disposition: attachment; filename="..."`, so the
browser downloads the file under a nice name.
"""

from pathlib import Path
from typing import Annotated

import uvicorn
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

HERE = Path(__file__).parent
app = FastAPI()
app.mount('/static', StaticFiles(directory=HERE / 'static'), name='static')


@app.get('/private/report')
def private_report(x_role: Annotated[str | None, Header()] = None) -> FileResponse:
    if x_role != 'admin':
        raise HTTPException(403, detail='Admins only')
    return FileResponse(
        HERE / 'static' / 'logo.txt', media_type='text/plain', filename='report.txt'
    )


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)

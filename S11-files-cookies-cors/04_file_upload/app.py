"""File uploads with `UploadFile` (multipart/form-data).

    file: UploadFile                       one file
    files: list[UploadFile]                several files
    title: Annotated[str, Form()]          other fields travel as form fields

UploadFile gives: `.filename`, `.content_type`, `.size`, and async methods
`await file.read(n)`, `await file.seek(0)`. Big files are spooled to disk by
Starlette, so reading in CHUNKS keeps memory low.

Never trust `file.filename` as a path ("../../etc/passwd"): example 05 stores
files under generated names.
"""

from pathlib import Path
from typing import Annotated

import uvicorn
from fastapi import FastAPI, File, Form, UploadFile

UPLOAD_DIR = Path('uploads')
UPLOAD_DIR.mkdir(exist_ok=True)
app = FastAPI()


@app.post('/upload')
async def upload(file: UploadFile, title: Annotated[str, Form()] = 'untitled') -> dict:
    target = UPLOAD_DIR / Path(file.filename or 'file').name  # .name drops any folders
    size = 0
    with target.open('wb') as out:
        while chunk := await file.read(64 * 1024):  # 64 KB at a time
            size += len(chunk)
            out.write(chunk)
    return {
        'title': title,
        'filename': file.filename,
        'content_type': file.content_type,
        'bytes': size,
        'saved_as': str(target),
    }


@app.post('/upload-many')
async def upload_many(
    files: Annotated[list[UploadFile], File(description='several files')],
) -> list[dict]:
    return [{'filename': f.filename, 'size': f.size, 'type': f.content_type} for f in files]


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)

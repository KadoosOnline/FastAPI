"""Validating uploads: type, content and size. Trust nothing.

1. The declared `content_type` comes from the CLIENT: it can lie.
   -> check a white list of types (415 Unsupported Media Type)
2. So also look at the first bytes ("magic numbers"):
       PDF  starts with  %PDF-
       PNG  starts with  \x89PNG\r\n\x1a\n
       JPEG starts with  \xff\xd8\xff
3. Limit the size WHILE reading, and stop early (413 Content Too Large).
4. Store under a generated name (uuid4) -- never under the client's name.
5. If anything fails half way, delete the partial file.
"""

import uuid
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, status

UPLOAD_DIR = Path('uploads')
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_BYTES = 1 * 1024 * 1024  # 1 MB for the demo
ALLOWED = {
    'application/pdf': ('.pdf', b'%PDF-'),
    'image/png': ('.png', b'\x89PNG\r\n\x1a\n'),
    'image/jpeg': ('.jpg', b'\xff\xd8\xff'),
    'text/plain': ('.txt', None),
}
app = FastAPI()


@app.post('/materials', status_code=status.HTTP_201_CREATED)
async def upload_material(file: UploadFile) -> dict:
    if file.content_type not in ALLOWED:
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=f'{file.content_type} not allowed'
        )
    extension, magic = ALLOWED[file.content_type]
    if magic is not None:
        head = await file.read(len(magic))
        await file.seek(0)
        if head != magic:
            raise HTTPException(
                status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail='Content does not match the type'
            )

    stored = UPLOAD_DIR / f'{uuid.uuid4().hex}{extension}'
    size = 0
    try:
        with stored.open('wb') as out:
            while chunk := await file.read(64 * 1024):
                size += len(chunk)
                if size > MAX_BYTES:
                    raise HTTPException(
                        status.HTTP_413_CONTENT_TOO_LARGE, detail='File is larger than 1 MB'
                    )
                out.write(chunk)
    except BaseException:
        stored.unlink(missing_ok=True)  # no half-written files left behind
        raise
    return {'original_name': file.filename, 'stored_as': stored.name, 'bytes': size}


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)

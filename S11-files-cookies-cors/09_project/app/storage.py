"""Saving uploaded files on the local disk, safely."""

import uuid
from pathlib import Path

from fastapi import UploadFile

from app.exceptions import FileTooLargeError, FileValidationError

CHUNK_SIZE = 64 * 1024

# Allowed MIME type -> (extension we store, first bytes the file must start with)
ALLOWED_TYPES: dict[str, tuple[str, bytes | None]] = {
    'application/pdf': ('.pdf', b'%PDF-'),
    'image/png': ('.png', b'\x89PNG\r\n\x1a\n'),
    'image/jpeg': ('.jpg', b'\xff\xd8\xff'),
    'application/zip': ('.zip', b'PK\x03\x04'),
    'text/plain': ('.txt', None),
}


class LocalStorage:
    def __init__(self, root: Path, max_bytes: int) -> None:
        self.root = root
        self.max_bytes = max_bytes

    def path_for(self, stored_name: str) -> Path:
        return self.root / stored_name

    def check_type(self, upload: UploadFile) -> str:
        """Validate the declared type AND the real first bytes; return the extension."""
        content_type = upload.content_type or ''
        if content_type not in ALLOWED_TYPES:
            allowed = ', '.join(ALLOWED_TYPES)
            raise FileValidationError(f'{content_type!r} is not allowed. Allowed: {allowed}')
        extension, magic = ALLOWED_TYPES[content_type]
        if magic is not None:
            head = upload.file.read(len(magic))
            upload.file.seek(0)
            if head != magic:
                raise FileValidationError(f'The file content is not really {content_type}')
        return extension

    def save(self, upload: UploadFile, extension: str) -> tuple[str, int]:
        """Copy the upload in chunks under a random name. Returns (name, size)."""
        self.root.mkdir(parents=True, exist_ok=True)
        stored_name = f'{uuid.uuid4().hex}{extension}'
        target = self.path_for(stored_name)
        size = 0
        try:
            with target.open('wb') as out:
                while chunk := upload.file.read(CHUNK_SIZE):
                    size += len(chunk)
                    if size > self.max_bytes:
                        raise FileTooLargeError(f'The file is larger than {self.max_bytes} bytes')
                    out.write(chunk)
        except BaseException:
            target.unlink(missing_ok=True)
            raise
        return stored_name, size

    def delete(self, stored_name: str) -> None:
        self.path_for(stored_name).unlink(missing_ok=True)

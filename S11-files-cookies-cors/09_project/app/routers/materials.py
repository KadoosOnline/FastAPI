from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile, status
from fastapi.responses import FileResponse

from app.deps import CurrentUser, MaterialServiceDep, StaffUser
from app.schemas import MaterialRead

router = APIRouter(tags=['materials'])


@router.post('/courses/{course_id}/materials', status_code=status.HTTP_201_CREATED)
def upload_material(
    course_id: int,
    file: Annotated[UploadFile, File(description='PDF, PNG, JPEG, ZIP or TXT')],
    title: Annotated[str, Form(min_length=3, max_length=200)],
    actor: StaffUser,
    service: MaterialServiceDep,
) -> MaterialRead:
    """multipart/form-data: a `file` plus a `title` field. Admin or the course's instructor."""
    return MaterialRead.model_validate(service.upload(course_id, file, title, actor))


@router.get('/courses/{course_id}/materials')
def list_materials(
    course_id: int, user: CurrentUser, service: MaterialServiceDep
) -> list[MaterialRead]:
    return [MaterialRead.model_validate(m) for m in service.list_for_course(course_id, user)]


@router.get('/materials/{material_id}/download', response_class=FileResponse)
def download_material(
    material_id: int, user: CurrentUser, service: MaterialServiceDep
) -> FileResponse:
    material, path = service.get_file(material_id, user)
    return FileResponse(path, media_type=material.content_type, filename=material.original_filename)


@router.delete('/materials/{material_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_material(material_id: int, actor: StaffUser, service: MaterialServiceDep) -> None:
    service.delete(material_id, actor)

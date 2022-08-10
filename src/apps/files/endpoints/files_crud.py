import hashlib

from fastapi import APIRouter, UploadFile
from starlette.background import BackgroundTasks
from starlette.responses import FileResponse, Response

from .. import services, models, schemas

files_crud_router = APIRouter()


@files_crud_router.post('/', response_model=schemas.FileInfo)
async def upload_file(file: UploadFile, background_task: BackgroundTasks):
    return await services.upload_file(file, background_task)


@files_crud_router.get('/')
async def get_file(file_id: str, preview: bool = False):
    # TODO: отдельная функция для превью + количество dpi
    response = await services.get_file(file_id, preview)
    if not preview:
        return FileResponse(response)
    else:
        return Response(content=response, media_type="image/png")


@files_crud_router.get('/b64', response_model=schemas.FileB64Response)
async def get_file_b64(file_id: str):
    return await services.get_file_b64(file_id)


@files_crud_router.delete('/', response_model=schemas.FileInfo)
async def get_file_b64(file_id: str, bt: BackgroundTasks):
    return await services.delete_file(file_id, bt)

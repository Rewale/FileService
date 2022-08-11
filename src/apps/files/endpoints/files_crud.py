import hashlib
from typing import List

from fastapi import APIRouter, UploadFile
from starlette.background import BackgroundTasks
from starlette.responses import FileResponse, Response

from .. import services, models, schemas

files_crud_router = APIRouter()


@files_crud_router.post('/', response_model=schemas.FileInfo)
async def upload_file(file: UploadFile, background_task: BackgroundTasks):
    return await services.upload_file(file, background_task)


@files_crud_router.get('/', response_class=FileResponse)
async def get_file(file_id: str):
    return await services.get_file(file_id)


@files_crud_router.get('/preview')
async def get_file_preview(file_id: str, preview_dpi: int = 500):
    content = await services.get_file_preview(file_id, preview_dpi)
    return Response(content=content, media_type='image/png')


@files_crud_router.get('/b64', response_model=schemas.FileB64Response)
async def get_file_b64(file_id: str):
    return await services.get_file_b64(file_id)


@files_crud_router.delete('/', response_model=schemas.FileInfo)
async def get_file_b64(file_id: str, bt: BackgroundTasks):
    return await services.delete_file(file_id, bt)


@files_crud_router.get('/all', response_model=List[schemas.FileInfoItem])
async def get_all_files():
    return await services.get_files()


@files_crud_router.put('/', response_model=schemas.FileInfo)
async def update_file_info(new_file_info: schemas.FileInfo):
    # TODO: update file info
    return None


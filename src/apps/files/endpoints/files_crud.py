import hashlib

from fastapi import APIRouter, UploadFile
from starlette.background import BackgroundTasks
from starlette.responses import FileResponse

from .. import services, models, schemas

files_crud_router = APIRouter()


@files_crud_router.post('/upload_file', response_model=schemas.CreatedFileInfo)
async def upload_file(file: UploadFile, background_task: BackgroundTasks):
    return await services.upload_file(file, background_task)


@files_crud_router.get('/get_file', response_class=FileResponse)
async def get_file(file_id: str):
    return await services.get_file_path(file_md5=file_id)


@files_crud_router.get('/get_file/b64', response_model=schemas.FileB64Response)
async def get_file_b64(file_id: str):
    return await services.get_file_b64(file_id)

import hashlib

from fastapi import APIRouter, UploadFile
from starlette.background import BackgroundTasks

from .. import services, models, schemas

files_crud_router = APIRouter()


@files_crud_router.post('/upload_file', response_model=schemas.CreatedFileInfo)
async def upload_file(file: UploadFile, background_task: BackgroundTasks):
    return await services.upload_file(file, background_task)


@files_crud_router.post('/get_file', response_model=schemas.CreatedFileInfo)
async def get_file(file_id: str):
    return await services.upload_file(file, background_task)

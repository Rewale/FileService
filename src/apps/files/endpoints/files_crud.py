from fastapi import APIRouter, UploadFile
from starlette.background import BackgroundTasks
from starlette.responses import HTMLResponse
import hashlib

from .. import schemas, services, models

files_crud_router = APIRouter()


@files_crud_router.post('/upload_file')
async def upload_file(file: UploadFile, background_task: BackgroundTasks):
    content = await file.read()

    extension = file.filename.split('.')[-1]
    title = ".".join(file.filename.split('.')[:-1])
    md5 = hashlib.md5(content).hexdigest()
    file_info = await models.File.objects.create(title=title, md5=md5, extension=extension)
    background_task.add_task(services.save_file, content, '123.png')
    return file_info

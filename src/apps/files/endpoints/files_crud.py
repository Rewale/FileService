from typing import List, Optional

from fastapi import APIRouter, UploadFile
from starlette.background import BackgroundTasks
from starlette.responses import FileResponse, Response

from .. import services, schemas

files_crud_router = APIRouter()


@files_crud_router.post('/', response_model=schemas.FileInfo)
async def upload_file(file: UploadFile, background_task: BackgroundTasks):
    return await services.upload_file(file, background_task)


@files_crud_router.get('/', response_class=FileResponse)
async def get_file(file_id: str):
    return await services.get_file_stream(file_id)


@files_crud_router.get('/info', response_model=schemas.FileInfoItem)
async def get_file_info(file_id: str):
    return await services.get_file_info(file_id)


@files_crud_router.get('/preview')
async def get_file_preview(file_id: str, preview_dpi: int = 500):
    content = await services.get_file_preview(file_id, preview_dpi)
    return Response(content=content, media_type='image/png')


@files_crud_router.get('/b64', response_model=schemas.FileB64Response)
async def get_file_b64(file_id: str):
    return await services.get_file_b64(file_id)


@files_crud_router.delete('/', response_model=schemas.FileInfo)
async def delete_file(file_id: str, bt: BackgroundTasks):
    return await services.delete_file(file_id, bt)


@files_crud_router.get('/all', response_model=List[schemas.FileInfoItem])
async def get_all_files():
    return await services.get_files()


@files_crud_router.get('/all/page/{page}', response_model=schemas.ItemsPage)
async def get_page_files(page: int, title_contains: Optional[str] = None, extension: Optional[str] = None,
                         count_items: int = 5):
    filter_params = schemas.FilterParams(title_contains=title_contains, extension=extension)
    return await services.get_files_filter(filter_params,
                                           page,
                                           count_items)

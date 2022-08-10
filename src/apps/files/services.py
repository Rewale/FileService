import hashlib
import os.path
from typing import Tuple

import aiofiles as aiof
from fastapi import UploadFile
from starlette.background import BackgroundTasks

from src.apps.files import models, schemas
from src.config import settings


async def save_file_task(content: bytes, path: str):
    async with aiof.open(path, 'wb') as out:
        await out.write(content)
        await out.flush()


async def create_or_get_exist_file(filename: str, content: bytes) -> Tuple[bool, models.File]:
    """
    Создает запись о новом файле или возвращает запись об уже существующем
    :param filename: имя файла
    :param content: данные
    :return: (Создан новый файл, информация о файле)
    """
    extension = filename.split('.')[-1]
    title = ".".join(filename.split('.')[:-1])
    md5 = hashlib.md5(content).hexdigest()

    exist_file = await models.File.objects.get_or_none(md5=md5)
    if exist_file:
        return False, exist_file

    file_info = await models.File.objects.create(title=title, md5=md5, extension=extension)
    return True, file_info


def _get_storage_path(filename):
    return os.path.join(settings.FILES_STORAGE_PATH, filename)


async def upload_file(file: UploadFile, background_task: BackgroundTasks) -> schemas.CreatedFileInfo:
    content = await file.read()
    is_created_new, file_info = await create_or_get_exist_file(file.filename, content)
    path = _get_storage_path(file.filename)
    background_task.add_task(save_file_task, content, path)
    return schemas.CreatedFileInfo(extension=file_info.extension,
                                   title=file_info.title,
                                   id=file_info.md5,
                                   created=is_created_new,
                                   created_at=file_info.created_at)


async def get_file_path(file_md5: str):
    file = await models.File.objects.get_or_none(md5=file_md5)


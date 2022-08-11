import asyncio
import hashlib
import base64
import io
import os.path
from os import PathLike
from typing import Tuple, Union, List

from PIL import Image
from pdf2image import convert_from_path

import aiofiles as aiof
from fastapi import UploadFile
from starlette.background import BackgroundTasks

from src.apps.files import models, schemas, custom_exceptions
from src.config import settings


async def save_file_task(content: bytes, path: str):
    """ Сохранение файла """
    async with aiof.open(path, 'wb') as out:
        await out.write(content)
        await out.flush()


async def read_file(path) -> bytes:
    """ Чтение файла """
    async with aiof.open(path, 'rb') as out:
        content = await out.read()
        await out.flush()

    return content


def remove_file(path):
    """ Удаление файла """
    os.remove(path)


async def create_or_get_exist_file(filename: str, content: bytes) -> Tuple[bool, models.File]:
    """
    Создает запись о новом файле или возвращает запись об уже существующем.
    :param filename: имя файла.
    :param content: данные
    :return: (Создан новый файл, информация о файле)
    """
    extension = filename.split('.')[-1]
    title = ".".join(filename.split('.')[:-1])
    md5 = hashlib.md5(content).hexdigest()

    exist_file = await models.File.objects.get_or_none(md5=md5)
    if exist_file:
        return False, exist_file

    file = await models.File.objects.create(title=title, md5=md5, extension=extension)
    return True, file


def _get_storage_path(filename):
    return os.path.join(settings.FILES_STORAGE_PATH, filename)


async def upload_file(file: UploadFile, background_task: BackgroundTasks) -> schemas.FileInfo:
    """ Загрузить файл на сервер """
    content = await file.read()
    is_created_new, file = await create_or_get_exist_file(file.filename, content)
    path = _get_storage_path(file.filename)
    background_task.add_task(save_file_task, content, path)
    return schemas.FileInfo(extension=file.extension,
                            title=file.title,
                            id=file.md5,
                            created=is_created_new,
                            created_at=file.created_at)


def _get_preview_pdf(file: models.File, dpi: int = 500) -> bytes:
    """ Превью pdf в виде изображения, блокирующая"""
    path = _get_storage_path(file.filename)
    first_page = convert_from_path(path, dpi, single_file=True)[0]
    img_byte_arr = io.BytesIO()
    first_page.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()


def _get_preview_image(file: models.File, dpi: int = 300) -> bytes:
    path = _get_storage_path(file.filename)
    im = Image.open(path)
    size = dpi, dpi
    im.thumbnail(size, Image.ANTIALIAS)
    img_byte_arr = io.BytesIO()
    im.save(img_byte_arr, "PNG")
    return img_byte_arr.getvalue()


async def _get_file_or_raise(file_md5: str) -> models.File:
    file = await models.File.objects.get_or_none(md5=file_md5)
    if not file:
        raise custom_exceptions.NotFoundFileException(file_md5)

    return file


async def get_file(file_md5: str) -> str:
    """ Путь до файла или изображение превью (для определенных расширений) """
    file = await _get_file_or_raise(file_md5)
    return _get_storage_path(file.filename)


async def get_file_b64(file_md5: str):
    file = await models.File.objects.get_or_none(md5=file_md5)
    file_path = _get_storage_path(file.filename)

    content = await read_file(file_path)
    base_64 = base64.b64encode(content)

    return schemas.FileB64Response(data_b64=base_64,
                                   extension=file.extension,
                                   title=file.title,
                                   id=file_md5,
                                   created_at=file.created_at)


async def delete_file(file_md5: str, background_task: BackgroundTasks):
    file = await _get_file_or_raise(file_md5)
    await file.delete()
    background_task.add_task(remove_file, _get_storage_path(file.filename))
    return schemas.FileInfo(extension=file.extension,
                            title=file.title,
                            id=file.md5,
                            created=False,
                            created_at=file.created_at)


async def get_file_preview(file_md5: str, preview_dpi: int) -> bytes:
    file = await _get_file_or_raise(file_md5)

    if file.extension == 'pdf':
        # Запуск в executor блокирующей функции
        return await asyncio.get_event_loop().run_in_executor(None, _get_preview_pdf, file, preview_dpi)
    elif file.extension in ['png', 'jpg', 'jpeg']:
        # Запуск в executor блокирующей функции
        return await asyncio.get_event_loop().run_in_executor(None, _get_preview_image, file, preview_dpi)
    else:
        return await read_file(_get_storage_path('not_found.png'))


def get_url_preview(md5: str):
    return f'http://127.0.0.1/files/?file_id{md5}'


async def get_files() -> List[schemas.FileInfoItem]:
    def mapping_func(f: models.File):
        file_info_item = schemas.FileInfoItem(
            url_preview=get_url_preview(f.md5),
            title=f.title,
            extension=f.extension,
            id=f.md5,
            created_at=f.created_at
        )
        return file_info_item

    files = await models.File.objects.all()
    return list(map(mapping_func, files))

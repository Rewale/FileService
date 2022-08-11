import asyncio
import hashlib
import base64
import io
import os.path
from os import PathLike
from typing import Tuple, Union, List, Optional

from PIL import Image
from pdf2image import convert_from_path, convert_from_bytes

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


def _prev_path(path: str):
    return os.path.abspath(os.path.join(path, '..'))


def remove_file(path):
    """ Удаление файла """
    if not os.path.exists(path):
        return
    os.remove(path)
    prev_path = _prev_path(path)
    if len(os.listdir(prev_path)) == 0:
        os.rmdir(prev_path)

    prev_path = _prev_path(prev_path)
    if len(os.listdir(prev_path)) == 0:
        os.rmdir(prev_path)


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


def _get_not_found_image():
    return os.path.join(settings.FILES_STORAGE_PATH, 'not_found.png')


async def upload_file(file: UploadFile, background_task: BackgroundTasks) -> schemas.FileInfo:
    """ Загрузить файл на сервер """
    content = await file.read()
    is_created_new, file = await create_or_get_exist_file(file.filename, content)
    path = _get_storage_path(file.filename, True)
    background_task.add_task(save_file_task, content, path)

    if file.extension == 'pdf':
        background_task.add_task(_create_preview_pdf_from_bytes, file.filename_preview, content)

    return schemas.FileInfo(extension=file.extension,
                            title=file.title,
                            id=file.md5,
                            created=is_created_new,
                            created_at=file.created_at)


async def _get_preview_pdf(file: models.File, dpi: int = 500) -> bytes:
    """ Превью pdf в виде изображения, блокирующая"""
    path_exist = _get_exist_preview_path(file.filename_preview)
    if path_exist:
        content = await read_file(path_exist)
        return content
    else:
        content = await read_file(_get_storage_path(file.filename))
        preview_path = await asyncio.get_event_loop().run_in_executor(None, _create_preview_pdf_from_bytes,
                                                                      file.filename_preview,
                                                                      content)
        content_preview = await read_file(preview_path)
        return content_preview


def __get_sub_sub_path(base_path: str, filename, create_path):
    sub_dir = os.path.join(base_path, filename[:2])
    sub_sub_dir = os.path.join(base_path, filename[:2], filename[2:4])

    if create_path:
        if not os.path.exists(sub_dir):
            os.mkdir(sub_dir)

        if not os.path.exists(sub_sub_dir):
            os.mkdir(sub_sub_dir)

    return os.path.join(sub_sub_dir, filename)


def _get_storage_path(filename, create_path=False):
    return __get_sub_sub_path(settings.FILES_STORAGE_PATH, filename, create_path)


def _get_preview_storage_path(filename, create_path=True):
    return __get_sub_sub_path(settings.PREVIEW_FILES_STORAGE_PATH, filename, create_path)


def _create_preview_pdf_from_bytes(filename: str, content_pdf: bytes, dpi: int = 550) -> str:
    """ Создает превью pdf в виде изображения и сохраняет в хранилище, блокирующая"""
    first_page = convert_from_bytes(content_pdf, dpi, single_file=True)[0]
    preview_path = _get_preview_storage_path(filename)
    first_page.save(preview_path, format='PNG')
    return preview_path


def _get_exist_preview_path(filename: str) -> Optional[str]:
    path = _get_preview_storage_path(filename, False)
    if os.path.exists(path):
        return path
    return None


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
    background_task.add_task(remove_file, _get_preview_storage_path(file.filename_preview))
    return schemas.FileInfo(extension=file.extension,
                            title=file.title,
                            id=file.md5,
                            created=False,
                            created_at=file.created_at)


async def get_file_preview(file_md5: str, preview_dpi: int) -> bytes:
    file = await _get_file_or_raise(file_md5)

    if file.extension == 'pdf':
        # Запуск в executor блокирующей функции
        return await _get_preview_pdf(file)
    elif file.extension in ['png', 'jpg', 'jpeg']:
        # Запуск в executor блокирующей функции
        return await asyncio.get_event_loop().run_in_executor(None, _get_preview_image, file, preview_dpi)
    else:
        raise custom_exceptions.NotSupportedFilePreviewException(file.md5, file.extension)


def get_url_preview(md5: str):
    return f'http://127.0.0.1:8000/files/preview/?file_id={md5}'


def file_info(f: models.File):
    file_info_item = schemas.FileInfoItem(
        url_preview=get_url_preview(f.md5),
        title=f.title,
        extension=f.extension,
        id=f.md5,
        created_at=f.created_at
    )
    return file_info_item


async def get_file_info(file_id):
    file = await _get_file_or_raise(file_id)
    return file_info(file)


async def get_files() -> List[schemas.FileInfoItem]:
    files = await models.File.objects.all()
    return list(map(file_info, files))


async def update_file_info(file_info: schemas.FileInfo):
    file = await _get_file_or_raise(file_info.id)

    file.extension = file_info.extension
    file.title = file_info.title

    await file.save()
    file_info.created = False
    return

import asyncio
import os.path
import pytest
import test_data
from src.apps.files import services
from src.config.db_config import database


def test__get_storage_path():
    pytest.skip('Переписать')
    path = services._get_storage_path('1234test.txt')
    path = "/".join(path.split('/')[:-1])
    assert os.path.exists(path)
    os.rmdir(path)
    path = "/".join(path.split('/')[:-1])
    os.rmdir(path)


def test__prev_path():
    path = '/home/storage/123/'
    assert services._prev_path(path) == '/home/storage'


def rollback_operations(func):
    @pytest.mark.asyncio
    async def inner(event_loop):
        async with database:
            async with database.transaction(force_rollback=True):
                await func(event_loop)

    return inner


@pytest.fixture(autouse=True)
def start_up_fixture():
    asyncio.get_event_loop().run_until_complete(database.connect())
    yield
    asyncio.get_event_loop().run_until_complete(database.disconnect())


@rollback_operations
async def test_create_file(event_loop):
    _, file = await services.create_or_get_exist_file(test_data.text_file.file_name, test_data.text_file.file_data)
    assert file.md5
    file_path = await services.get_file_path(file.md5)
    services.remove_file(file_path)


@rollback_operations
async def test_create_pdf(event_loop):
    is_new, file = await services.create_or_get_exist_file(test_data.pdf_file.file_name, test_data.pdf_file.file_data)
    if not is_new:
        pytest.skip("Уже существующий тестовый pdf файл")

    file_path = await services.get_file_path(file.md5)
    services.remove_file(file_path)


@rollback_operations
async def test_create_exist_file(event_loop):
    is_new, file = await services.create_or_get_exist_file(test_data.text_file.file_name,
                                                           test_data.text_file.file_data)
    if not is_new:
        pytest.skip("Уже существующий тестовый файл")

    is_new, file = await services.create_or_get_exist_file(test_data.text_file.file_name,
                                                           test_data.text_file.file_data)
    file_path = await services.get_file_path(file.md5)
    services.remove_file(file_path)
    assert not is_new, "Файл записался заново"

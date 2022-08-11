import os.path

from src.apps.files import services


def test__get_storage_path():
    path = services._get_storage_path('1234test.txt')
    path = "/".join(path.split('/')[:-1])
    assert os.path.exists(path)
    os.rmdir(path)
    path = "/".join(path.split('/')[:-1])
    os.rmdir(path)


def test__prev_path():
    path = '/home/storage/123/'
    assert services._prev_path(path) == '/home/storage'

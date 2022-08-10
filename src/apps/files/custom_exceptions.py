class NotFoundFileException(Exception):
    def __init__(self, file_md5: str):
        self.file_md5 = file_md5

    def __str__(self):
        return f'Файла с id {self.file_md5} не найден!'

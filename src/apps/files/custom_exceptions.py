class NotFoundFileException(Exception):
    def __init__(self, file_md5: str):
        self.file_md5 = file_md5

    def __str__(self):
        return f'Файла с id {self.file_md5} не найден!'


class NotSupportedFilePreviewException(Exception):
    def __init__(self, file_md5: str, extension: str):
        self.file_md5 = file_md5
        self.extension = extension

    def __str__(self):
        return f'Для файла с id {self.file_md5} и расширением {self.extension} не может быть отображено превью'

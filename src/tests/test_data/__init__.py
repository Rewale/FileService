import os

DEFAULT_PATH = os.path.abspath(os.path.dirname(__file__))


class TestData:
    def __init__(self, file_name, location=DEFAULT_PATH):
        self.location = location
        self.file_path = os.path.join(location, file_name)
        self.file_name = file_name

    @property
    def file_data(self) -> bytes:
        with open(self.file_path, 'rb') as f:
            return f.read()


pdf_file = TestData('test.pdf')
text_file = TestData('test_file.test')
image_file = TestData('test.png')

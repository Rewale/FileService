import os

import dotenv

dotenv.load_dotenv()
__DEFAULT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'files_storage'))

FILES_STORAGE_PATH = os.getenv('FILES_STORAGE_PATH') or __DEFAULT_PATH
PREVIEW_FILES_STORAGE_PATH = os.path.join(FILES_STORAGE_PATH, 'previews')
POSTGRES_URL = os.getenv('POSTGRES_URL')

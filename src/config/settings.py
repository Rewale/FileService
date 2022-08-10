import os

import dotenv

dotenv.load_dotenv()

FILES_STORAGE_PATH = os.getenv('FILES_STORAGE_PATH') or 'files_storage'
POSTGRES_URL = os.getenv('POSTGRES_URL')

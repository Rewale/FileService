from fastapi import APIRouter

from src.apps.files.endpoints.files_crud import files_crud_router

files_router = APIRouter()
files_router.include_router(files_crud_router, prefix='/files')

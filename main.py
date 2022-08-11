from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse, FileResponse

from src.apps.files.models import database, metadata, engine
from src.apps.files.routers import files_router
from src.apps.files.services import _get_not_found_image
from src.apps.files.custom_exceptions import NotFoundFileException, NotSupportedFilePreviewException

app = FastAPI()

app.state.database = database
app.include_router(files_router)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(NotFoundFileException)
async def not_found_file_exception_handler(request: Request, exc: NotFoundFileException):
    return JSONResponse(
        content={"message": "file not found"},
        status_code=404
    )


@app.exception_handler(NotSupportedFilePreviewException)
async def not_found_file_exception_handler(request: Request, exc: NotFoundFileException):
    return JSONResponse(
        content={"message": str(exc)},
        status_code=200
    )


@app.on_event("startup")
async def startup() -> None:
    database_ = app.state.database
    metadata.create_all(engine)
    if not database_.is_connected:
        await database_.connect()


@app.on_event("shutdown")
async def shutdown() -> None:
    database_ = app.state.database
    if database_.is_connected:
        await database_.disconnect()

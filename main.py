from fastapi import FastAPI
from src.apps.files.models import database, metadata, engine
from src.apps.files.routers import files_router

app = FastAPI()

app.state.database = database
app.include_router(files_router)


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

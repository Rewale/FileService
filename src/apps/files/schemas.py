from pydantic import BaseModel


class CreatedFileInfo(BaseModel):
    extension: str
    title: str
    id: str

import datetime
from typing import Optional

from pydantic import BaseModel


# TODO: Mixin
class CreatedFileInfo(BaseModel):
    extension: str
    title: str
    id: str
    created: bool
    created_at: Optional[datetime.datetime]


class FileB64Response(BaseModel):
    data_b64: str
    extension: str
    title: str
    id: str
    created_at: Optional[datetime.datetime]

import datetime
from typing import Optional

from pydantic import BaseModel


# TODO: Mixin
class FileInfo(BaseModel):
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


class FileInfoItem(BaseModel):
    url_preview: str
    title: str
    extension: str
    id: str
    created_at: datetime.datetime

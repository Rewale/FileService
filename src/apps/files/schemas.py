import datetime
from typing import Optional, List

from pydantic import BaseModel


# TODO: Mixin
class FileInfo(BaseModel):
    extension: str
    url_preview: Optional[str]
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


class FilterParams(BaseModel):
    extension: Optional[str]
    title_contains: Optional[str]
    # created_from: datetime.datetime
    # created_to: datetime.datetime


class ItemsPage(BaseModel):
    files: List[FileInfoItem]
    total_count: int

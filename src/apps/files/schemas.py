import datetime
from typing import Optional

from pydantic import BaseModel


class CreatedFileInfo(BaseModel):
    extension: str
    title: str
    id: str
    created: bool
    created_at: Optional[datetime.datetime]

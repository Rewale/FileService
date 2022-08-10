import datetime
import ormar
from src.config.db_config import metadata, database, engine


class File(ormar.Model):
    """ Информация о хранимом на сервисе файле """
    class Meta:
        metadata = metadata
        database = database

    id: int = ormar.Integer(primary_key=True)
    md5: str = ormar.String(max_length=32, unique=True)
    extension: str = ormar.String(max_length=20)
    created_at: datetime.datetime = ormar.DateTime(default=datetime.datetime.now)
    title: str = ormar.String(max_length=255)

    @property
    def filename(self) -> str:
        return f'{self.title}.{self.extension}'

import databases
import sqlalchemy
import src.config.settings as settings

engine = sqlalchemy.create_engine(settings.POSTGRES_URL)

metadata = sqlalchemy.MetaData()
database = databases.Database(settings.POSTGRES_URL)

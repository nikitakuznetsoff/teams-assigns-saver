import config
from models.base import Base
from sqlalchemy import create_engine


DSN = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(
    config.DB_USER, config.DB_PASS, config.DB_HOST, config.DB_PORT, config.DB_NAME
)

engine = create_engine(DSN)
Base.metadata.create_all(engine)


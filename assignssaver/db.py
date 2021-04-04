from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import config

DSN = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(
    config.DB_USER, config.DB_PASS, config.DB_HOST, config.DB_PORT, config.DB_NAME
)

def get_session():
    engine = create_engine(DSN)
    return sessionmaker(engine)

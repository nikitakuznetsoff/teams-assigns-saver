from models.base import Base
from sqlalchemy import Column, Integer, String, DateTime
import json

class LTIRegistration(Base):
    __tablename__ = 'lti_registrations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    iss = Column(String)
    client_id = Column(String)
    platform_auth_url = Column(String)
    platform_token_url = Column(String)
    platform_public_keyset_url = Column(String)

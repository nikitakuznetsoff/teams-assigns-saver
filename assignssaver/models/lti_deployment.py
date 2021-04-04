from models.base import Base
from sqlalchemy import Column, Integer, String, DateTime
import json

class LTIDeployment(Base):
    __tablename__ = 'lti_deployments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    deployment_id = Column(String)
    registration_id = Column(String)
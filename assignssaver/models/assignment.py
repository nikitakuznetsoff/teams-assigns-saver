from models.base import Base
from sqlalchemy import Column, Integer, String, DateTime
import json

class Assignment(Base):
    __tablename__ = 'assignments'

    id = Column(String, primary_key=True)
    class_id = Column(String)
    expiration_time = Column(DateTime)
    context = Column(String)

    def toDict(self):
        return { 
            'id': self.id, 
            'class_id': self.class_id, 
            'expiration_time': self.expiration_time.strftime("%Y-%m-%d %H:%M:%S"), 
            'context': self.context
        }

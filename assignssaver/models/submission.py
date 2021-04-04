from sqlalchemy import Column, String, Integer, Boolean
from models.base import Base
import json

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(String, primary_key=True)
    student_id = Column(String)
    assignment_id = Column(String)
    mark = Column(Integer, default=0)
    status = Column(Boolean, default=False)


    def toDict(self):
        return {
            'id': self.id, 
            'student_id': self.student_id, 
            'assignment_id': self.assignment_id,
            'mark': self.mark, 
        }
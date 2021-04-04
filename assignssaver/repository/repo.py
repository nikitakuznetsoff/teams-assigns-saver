from models import Assignment, Submission
from sqlalchemy import true

class Repository:
    def __init__(self):
        self.Session = None

    def set_session(self, Session):
        self.Session = Session

    def push_assignments(self, assignments, class_id):
        session = self.Session()
        for assignment in assignments:
            result = session.query(Assignment).filter(
                Assignment.id == assignment['id']
            ).first()
            
            if result:
                continue
            assignment_new = Assignment(
                id = assignment['id'],
                class_id = class_id,
                expiration_time = assignment['dueDateTime'],
                context = assignment['displayName']
            )
            session.add(assignment_new)
            
            if not assignment.get('submissions'):
                continue
            for submission in assignment['submissions']:
                submission_new = Submission(
                    id=submission['id'],
                    student_id=submission['userId'], 
                    assignment_id=assignment['id'],
                    mark=0,
                    status=False
                )
                session.add(submission_new)
        session.commit()


    def get_assignments(self, student_id):
        result = []
        session = self.Session()
        assigments = session.query(Assignment).\
            join(Submission, Submission.assignment_id == Assignment.id).\
            filter(Submission.student_id == student_id).\
            all()
        return assigments          
      
    
    def set_mark(self, student_id, assignment_id, mark):
        session = self.Session()
        submission = session.query(Submission).\
            filter(
                Submission.student_id == student_id, 
                Submission.assignment_id == assignment_id
            ).first()
        
        if not submission:
            raise ValueError()

        submission.mark = mark
        submission.status = True
        session.commit()

    
    def get_evaluated_unsync_assigns(self):
        session = self.Session()
        submissions = session.query(Submission).\
            filter(Submission.status.is_(True)).\
            filter(Submission.assignment_id != 'moodle-subm').\
            all()
        for sub in submissions:
            sub.status = False
        session.commit()
        return submissions
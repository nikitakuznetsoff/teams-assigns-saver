from models import Assignment, StudentAssignment

class Repository:
    def __init__(self):
        self.Session = None

    def set_session(self, Session):
        self.Session = Session

    def push_assignments(self, assignments, students, class_id):
        session = self.Session()
        for assignment in assignments:
            result = self.sess.query(Assignment).filter(
                Assignemnt.id == assignment['id']
            ).first()
            
            if result:
                continue
            
            new_assignment = Assignment(
                id = assignment['id'],
                class_id = class_id,
                expiration_time = assignment['expiration_time'],
                context = assignment['context']
            )
            session.add(new_assignment)

            for student in students:
                new_pair = StudentAssignment(
                    student_id=student, 
                    assignment_id=assignment['id']
                )
                session.add(new_pair)
        session.commit()


    def get_assignments(self, student_id):
        result = []
        session = self.Session()
        assigments = session.query(Assignment).\
            join(StudentAssignment, StudentAssignment.assignment_id == Assignment.id).\
            filter(StudentAssignment.student_id == student_id).\
            all()
        return assigments          
      
    
    def set_mark(self, student_id, assignment_id, mark):
        session = self.Session()
        assignment = session.query(StudentAssignment).\
            filter(student_id == student_id, assignment_id == assignment_id).first()
        
        if not assignment:
            raise ValueError()

        assignment.mark = mark
        assignment.stats = True
        session.commit()

    
    def get_evaluated_unsync_assigns(self):
        session = self.Session()
        assigments = session.query(StudentAssignment).\
            jfilter(StudentAssignment.status == True).\
            all()
        for assign in assignments:
            assign.status = False
        session.commit()
        return assignments
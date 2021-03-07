import config
from repository import Repository

import json
from flask import Flask, request, make_response, jsonify
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import InvalidRequestError
from werkzeug.exceptions import BadRequest



DSN = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(
    config.DB_USER, config.DB_PASS, config.DB_HOST, config.DB_PORT, config.DB_NAME
)
app = Flask(__name__)
engine = create_engine(DSN)
Session = sessionmaker(engine)
repository = Repository()
repository.set_session(Session=Session)


@app.route('/get', methods=['GET'])
def get_assignments():
    try:
        student_id = request.args.get('student_id')
    except ValueError:
        return "unexpected arguments in request", 400
    try:
        assignments = repository.get_assignments(student_id=student_id)
    except InvalidRequestError:
        return "internal error", 500
    assignments = [assign.toDict() for assign in assignments ]
    d = {"assignments": assignments}
    response = make_response(
        jsonify(d), 200
    )
    response.headers["Content-Type"] = "application/json"
    return response


# {
#     assignments: {
#       'id': assign['id'],
#       'displayName': assign['displayName'],
#       'dueDateTime': assign['dueDateTime'],
#       'assignedDateTime': assign['assignedDateTime'],
#       'status': assign['status'],
#       'grading': assign['grading'],
#       'submissions': []
#     },
#     class_id: []
# }
@app.route('/sync_push', methods=['POST'])
def push_assignments():
    try:
        body = request.get_json()
    except BadRequest:
        return "unexcepted request body", 400
    assignments = body.get('assignmets', None)
    class_id = body.get('class_id', None)

    if not assignments or not class_id:
        return "unexcepted request body", 400
    try:
        repository.push_assignments(
            assignments=assignments, 
            class_id=class_id
        )
    except InvalidRequestError:
        return "internal error", 500
    return "success", 200


@app.route('/sync_get', methods=['GET'])
def get_evaluated_assigns():
    try:
        class_id = request.args.get('class_id')
    except ValueError:
        return "unexpected arguments in request", 400
    try:
        assignments = repository.get_evaluated_unsync_assigns()
    except InvalidRequestError:
        return "internal error", 500
    assignments = [assign.toDict() for assign in assignments]
    return json.dumps(assignments), 200
    

# {
#     student_id: str,
#     assignment_id: str,
#     mark: int
# }
@app.route('/setmark', methods=['POST'])
def set_mark():
    try:
        body = request.get_json()
    except BadRequest:
        return "unexcepted request body", 400
    student_id = body.get('student_id')
    assignment_id = body.get('assignment_id')
    mark = body.get('mark')

    if not student_id or not assignment_id or not mark:
        return "unexpected request body", 400
    try:
        status = repository.set_mark(
            student_id=student_id,
            assignment_id=assignment_id,
            mark=mark
        )
    except ValueError:
        return "incorrect request params", 400
    except InvalidRequestError:
        return "internal error", 500
    return "success", 200


if __name__ == '__main__':
    app.run(host='0.0.0.0')

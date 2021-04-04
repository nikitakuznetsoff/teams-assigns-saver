from flask import Blueprint, redirect, request, make_response, jsonify, session, Response, render_template
import json
import xmltodict
# from authlib.jose import jwt
# from authlib.jose import JsonWebSignature
import jwt
# from cryptography.hazmat.primitives import serialization
from urllib.parse import urlencode
import requests
import uuid
from repository import LTIRepository
import db
import hashlib
import time
import config

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import argparse
import base64
import six
import struct

from jose import jwk
from jose.utils import base64url_decode

from datetime import datetime

# from jwcrypto.jws import JWS


Session = db.get_session()

lti_repository = LTIRepository()
lti_repository.set_session(Session=Session)

bg = Blueprint('lti', __name__, url_prefix='/lti', template_folder='templates')


@bg.route('', methods=['GET'])
def lti():
    scopes = ['https://purl.imsglobal.org/spec/lti-ags/scope/lineitem.readonly','https://purl.imsglobal.org/spec/lti-ags/scope/result/read.readonly', 'https://purl.imsglobal.org/spec/lti-ags/scope/score.createpost']
    token = get_access_token(scopes)
    session['token'] = token
    # print(token)
    lineitems = get_line_items(token)
    print(lineitems)
    # post_score(token)
    return render_template('auth.html', url=config.BASE_URL+'/lti/send')


@bg.route('/send')
def lti_send():
    user_id = 'b453620a-e741-4930-8ce6-4554f086e620'
    assign = {
        'id': 'moodle-assignment-id',
        'displayName': 'Молекулы-5',
        'dueDateTime': '2021-03-25 20:59:00',
        'assignedDateTime': '2021-03-25 20:59:00',
        'status': False,
        'grading': False,
        'submissions': [{
            'id': 'moodle-subm',
            'status': 'status',
            'userId': user_id
        }]
    }
    r = requests.post(
        "http://localhost:5000" + "/syncpush",
        json={'assignments': [assign], 'class_id': 'moodle_class'}
    )
    print(r.status_code)
    return render_template('go.html')


@bg.route('/mark', methods=['POST'])
def lti_mark():
    mark = request.get_json()['mark']
    post_score(session['token'])


@bg.route('/register', methods=['POST'])
def lti_register():
    '''Register new platform to tool'''
    params = request.form
    # need checking
    try:
        lti_repository.register_platform(
            iss=params['iss'],
            client_id=params['client_id'],
            platform_auth_url=params['platform_auth_url'],
            platform_token_url=params['platform_token_url'],
            platform_public_keyset_url=params['platform_public_keyset_url']
        )
    except:
        return "bad request", 400
    return "successful platform registation", 200


@bg.route('/login', methods=['POST'])
def lti_login():
    '''Tool authentication in platform'''
    params = request.form

    platform = lti_repository.get_registration_by_iss_and_client(
        iss=params['iss'],
        client_id=params['client_id'] 
    )

    if not platform:
        return "unregstered platform", 400

    session['state'] = str(uuid.uuid4())
    session['client_id'] = params['client_id']

    auth_params = {
        'response_type': 'id_token',
        'response_mode': 'form_post',
        'scope': 'openid',
        'prompt': 'none',
        'redirect_uri': 'http://localhost:5000/lti/launch',
        'client_id': params['client_id'],
        'state': session['state'],
        'nonce': str(uuid.uuid4()),
        'lti_message_hint': params['lti_message_hint'],
        'login_hint': params['login_hint'],
        'lti_deployment_id': params['lti_deployment_id']
    }
    
    lti_repository.create_deployment(
        registration_id=platform.id,
        deployment_id=params['lti_deployment_id']
    )
    

    url_params = urlencode(auth_params)
    resp = Response()
    resp.status_code = 302
    resp.headers['Location'] = platform.platform_auth_url + '/?' + url_params
    return resp


@bg.route('/launch', methods=['POST'])
def lti_launch():
    '''Get authenticaton'''
    url = 'http://localhost:8080/moodle/mod/lti/certs.php'
    
    
    params = request.form
    id_token_encoded = params.get('id_token')
    state = params.get('state')


    r = requests.get(url)
    key = r.json()['keys'][0]

    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
    pubk_bytes = public_key.public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo)
    claim = jwt.decode(id_token_encoded, pubk_bytes, audience=session['client_id'], algorithms=['RS256'])
    # print(claim)
    session['body'] = claim
    return redirect('http://localhost:5000/lti')



def get_access_token(scopes):
    client_id = session['client_id']
    jwt_d = {
        'iss': client_id,
        'sub': client_id,
        'aud': 'http://localhost:8080/moodle/mod/lti/token.php',
        'iat': int(time.time()) - 5,
        'exp': int(time.time()) + 10000,
        'jti': str(hashlib.sha256(str.encode('asdasdasd')))
    }

    f = open('rsa_keys/private.key', 'rb')
    tool_private_key = f.read()
    # print(tool_private_key)

    jwt_token = jwt.encode(jwt_d, tool_private_key, algorithm='RS256')
     
    auth_request = {
         'grant_type': 'client_credentials',
         'client_assertion_type':'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
         'client_assertion': jwt_token,
         'scope': "https://purl.imsglobal.org/spec/lti-ags/scope/result.readonly https://purl.imsglobal.org/spec/lti-ags/scope/score"
     }
    auth_request = urlencode(auth_request)
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    r = requests.post(
        'http://localhost:8080/moodle/mod/lti/token.php', 
        data=auth_request,
        headers=headers
    )
    print(r.text)
    result = r.json()
    return result['access_token']


def create_line_item():
    d = {
        'id': id,
        'score_maximum': 10,
        'label': 1,
        'resource_id': session['body']['https://purl.imsglobal.org/spec/lti/claim/resource_link']['id'],
        'tag': 1,
        # 'start'
    }

def get_line_items(token):
    url = session['body']['https://purl.imsglobal.org/spec/lti-ags/claim/endpoint']['lineitem']
    # ind = url.index('/lineitem?')
    # url = url[:ind]
    print(url)
    h = {'Accept': 'application/vnd.ims.lis.v2.lineitem+json', 'Authentication': 'Bearer {0}'.format(token)}
    r = requests.get(url, headers=h)
    return r.text


def post_score(token):
    url = session['body']['https://purl.imsglobal.org/spec/lti-ags/claim/endpoint']['lineitem']
    ind = url.index('/lineitem?')
    url = url[:ind]+'/score'
    print(url)

    lis_res = session['body']['https://purl.imsglobal.org/spec/lti-bo/claim/basicoutcome']['lis_result_sourcedid']
    lis_res = json.loads(lis_res)

    score = {
        "timestamp": "2021-03-24T08:55:36.736+00:00",
        "scoreGiven" : 6,
        "scoreMaximum" : 10,
        "comment" : "Exellent work!",
        "activityProgress" : "Completed",
        "gradingProgress": "FullyGraded",
        "userId" : lis_res["data"]["userid"]
    }
    h = {'Content-Type': 'application/vnd.ims.lis.v1.score+json', 'Authentication': 'Bearer {0}'.format(token)}
    r = requests.post(url, headers=h, data=score)
    print(r.text)
    return False
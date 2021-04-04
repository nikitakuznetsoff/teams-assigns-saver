# from assignssaver import config
# from models.base import Base
# from sqlalchemy import create_engine
import requests

# DSN = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(
#     config.DB_USER, config.DB_PASS, config.DB_HOST, config.DB_PORT, config.DB_NAME
# )

# engine = create_engine(DSN)
# Base.metadata.create_all(engine)

d = { 
    'iss': 'http://localhost:8080/moodle',
    'client_id': 'XOzrCbTiWfDMiXS',
    'platform_auth_url': 'http://localhost:8080/moodle/mod/lti/auth.php',
    'platform_token_url': 'http://localhost:8080/moodle/mod/lti/token.php',
    'platform_public_keyset_url': 'http://localhost:8080/moodle/mod/lti/certs.php'
}
r = requests.post('http://localhost:5000/lti/register', data=d)
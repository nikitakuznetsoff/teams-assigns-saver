from models import LTIDeployment, LTIRegistration
from sqlalchemy import true

class LTIRepository:
    def __init__(self):
        self.Session = None

    def set_session(self, Session):
        self.Session = Session

    def register_platform(self, 
                        iss, 
                        client_id, 
                        platform_auth_url, 
                        platform_token_url,
                        platform_public_keyset_url):
        session = self.Session()
        reg = LTIRegistration(
            iss=iss,
            client_id=client_id,
            platform_auth_url=platform_auth_url,
            platform_token_url = platform_token_url,
            platform_public_keyset_url = platform_public_keyset_url)
        session.add(reg)
        session.commit()


    def get_registration_by_iss_and_client(self, iss, client_id):
        session = self.Session()
        reg = session.query(LTIRegistration).\
            filter(LTIRegistration.iss == iss, LTIRegistration.client_id == client_id).\
            first()
        return reg


    def create_deployment(self, registration_id, deployment_id):
        session = self.Session()
        depl = LTIDeployment(
            deployment_id = deployment_id,
            registration_id = registration_id
        )
        session.add(depl)
        session.commit()


    def get_registration_by_deployment_id(self, deployment_id):
        session = self.Session()
        reg = session.query(LTIRegistration).\
            join(LTIDeployment, LTIDeployment.registration_id == LTIRegistration.id).\
            filter(LTIDeployment.deployment_id == deployment_id).\
            first()
        return reg

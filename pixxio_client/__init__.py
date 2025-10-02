import logging
import requests

class Authentication:
    
    def __init__(self, api_key):
        self.api_key = api_key
        return
    
    def authenticate_client(self, client_session):
        client_session.headers.update(
            {"Authorization": f"Bearer {self.api_key}"}
        )
        return
        

class Client:
    
    def __init__(self, authentication, host, port=None, version = 'v1', logger=None):
        self.authentication = authentication
        self._host = host
        self._port = port
        self._version = version
        #
        if logger is None:
            self.logger = logging.getLogger("pixx!o client")
        else:
            self.logger = logger
        #
        host = host.lower()
        if not host.startswith('http'):
            host = '%s://%s' % ('https', host)
        if host.endswith('/'):
            host = host[:-1]
        if port is not None:
            host = '%s:%s' % (host, port)
        self.location_base = '%s/api/%s' % (host, version)
        self._session = None
        return
    
    @staticmethod
    def create_client(api_key, host):
        return Client(
            host=host, 
            authentication=Authentication(api_key))
        
    @property
    def session(self):
        if self._session is None:
            self._session = requests.Session()
            self.authentication.authenticate_client(
                self._session
            )
        return self._session
    
    def reset(self):
        self._session = None
        return


    
        
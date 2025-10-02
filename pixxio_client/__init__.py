import logging
from typing import Optional
import requests
from requests import Session

from .pixxio_types import APIKey


class Authentication:
    """Handles Bearer token authentication for PIXXIO API."""
    
    def __init__(self, api_key: APIKey) -> None:
        self.api_key = api_key
    
    def authenticate_client(self, client_session: Session) -> None:
        """Add Bearer token authentication headers to the session."""
        client_session.headers.update(
            {"Authorization": f"Bearer {self.api_key}"}
        )
        

class Client:
    """Main client for interacting with the PIXXIO API."""
    
    def __init__(self, authentication: Authentication, host: str, 
                 port: Optional[int] = None, version: str = 'v1', 
                 logger: Optional[logging.Logger] = None) -> None:
        self.authentication = authentication
        self._host = host
        self._port = port
        self._version = version
        
        if logger is None:
            self.logger = logging.getLogger("pixx!o client")
        else:
            self.logger = logger
        
        host = host.lower()
        if not host.startswith('http'):
            host = f'https://{host}'
        if host.endswith('/'):
            host = host[:-1]
        if port is not None:
            host = f'{host}:{port}'
        self.location_base = f'{host}/api/{version}'
        self._session: Optional[Session] = None
    
    @staticmethod
    def create_client(api_key: APIKey, host: str) -> 'Client':
        """Create a client with API key authentication."""
        return Client(
            host=host, 
            authentication=Authentication(api_key))
        
    @property
    def session(self) -> Session:
        """Get or create authenticated HTTP session."""
        if self._session is None:
            self._session = requests.Session()
            self.authentication.authenticate_client(self._session)
        return self._session
    
    def reset(self) -> None:
        """Reset the HTTP session, forcing re-authentication on next use."""
        self._session = None


    
        
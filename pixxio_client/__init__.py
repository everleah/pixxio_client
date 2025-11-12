"""
PIXXIO API Client Library

This module provides the main client interface for interacting with the PIXXIO digital
asset management (DAM) REST API. It includes authentication handling and session
management for making API requests.

The client library follows a resource-based architecture where each API endpoint
is represented by a dedicated class inheriting from base classes with common
functionality.

Example:
    Basic usage of the PIXXIO client:
    
    ```python
    from pixxio_client import Client, Authentication
    from pixxio_client.files import File
    
    # Create authenticated client
    client = Client.create_client("your-api-key", "your-host.com")
    
    # Use resource endpoints
    files = File(client)
    result = files.get()  # List all files
    file_detail = files.get(id=123)  # Get specific file
    ```

Classes:
    Authentication: Handles Bearer token authentication for API requests
    Client: Main client for managing API connections and session state
"""

import logging
from typing import Optional
import requests
from requests import Session

from .pixxio_types import APIKey


class Authentication:
    """
    Handles Bearer token authentication for PIXXIO API requests.
    
    This class manages API key authentication using the Bearer token method
    required by the PIXXIO REST API. It automatically adds the proper
    Authorization header to HTTP requests.
    
    Attributes:
        api_key (APIKey): The PIXXIO API key for authentication
        
    Example:
        ```python
        auth = Authentication("your-api-key-here")
        session = requests.Session()
        auth.authenticate_client(session)
        # Session now has Authorization: Bearer your-api-key-here
        ```
    """
    
    def __init__(self, api_key: APIKey) -> None:
        """
        Initialize authentication with API key.
        
        Args:
            api_key: The PIXXIO API key obtained from your PIXXIO account
        """
        self.api_key = api_key
    
    def authenticate_client(self, client_session: Session) -> None:
        """
        Add Bearer token authentication headers to the HTTP session.
        
        This method updates the session headers to include the Authorization
        header with the Bearer token format required by PIXXIO API.
        
        Args:
            client_session: The requests.Session object to authenticate
            
        Note:
            This method modifies the session in-place by updating its headers.
            All subsequent requests using this session will include the
            authentication header.
        """
        client_session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json"
            }
        )
        

class Client:
    """
    Main client for interacting with the PIXXIO API.
    
    This class manages the HTTP session, authentication, and base URL construction
    for all API requests. It serves as the foundation for all resource-specific
    classes and handles connection state management.
    
    The client automatically constructs the proper API URLs and manages session
    state including authentication headers. It supports both HTTP and HTTPS
    connections and can be configured for different API versions.
    
    Attributes:
        authentication (Authentication): Authentication handler for API requests
        location_base (str): Base URL for all API endpoints
        logger (logging.Logger): Logger instance for debugging and monitoring
        
    Example:
        ```python
        # Method 1: Direct instantiation
        auth = Authentication("your-api-key")
        client = Client(auth, "your-host.com")
        
        # Method 2: Factory method (recommended)
        client = Client.create_client("your-api-key", "your-host.com")
        
        # Use with resource classes
        files = File(client)
        collections = Collection(client)
        ```
    """
    
    def __init__(self, authentication: Authentication, host: str, 
                 port: Optional[int] = None, version: str = 'v1', 
                 logger: Optional[logging.Logger] = None) -> None:
        """
        Initialize the PIXXIO API client.
        
        Args:
            authentication: Authentication instance with API credentials
            host: PIXXIO host domain (e.g., "your-company.pixxio.com")
            port: Optional port number for API connections
            version: API version to use (default: "v1")
            logger: Optional custom logger instance
            
        Note:
            The host parameter should not include the protocol (http/https).
            The client automatically uses HTTPS unless explicitly configured
            otherwise. Port numbers are typically not needed for standard
            PIXXIO installations.
        """
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
        """
        Factory method to create a client instance with API key authentication.
        
        This is the recommended way to create a client as it handles the
        Authentication object creation automatically. It's particularly useful
        when you only have an API key and don't need custom authentication
        behavior.

        Args:
            api_key: Your PIXXIO API key (Bearer token)
            host: PIXXIO host domain (e.g., "company.pixxio.com")

        Returns:
            Client: Fully configured client ready for API operations
            
        Example:
            ```python
            # Simple client creation
            client = Client.create_client("your-api-key", "company.pixxio.com")
            
            # Use immediately with resources
            from pixxio_client.files import File
            files = File(client)
            all_files = files.get()
            ```
        """
        return Client(
            host=host, 
            authentication=Authentication(api_key))
        
    @property
    def session(self) -> Session:
        """
        Get or create authenticated HTTP session.
        
        This property lazily creates and configures the HTTP session used for
        all API requests. The session includes proper authentication headers
        and connection pooling for efficient request handling.
        
        Returns:
            Session: Configured requests.Session with authentication headers
            
        Note:
            The session is created once and reused for all subsequent requests
            until reset() is called. This enables connection pooling and
            improves performance for multiple API calls.
        """
        if self._session is None:
            self._session = requests.Session()
            self.authentication.authenticate_client(self._session)
        return self._session
    
    def reset(self) -> None:
        """
        Reset the HTTP session, forcing re-authentication on next use.
        
        This method clears the current session, which will force creation
        of a new session with fresh authentication headers on the next
        API request. Useful for handling authentication token expiration
        or connection issues.
        
        Example:
            ```python
            client = Client.create_client("api-key", "company.pixxio.com")
            
            
            # Make some requests...
            files = File(client)
            
            # Reset if authentication issues occur
            client.reset()
            
            # Next request will use new session
            files.get()  # Creates new authenticated session
            ```
        """
        self._session = None


# Webhook parser exports (generalized approach - single EventData class handles all event types)
from .webhook_parser import (
    WebhookParser,
    WebhookEvent,
    EventData,
    parse_pixxio_webhook,
    EventAction,
    ResourceType,
    EventKey,
)

__all__ = [
    # Authentication and Client
    "Authentication",
    "Client",
    # Webhook Parser - Generalized Approach
    "WebhookParser",
    "WebhookEvent",
    "EventData",
    "parse_pixxio_webhook",
    "EventAction",
    "ResourceType",
    "EventKey",
]
        

    
        
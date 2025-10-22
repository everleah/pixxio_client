import json
import logging
from typing import Optional, Dict, Any, Union, List, IO, TYPE_CHECKING

from types import SimpleNamespace
from json import JSONEncoder
from requests import Response, Session

from .exceptions import get_response_exception
from .pixxio_types import (
    PIXXIOId, ResponseData, JSONDict, QueryParams, 
    ResponseFields, FileHandle, FileParams
)

if TYPE_CHECKING:
    from . import Client


class ReadOnlyResourceBase:
    """
    Base class for read-only API resources providing GET operations.
    
    This class provides the foundation for all API resources that support
    read operations. It handles URL construction, response field filtering,
    error handling, and response parsing. All resource classes should inherit
    from this class or its subclasses.
    
    The class automatically constructs endpoint URLs based on the client's
    base URL and the resource's NAME attribute. It supports response field
    filtering to limit the data returned by API calls.
    
    Attributes:
        NAME (str): The API endpoint name (must be defined by subclasses)
        client (Client): The API client instance for making requests
        endpoint_base (str): Full URL for this resource's endpoints
        response_fields (Optional[List[str]]): Fields to include in responses
        logger (logging.Logger): Logger for this resource
        
    Example:
        ```python
        # Subclass implementation
        class User(ReadOnlyResourceBase):
            NAME = "users"
            
        # Usage
        client = Client.create_client("api-key", "company.pixxio.com")
        users = User(client)
        all_users = users.get()
        user_123 = users.get(123)
        ```
    """
    _paged: bool = True
    NAME: str  # Must be defined by subclasses
    
    def __init__(self, client: 'Client', logger: Optional[logging.Logger] = None, 
                 response_fields: Optional[ResponseFields] = None) -> None:
        """
        Initialize the resource with client and optional configuration.
        
        Args:
            client: The API client instance for making requests
            logger: Optional custom logger (defaults to class name logger)
            response_fields: Optional list of fields to include in responses
        """
        self.client = client
        self.response_fields = response_fields
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(self.__class__.__name__)
        self.endpoint_base = f'{self.client.location_base}/{self.NAME}'
    
    def set_response_fields(self, response_fields: ResponseFields) -> None:
        """
        Set the list of fields to include in API responses.
        
        This method configures response field filtering to limit the data
        returned by API calls. Only the specified fields will be included
        in the response, which can improve performance and reduce bandwidth.
        
        Args:
            response_fields: List of field names to include in responses
            
        Example:
            ```python
            files = File(client)
            files.set_response_fields(['id', 'fileName', 'subject'])
            result = files.get()  # Only returns specified fields
            ```
        """
        self.response_fields = response_fields
    
    def set_response_field(self, response_field: str) -> int:
        """
        Add a single field to the response fields list.
        
        This method adds a field to the existing response fields list,
        or creates a new list if none exists. Duplicate fields are
        automatically prevented.
        
        Args:
            response_field: Name of the field to add to response filtering
            
        Returns:
            int: Total number of fields in the response fields list
            
        Example:
            ```python
            files = File(client)
            files.set_response_field('id')
            files.set_response_field('fileName')
            count = files.set_response_field('subject')  # Returns 3
            ```
        """
        if self.response_fields and response_field not in self.response_fields:
            self.response_fields.append(response_field)
        elif not self.response_fields:
            self.response_fields = [response_field]
        return len(self.response_fields)

    def _transform_params(self, params_dict: dict) -> List[tuple[str, str]]:
        """
        Transform query parameters into the required format.
        
        This method processes query parameters to ensure they are in the
        correct format for API requests. It handles lists, booleans, and
        other data types as needed.

        Args:
            params_dict: The original query parameters as a dictionary

        Returns:
            QueryParams: Transformed query parameters suitable for requests
        """
        transformed = []
        for key, value in params_dict.items():
            if isinstance(value, list):
                for item in value:
                    transformed.append((key, str(item)))
            elif isinstance(value, bool):
                transformed.append((key, str(value).lower()))
            elif value is not None:
                transformed.append((key, str(value)))

        return transformed


    def _get(self, endpoint_base: str, **params: Any) -> ResponseData:
        """
        Internal GET method with automatic response field handling.
        
        This method handles the low-level HTTP GET request with automatic
        inclusion of response fields if configured. It also handles
        request exceptions and response parsing.
        
        Args:
            endpoint_base: The full URL for the GET request
            **params: Additional query parameters for the request
            
        Returns:
            ResponseData: Parsed response data as SimpleNamespace object
            
        Raises:
            PIXXIOException: If the request fails or response is invalid
        """
        if self.response_fields:
            params.update({"responseFields": self.response_fields})
        
        # Add default pagination parameters if not provided (only for list requests)
        # Individual item requests (with ID in URL) don't need pagination
        is_list_request = endpoint_base == self.endpoint_base
        if is_list_request and self._paged:
            if 'page' not in params:
                params['page'] = 1
            if 'pageSize' not in params:
                params['pageSize'] = 50  # Default page size
            
        try:
            response = self.client.session.get(
                endpoint_base,
                params=params
            )
        except Exception as ex:
            raise get_response_exception(ex)
        return self._parseResponse(response)
    
    def get(self, id: Optional[PIXXIOId] = None, **params: Any) -> ResponseData:
        """
        Get resource(s) by ID or list all resources.
        
        This is the primary method for retrieving resources. When called without
        an ID, it returns a list of all resources. When called with an ID,
        it returns the specific resource.
        
        Args:
            id: Optional resource ID to retrieve a specific item
            **params: Additional query parameters (filters, pagination, etc.)
            
        Returns:
            ResponseData: Resource data or list of resources
            
        Example:
            ```python
            files = File(client)
            
            # Get all files
            all_files = files.get()
            
            # Get specific file
            file_123 = files.get(123)
            
            # Get with filters
            filtered_files = files.get(keyword="landscape", quantity=10)
            ```
        """
        if id is None:
            return self._get(
                endpoint_base=self.endpoint_base, **params)
        return self._get(
            endpoint_base=f"{self.endpoint_base}/{id}", 
            **params)
    
    def _parseResponse(self, response: Response) -> ResponseData:
        """
        Parse HTTP response into a structured data object.
        
        This method converts HTTP responses into SimpleNamespace objects
        for easy attribute access. It handles JSON parsing, empty responses,
        and error conditions with appropriate exception raising.
        
        Args:
            response: The HTTP response object from requests
            
        Returns:
            ResponseData: Parsed response as SimpleNamespace object
            
        Raises:
            PIXXIOException: If response is invalid or indicates an error
            
        Note:
            - JSON responses are parsed into SimpleNamespace objects
            - 204 No Content responses return SimpleNamespace(success=True)
            - Non-OK status codes raise appropriate exceptions
        """
        if response is None:
            raise get_response_exception()
        content = response.text
        if content:
            try:
                response_object = Objectifier.from_json_str(content)
            except Exception as ex:
                raise get_response_exception(
                    message=f"invalid response; maybe not json: {content}\r\n(err:{ex})")
        elif response.status_code == 204:  # No Content
            response_object = SimpleNamespace(
                success=True
            )
        if not response.ok:
            raise get_response_exception(
                response_object=response_object, response=response)
        return response_object
    

class ResourceBase(ReadOnlyResourceBase):
    """
    Base class for full CRUD API resources with POST, PUT, DELETE operations.
    
    This class extends ReadOnlyResourceBase to provide complete CRUD (Create,
    Read, Update, Delete) functionality for API resources. It adds support for
    POST, PUT, and DELETE HTTP methods while maintaining all read functionality.
    
    The class supports multiple data formats including JSON, form data, and
    file uploads. It automatically handles different content types and provides
    consistent error handling across all operations.
    
    Attributes:
        Inherits all attributes from ReadOnlyResourceBase
        
    Example:
        ```python
        # Subclass for full CRUD operations
        class File(ResourceBase, ResourceUploadMixin):
            NAME = "files"
            
        # Usage
        files = File(client)
        
        # Create new resource
        new_file = files.post(data={'title': 'My Document'})
        
        # Update existing resource
        updated = files.put(123, data={'title': 'Updated Title'})
        
        # Delete resource
        result = files.delete(123)
        ```
    """
    
    def _post(
            self, endpoint_base: str, json_data: Optional[JSONDict] = None, 
            form_data: Optional[Dict[str, Any]] = None, 
            files: Optional[FileParams] = None, **params: Any) -> ResponseData:
        """
        Internal POST method with support for multiple data formats.
        
        This method handles HTTP POST requests with automatic content type
        detection based on the provided data. It supports JSON payloads,
        form data, and file uploads with proper encoding.
        
        Args:
            endpoint_base: The full URL for the POST request
            json_data: Optional JSON data to send in request body
            form_data: Optional form data for multipart/form-data requests
            files: Optional file data for uploads
            **params: Additional query parameters
            
        Returns:
            ResponseData: Parsed response data as SimpleNamespace object
            
        Raises:
            PIXXIOException: If the request fails or response is invalid
            
        Note:
            Only one of json_data, form_data, or files should be provided.
            The method automatically selects the appropriate content type.
        """
        try:
            response = self.client.session.post(
                endpoint_base,
                params=params,
                json=json_data,
                data=form_data,
                files=files
            )
        except Exception as ex:
            raise get_response_exception(ex)
        return self._parseResponse(response)
    
    def _put(self, endpoint_base: str, json_data: Optional[JSONDict] = None, 
             form_data: Optional[Dict[str, Any]] = None, **params: Any) -> ResponseData:
        """
        Internal PUT method for updating resources.
        
        This method handles HTTP PUT requests for resource updates. It supports
        both JSON and form data payloads with automatic content type handling.
        
        Args:
            endpoint_base: The full URL for the PUT request
            json_data: Optional JSON data to send in request body
            form_data: Optional form data for updates
            **params: Additional query parameters
            
        Returns:
            ResponseData: Parsed response data as SimpleNamespace object
            
        Raises:
            PIXXIOException: If the request fails or response is invalid
        """
        try:
            response = self.client.session.put(
                endpoint_base,
                params=params,
                json=json_data,
                data=form_data
            )
        except Exception as ex:
            raise get_response_exception(ex)
        return self._parseResponse(response)
    
    def _delete(self, endpoint_base: str, **params: Any) -> ResponseData:
        """
        Internal DELETE method for removing resources.
        
        This method handles HTTP DELETE requests for resource removal.
        It supports query parameters for conditional deletion or
        additional options.
        
        Args:
            endpoint_base: The full URL for the DELETE request
            **params: Additional query parameters
            
        Returns:
            ResponseData: Parsed response data as SimpleNamespace object
            
        Raises:
            PIXXIOException: If the request fails or response is invalid
        """
        try:
            response = self.client.session.delete(
                endpoint_base,
                params=params
            )
        except Exception as ex:
            raise get_response_exception(ex)
        return self._parseResponse(response)
        
    def delete(self, **params: Any) -> ResponseData:
        """
        Delete resource(s) using DELETE method.
        
        This method performs resource deletion at the collection level.
        Some APIs support bulk deletion or filtering for deletion operations.
        
        Args:
            **params: Query parameters for deletion (filters, options, etc.)
            
        Returns:
            ResponseData: Result of the deletion operation
            
        Example:
            ```python
            files = File(client)
            result = files.delete(filter_param="value")
            ```
        """
        return self._delete(
            endpoint_base=self.endpoint_base, **params)
        
    def post(self, json_data: Optional[JSONDict] = None, 
             form_data: Optional[Dict[str, Any]] = None, 
             files: Optional[FileParams] = None, **params: Any) -> ResponseData:
        """
        Create new resource using POST method.
        
        This method creates new resources by posting data to the collection
        endpoint. It supports multiple data formats and automatically handles
        content type detection.
        
        Args:
            json_data: JSON payload for the new resource
            form_data: Form data for the new resource  
            files: File uploads for the new resource
            **params: Additional query parameters
            
        Returns:
            ResponseData: The created resource data
            
        Example:
            ```python
            collections = Collection(client)
            new_collection = collections.post(
                json_data={'name': 'My Collection', 'description': 'Test'}
            )
            ```
        """
        return self._post(
            endpoint_base=self.endpoint_base,
            json_data=json_data,
            form_data=form_data,
            files=files,
            **params)

    def put(self, id: PIXXIOId, json_data: Optional[JSONDict] = None, 
            form_data: Optional[Dict[str, Any]] = None, **params: Any) -> ResponseData:
        """
        Update specific resource by ID using PUT method.
        
        This method updates an existing resource identified by its ID.
        It supports both partial and complete updates depending on the
        API endpoint behavior.
        
        Args:
            id: The ID of the resource to update
            json_data: JSON payload with updated data
            form_data: Form data with updated fields
            **params: Additional query parameters
            
        Returns:
            ResponseData: The updated resource data
            
        Example:
            ```python
            collections = Collection(client)
            updated = collections.put(
                123, 
                json_data={'name': 'Updated Collection Name'}
            )
            ```
        """
        return self._put(
            endpoint_base=f"{self.endpoint_base}/{id}",
            json_data=json_data,
            form_data=form_data,
            **params)

class ResourceUploadMixin:
    """
    Mixin class providing file upload capability for resources.
    
    This mixin adds file upload functionality to resource classes by providing
    an upload() method that handles file operations with proper encoding.
    It integrates seamlessly with the ResourceBase POST functionality.
    
    Requirements:
        - Must be mixed with a class that has a post() method (e.g., ResourceBase)
        - The post() method must support files parameter
        
    Example:
        ```python
        class File(ResourceBase, ResourceUploadMixin):
            NAME = "files"
            
        # Usage
        files = File(client)
        result = files.upload(
            "/path/to/file.jpg",
            title="My Image",
            description="Uploaded via API"
        )
        ```
    """
    
    def upload(self, file_path: str, **form_data: Any) -> ResponseData:
        """
        Upload a file with optional form data parameters.
        
        This method handles file uploads by opening the file in binary mode
        and posting it to the API endpoint. Additional form data can be
        included for metadata or configuration.
        
        Args:
            file_path: Path to the file to upload
            **form_data: Additional form fields to include with the upload
            
        Returns:
            ResponseData: Result of the upload operation
            
        Raises:
            FileNotFoundError: If the specified file doesn't exist
            PIXXIOException: If the upload fails
            
        Example:
            ```python
            files = File(client)
            result = files.upload(
                "/path/to/image.jpg",
                title="My Photo",
                category="landscapes",
                keywords="nature,outdoor"
            )
            ```
        """
        with open(file_path, "rb") as f:
            files = {"file": f}
            # Type ignore because this is a mixin - post method comes from ResourceBase
            response_object = self.post(  # type: ignore[attr-defined]
                form_data=form_data, files=files)
        return response_object   


class ResourceJobMixin:
    """
    Mixin class providing async job tracking for resources.
    
    This mixin adds asynchronous operation support to resource classes by
    providing job tracking capabilities. It enables resources to handle
    long-running operations that return job IDs for status monitoring.
    
    The mixin automatically detects job IDs in API responses and provides
    methods to wait for job completion with configurable timeouts and
    polling intervals.
    
    Requirements:
        - Must be mixed with a class that has a 'client' attribute
        - The client must have access to the Job resource for status tracking
        
    Example:
        ```python
        class File(ResourceBase, ResourceJobMixin, ResourceUploadMixin):
            NAME = "files"
            
        # Usage - upload with job tracking
        files = File(client)
        result = files.post_and_wait(
            json_data={'convert': True, 'format': 'PDF'},
            timeout=600,  # 10 minutes
            poll_interval=5.0  # Check every 5 seconds
        )
        ```
    """
    
    def _get_job_resource(self):
        """
        Get Job resource instance for job tracking.
        
        Returns:
            Job: Job resource instance for monitoring async operations
        """
        from .jobs import Job  # Import here to avoid circular imports
        return Job(self.client)  # type: ignore[attr-defined]
    
    def _extract_job_id(self, response: ResponseData) -> Optional[PIXXIOId]:
        """
        Extract job ID from API response if present.
        
        This method checks for job ID in multiple common formats used
        by different API endpoints.
        
        Args:
            response: API response data to check for job ID
            
        Returns:
            Optional[PIXXIOId]: Job ID if found, None otherwise
        """
        if hasattr(response, 'jobID'):
            return getattr(response, 'jobID')
        elif hasattr(response, 'jobId'):
            return getattr(response, 'jobId') 
        elif hasattr(response, 'job_id'):
            return getattr(response, 'job_id')
        return None
    
    def post_and_wait(
        self, 
        timeout: int = 300,
        poll_interval: float = 2.0,
        **post_params: Any
    ) -> ResponseData:
        """
        Post operation and wait for completion if it returns a job ID.
        
        This method performs a POST operation and automatically handles job
        tracking if the response contains a job ID. It will poll the job
        status until completion or timeout.
        
        Args:
            timeout: Maximum time to wait for job completion (seconds, default: 300)
            poll_interval: Time between job status checks (seconds, default: 2.0) 
            **post_params: Parameters passed to the post method
            
        Returns:
            ResponseData: Final result data when operation completes, or original
                         response if no job ID was returned
                         
        Raises:
            JobTimeoutException: If job doesn't complete within timeout
            JobFailedException: If job fails during execution
            PIXXIOException: If the initial POST request fails
            
        Example:
            ```python
            files = File(client)
            result = files.post_and_wait(
                json_data={'operation': 'convert', 'format': 'PDF'},
                timeout=600,
                poll_interval=5.0
            )
            ```
        """
        response = self.post(**post_params)  # type: ignore[attr-defined]
        
        job_id = self._extract_job_id(response)
        if job_id:
            job_resource = self._get_job_resource()
            job_obj = job_resource.wait_for_completion(
                job_id=job_id,
                timeout=timeout,
                poll_interval=poll_interval
            )
            finished_data = getattr(job_obj, "finishedJobData", None)
            return finished_data or response
        return response
    
    async def async_post_and_wait(
        self,
        timeout: int = 300, 
        poll_interval: float = 2.0,
        **post_params: Any
    ) -> ResponseData:
        """
        Async version of post_and_wait for non-blocking job monitoring.
        
        This method provides an asynchronous interface for job tracking,
        allowing other operations to continue while waiting for job completion.
        Uses asyncio for non-blocking polling.
        
        Args:
            timeout: Maximum time to wait for job completion (seconds, default: 300)
            poll_interval: Time between job status checks (seconds, default: 2.0)
            **post_params: Parameters passed to the post method
            
        Returns:
            ResponseData: Final result data when operation completes, or original
                         response if no job ID was returned
                         
        Raises:
            JobTimeoutException: If job doesn't complete within timeout
            JobFailedException: If job fails during execution
            PIXXIOException: If the initial POST request fails
            
        Example:
            ```python
            import asyncio
            
            async def upload_and_process():
                files = File(client)
                result = await files.async_post_and_wait(
                    json_data={'operation': 'batch_process'},
                    timeout=1800,  # 30 minutes
                    poll_interval=10.0
                )
                return result
            
            # Usage
            result = asyncio.run(upload_and_process())
            ```
        """
        response = self.post(**post_params)  # type: ignore[attr-defined]
        
        job_id = self._extract_job_id(response)
        if job_id:
            job_resource = self._get_job_resource()
            job_obj = await job_resource.async_wait_for_completion(
                job_id=job_id,
                timeout=timeout,
                poll_interval=poll_interval
            )
            finished_data = getattr(job_obj, "finishedJobData", None)
            return finished_data or response
        return response


class _ResponseObject(SimpleNamespace):
    """
    Custom namespace object that returns None for missing attributes.
    
    This class extends SimpleNamespace to provide more graceful handling
    of missing attributes in API responses. Instead of raising AttributeError,
    it returns None for attributes that don't exist.
    
    This is particularly useful when working with API responses that may
    have varying field structures or optional fields.
    
    Example:
        ```python
        obj = _ResponseObject(id=123, name="test")
        print(obj.id)          # 123
        print(obj.name)        # "test"  
        print(obj.missing)     # None (no AttributeError)
        ```
    """

    def __getattribute__(self, value: str) -> Any:
        try:
            return super().__getattribute__(value)
        except AttributeError:
            return None


class _ObjectJSONEncoder(JSONEncoder):
    """
    Custom JSON encoder for serializing objects to JSON.
    
    This encoder handles custom objects by converting them to dictionaries
    using their __dict__ attribute. This enables serialization of complex
    objects that contain nested custom types.
    """

    def default(self, obj: Any) -> Dict[str, Any]:
        """
        Convert custom objects to JSON-serializable format.
        
        Args:
            obj: The object to serialize
            
        Returns:
            Dict[str, Any]: Dictionary representation of the object
        """
        return obj.__dict__


class Objectifier:
    """
    Utility class for converting JSON responses to namespace objects.
    
    This class provides static methods for converting between JSON strings
    and Python objects with dot notation access. It uses custom object hooks
    to create _ResponseObject instances that gracefully handle missing attributes.
    
    The class supports both serialization and deserialization with proper
    handling of nested objects and custom types.
    
    Example:
        ```python
        # Parse JSON response
        json_str = '{"id": 123, "user": {"name": "John", "email": "john@example.com"}}'
        obj = Objectifier.from_json_str(json_str)
        
        print(obj.id)              # 123
        print(obj.user.name)       # "John"  
        print(obj.missing_field)   # None
        
        # Convert back to JSON
        json_output = Objectifier.to_json_str(obj)
        ```
    """
    
    @staticmethod
    def from_json_str(json_data: str) -> ResponseData:
        """
        Convert JSON string to response object with dot notation access.
        
        This method parses JSON strings and converts them into _ResponseObject
        instances that support attribute access and graceful handling of
        missing fields.
        
        Args:
            json_data: JSON string to parse
            
        Returns:
            ResponseData: Parsed object with dot notation access
            
        Raises:
            json.JSONDecodeError: If the JSON string is invalid
        """
        return json.loads(json_data, object_hook=lambda d: _ResponseObject(**d))

    @staticmethod
    def to_json_str(obj: Any, json_encoder_cls: Optional[type] = None) -> str:
        """
        Convert object to JSON string using custom encoder.
        
        This method serializes Python objects to JSON strings with proper
        formatting and custom object handling.
        
        Args:
            obj: Object to serialize to JSON
            json_encoder_cls: Optional custom JSON encoder class
            
        Returns:
            str: Formatted JSON string representation
            
        Example:
            ```python
            data = SimpleNamespace(id=123, name="test")
            json_str = Objectifier.to_json_str(data)
            print(json_str)
            # Output: {
            #     "id": 123,
            #     "name": "test"
            # }
            ```
        """
        if json_encoder_cls is None:
            json_encoder_cls = _ObjectJSONEncoder
        return json.dumps(obj, indent=4, cls=json_encoder_cls)    
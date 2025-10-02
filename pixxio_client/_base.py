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
    """Base class for read-only API resources providing GET operations."""
    
    NAME: str  # Must be defined by subclasses
    
    def __init__(self, client: 'Client', logger: Optional[logging.Logger] = None, 
                 response_fields: Optional[ResponseFields] = None) -> None:
        self.client = client
        self.response_fields = response_fields
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(self.__class__.__name__)
        self.endpoint_base = f'{self.client.location_base}/{self.NAME}'
    
    def set_response_fields(self, response_fields: ResponseFields) -> None:
        """Set the list of fields to include in API responses."""
        self.response_fields = response_fields
    
    def set_response_field(self, response_field: str) -> int:
        """Add a single field to the response fields list."""
        if self.response_fields and response_field not in self.response_fields:
            self.response_fields.append(response_field)
        elif not self.response_fields:
            self.response_fields = [response_field]
        return len(self.response_fields)
    
    def _get(self, endpoint_base: str, **params: Any) -> ResponseData:
        """Internal GET method with response field handling."""
        if self.response_fields:
            params.update({"responseFields": self.response_fields})
        try:
            response = self.client.session.get(
                endpoint_base,
                params=params
            )
        except Exception as ex:
            raise get_response_exception(ex)
        return self._parseResponse(response)
    
    def get(self, id: Optional[PIXXIOId] = None, **params: Any) -> ResponseData:
        """Get resource(s) by ID or list all resources."""
        if id is None:
            return self._get(
                endpoint_base=self.endpoint_base, **params)
        return self._get(
            endpoint_base=f"{self.endpoint_base}/{id}", 
            **params)
    
    def _parseResponse(self, response: Response) -> ResponseData:
        """Parse HTTP response into a data object."""
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
    """Base class for full CRUD API resources extending read-only with POST, PUT, DELETE."""
    
    def _post(
            self, endpoint_base: str, json_data: Optional[JSONDict] = None, 
            form_data: Optional[Dict[str, Any]] = None, 
            files: Optional[FileParams] = None, **params: Any) -> ResponseData:
        """Internal POST method supporting JSON, form data, and file uploads."""
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
        """Internal PUT method for updating resources."""
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
        """Internal DELETE method for removing resources."""
        try:
            response = self.client.session.delete(
                endpoint_base,
                params=params
            )
        except Exception as ex:
            raise get_response_exception(ex)
        return self._parseResponse(response)
        
    def delete(self, **params: Any) -> ResponseData:
        """Delete resource(s) using DELETE method."""
        return self._delete(
            endpoint_base=self.endpoint_base, **params)
        
    def post(self, json_data: Optional[JSONDict] = None, 
             form_data: Optional[Dict[str, Any]] = None, 
             files: Optional[FileParams] = None, **params: Any) -> ResponseData:
        """Create new resource using POST method."""
        return self._post(
            endpoint_base=self.endpoint_base,
            json_data=json_data,
            form_data=form_data,
            files=files,
            **params)

    def put(self, id: PIXXIOId, json_data: Optional[JSONDict] = None, 
            form_data: Optional[Dict[str, Any]] = None, **params: Any) -> ResponseData:
        """Update specific resource by ID using PUT method."""
        return self._put(
            endpoint_base=f"{self.endpoint_base}/{id}",
            json_data=json_data,
            form_data=form_data,
            **params)

class ResourceUploadMixin:
    """Mixin class providing file upload capability for resources.
    
    This mixin requires the class to have a 'post' method available.
    Should be used with ResourceBase or its subclasses.
    """
    
    def upload(self, file_path: str, **form_data: Any) -> ResponseData:
        """Upload a file with optional form data parameters."""
        with open(file_path, "rb") as f:
            files = {"file": f}
            # Type ignore because this is a mixin - post method comes from ResourceBase
            response_object = self.post(  # type: ignore[attr-defined]
                form_data=form_data, files=files)
        return response_object   
    
    
class _ResponseObject(SimpleNamespace):
    """Custom namespace object that returns None for missing attributes."""

    def __getattribute__(self, value: str) -> Any:
        try:
            return super().__getattribute__(value)
        except AttributeError:
            return None


class _ObjectJSONEncoder(JSONEncoder):
    """JSON encoder for custom objects."""

    def default(self, obj: Any) -> Dict[str, Any]:
        return obj.__dict__


class Objectifier:
    """Utility class for converting JSON responses to namespace objects."""
    
    @staticmethod
    def from_json_str(json_data: str) -> ResponseData:
        """Convert JSON string to response object with dot notation access."""
        return json.loads(json_data, object_hook=lambda d: _ResponseObject(**d))

    @staticmethod
    def to_json_str(obj: Any, json_encoder_cls: Optional[type] = None) -> str:
        """Convert object to JSON string using custom encoder."""
        if json_encoder_cls is None:
            json_encoder_cls = _ObjectJSONEncoder
        return json.dumps(obj, indent=4, cls=json_encoder_cls)    
from typing import Optional, Dict, Any

from ._base import ResourceBase, ResourceUploadMixin
from .pixxio_types import PIXXIOId, ResponseData, JSONDict, FileParams


class Keyword(ResourceBase, ResourceUploadMixin):
    """Keyword resource with CSV import/export functionality."""
    
    NAME = "keywords"
    
    def put(self, id: PIXXIOId, **params: Any) -> None:
        """PUT method not available for keywords API."""
        raise NotImplementedError("not available in api")
    
    def post(self, json_data: Optional[JSONDict] = None, 
             form_data: Optional[Dict[str, Any]] = None, 
             files: Optional[FileParams] = None, **params: Any) -> ResponseData:
        """Import keywords using CSV endpoint instead of standard endpoint."""
        return self._post(
            endpoint_base=f"{self.endpoint_base}/csv",
            json_data=json_data,
            form_data=form_data,
            files=files,
            **params)
    
    def download(self, **params: Any) -> ResponseData:
        """Download keywords as CSV from the /csv endpoint."""
        return self._get(
            endpoint_base=f"{self.endpoint_base}/csv", 
            **params)
    
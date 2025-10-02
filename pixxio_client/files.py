from typing import Optional, Any

from ._base import ResourceBase, ResourceUploadMixin
from .pixxio_types import PIXXIOId, ResponseData


class File(ResourceBase, ResourceUploadMixin):
    """File resource for upload, download, and conversion operations."""
    
    NAME = "files"
    
    def download(self, id: Optional[PIXXIOId] = None, **params: Any) -> ResponseData:
        """Download file(s) using the /convert endpoint for format conversion."""
        if id is None:
            return self._get(
                endpoint_base=f"{self.endpoint_base}/convert", 
                **params)
        return self._get(
            endpoint_base=f"{self.endpoint_base}/{id}/convert", 
            **params)

        
    
    
    
    
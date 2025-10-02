from typing import Optional, Any

from ._base import ResourceBase, ResourceUploadMixin, ResourceJobMixin
from .pixxio_types import PIXXIOId, ResponseData


class File(ResourceBase, ResourceUploadMixin, ResourceJobMixin):
    """File resource for upload, download, and conversion operations with async job support."""
    
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
    
    def upload_and_wait(
        self, 
        file_path: str, 
        timeout: int = 300,
        poll_interval: float = 2.0,
        **form_data: Any
    ) -> ResponseData:
        """Upload a file and wait for processing to complete.
        
        Args:
            file_path: Path to the file to upload
            timeout: Maximum time to wait for processing (seconds)
            poll_interval: Time between status checks (seconds)
            **form_data: Additional form data for upload
            
        Returns:
            Final result when upload and processing completes
        """
        with open(file_path, "rb") as f:
            files = {"file": f}
            return self.post_and_wait(
                timeout=timeout,
                poll_interval=poll_interval,
                form_data=form_data,
                files=files
            )
    
    async def async_upload_and_wait(
        self,
        file_path: str,
        timeout: int = 300, 
        poll_interval: float = 2.0,
        **form_data: Any
    ) -> ResponseData:
        """Async upload a file and wait for processing to complete.
        
        Args:
            file_path: Path to the file to upload
            timeout: Maximum time to wait for processing (seconds)
            poll_interval: Time between status checks (seconds) 
            **form_data: Additional form data for upload
            
        Returns:
            Final result when upload and processing completes
        """
        with open(file_path, "rb") as f:
            files = {"file": f}
            return await self.async_post_and_wait(
                timeout=timeout,
                poll_interval=poll_interval,
                form_data=form_data,
                files=files
            )

        
    
    
    
    
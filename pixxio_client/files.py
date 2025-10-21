from typing import Optional, Any

from ._base import ResourceBase, ResourceUploadMixin, ResourceJobMixin
from .pixxio_types import PIXXIOId, ResponseData


class File(ResourceBase, ResourceUploadMixin, ResourceJobMixin):
    """
    File resource for managing digital assets in PIXXIO.
    
    This class provides comprehensive file management capabilities including
    upload, download, conversion, and metadata operations. It supports both
    synchronous and asynchronous operations with job tracking for long-running
    tasks like file processing and format conversion.
    
    The class combines multiple mixins to provide:
    - Full CRUD operations (ResourceBase)
    - File upload functionality (ResourceUploadMixin)  
    - Async job tracking (ResourceJobMixin)
    
    Example:
        ```python
        client = Client.create_client("api-key", "company.pixxio.com")
        files = File(client)
        
        # Upload a file
        result = files.upload("/path/to/image.jpg", title="My Image")
        
        # Upload with job tracking
        result = files.upload_and_wait(
            "/path/to/video.mp4", 
            timeout=600,
            title="My Video"
        )
        
        # Download/convert file
        converted = files.download(123, format="PDF", size="A4")
        
        # Get file metadata
        file_info = files.get(123)
        ```
    """
    
    NAME = "files"
    
    def upload_url(self, file_url: str, filename: Optional[str] = None, **json_data: Any) -> ResponseData:
        """
        Upload a file to PIXXIO using a remote file URL instead of a local file path.
        Optionally specify a filename for the uploaded asset.
        Additional metadata can be passed via json_data.
        """
        data = {"fileUrl": file_url}
        if filename:
            data["originalFilename"] = filename
        data.update(json_data)
        return self.post(json_data=data)

    def upload_url_and_wait(self, file_url: str, filename: Optional[str] = None, timeout: int = 300, poll_interval: float = 2.0, **form_data: Any) -> ResponseData:
        """
        Upload a file using a remote file URL and wait for processing to complete.
        Optionally specify a filename for the uploaded asset.
        Additional metadata can be passed via form_data.
        """
        data = {"fileUrl": file_url}
        if filename:
            data["originalFilename"] = filename
        data.update(form_data)
        return self.post_and_wait(timeout=timeout, poll_interval=poll_interval, json_data=data)

    def download(self, id: Optional[PIXXIOId] = None, **params: Any) -> ResponseData:
        """
        Download file(s) with optional format conversion.
        
        This method uses the PIXXIO /convert endpoint to download files with
        optional format conversion, resizing, or other processing options.
        When called without an ID, it can perform batch operations.
        
        Args:
            id: Optional file ID for specific file download
            **params: Conversion parameters such as:
                - format: Target format (PDF, JPG, PNG, etc.)
                - size: Target size for images/documents
                - quality: Compression quality (1-100)
                - dpi: Resolution for document conversion
                
        Returns:
            ResponseData: Download URL or conversion result information
            
        Example:
            ```python
            files = File(client)
            
            # Download original file
            download_info = files.download(123)
            
            # Convert to PDF
            pdf_result = files.download(123, format="PDF", size="A4")
            
            # Resize image
            resized = files.download(123, format="JPG", width=800, height=600)
            ```
        """
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
        """
        Upload a file and wait for processing to complete, extracting asset ID from job result.
        Handles duplicate scenario by returning existingFileID if present.
        Automatically JSON-encodes metadataStandard and metadataCustom if needed.
        """
        import json
        # JSON-encode metadata fields if needed
        for key in ("metadataStandard", "metadataCustom"):
            if key in form_data and not isinstance(form_data[key], str):
                form_data[key] = json.dumps(form_data[key])
        with open(file_path, "rb") as f:
            files = {"file": f}
            job_result = self.post_and_wait(
                timeout=timeout,
                poll_interval=poll_interval,
                form_data=form_data,
                files=files
            )
            # Try to extract asset ID from job_result
            asset_id = None
            # job_result may be a dict or SimpleNamespace
            if isinstance(job_result, dict):
                asset_id = job_result.get("id") or job_result.get("fileId")
                # Check for duplicateInfo
                duplicate_info = job_result.get("duplicateInfo")
                if duplicate_info:
                    asset_id = duplicate_info.get("existingFileID", asset_id)
            else:
                asset_id = getattr(job_result, "id", None) or getattr(job_result, "fileId", None)
                duplicate_info = getattr(job_result, "duplicateInfo", None)
                if duplicate_info:
                    asset_id = getattr(duplicate_info, "existingFileID", asset_id)
            # Attach asset_id to result for convenience
            if asset_id:
                if isinstance(job_result, dict):
                    job_result["asset_id"] = asset_id
                else:
                    setattr(job_result, "asset_id", asset_id)
            return job_result
    
    async def async_upload_and_wait(
        self,
        file_path: str,
        timeout: int = 300, 
        poll_interval: float = 2.0,
        **form_data: Any
    ) -> ResponseData:
        """
        Asynchronously upload a file and wait for processing to complete.
        
        This method provides a non-blocking version of upload_and_wait using
        asyncio. It allows other operations to continue while the file upload
        and processing happens in the background.
        
        Args:
            file_path: Path to the local file to upload
            timeout: Maximum time to wait for processing (seconds, default: 300)
            poll_interval: Time between status checks (seconds, default: 2.0) 
            **form_data: Additional metadata for the upload (same as upload_and_wait)
            
        Returns:
            ResponseData: Final result when upload and processing completes
            
        Raises:
            FileNotFoundError: If the specified file doesn't exist
            JobTimeoutException: If processing doesn't complete within timeout
            JobFailedException: If file processing fails
            PIXXIOException: If the upload request fails
            
        Example:
            ```python
            import asyncio
            
            async def batch_upload():
                files = File(client)
                
                # Upload multiple files concurrently
                tasks = [
                    files.async_upload_and_wait(
                        "/path/to/file1.jpg", 
                        title="File 1"
                    ),
                    files.async_upload_and_wait(
                        "/path/to/file2.pdf", 
                        title="File 2"
                    )
                ]
                
                results = await asyncio.gather(*tasks)
                return results
            
            # Usage
            results = asyncio.run(batch_upload())
            ```
        """
        with open(file_path, "rb") as f:
            files = {"file": f}
            return await self.async_post_and_wait(
                timeout=timeout,
                poll_interval=poll_interval,
                form_data=form_data,
                files=files
            )

    def update(
        self,
        ids=None,
        filter=None,
        **fields
    ) -> ResponseData:
        """
        Update existing files (metadata, attributes, etc) using the filesPut endpoint.
        Accepts all documented fields as kwargs. At least one of ids or filter is required.
        Automatically JSON-encodes metadataStandard and metadataCustom if needed.
        Returns jobID and success.
        """
        import json
        # Enforce mutual exclusion and required fields
        if (ids is None and filter is None) or (ids is not None and filter is not None):
            raise ValueError("Exactly one of 'ids' or 'filter' must be provided.")
        form_data = dict(fields)
        if ids is not None:
            form_data["ids"] = ids
        if filter is not None:
            form_data["filter"] = filter
        # JSON-encode metadata fields if needed
        for key in ("metadataStandard", "metadataCustom"):
            if key in form_data and not isinstance(form_data[key], str):
                form_data[key] = json.dumps(form_data[key])
        # Use PUT with multipart/form-data at the collection endpoint
        return self._put(endpoint_base=self.endpoint_base, form_data=form_data)
        
    
    
    
    
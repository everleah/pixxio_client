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
        Upload a file and wait for processing to complete.
        
        This method combines file upload with job tracking to ensure the upload
        and any associated processing (thumbnails, metadata extraction, etc.)
        completes before returning. This is particularly useful for files that
        require processing time.
        
        Args:
            file_path: Path to the local file to upload
            timeout: Maximum time to wait for processing (seconds, default: 300)
            poll_interval: Time between status checks (seconds, default: 2.0)
            **form_data: Additional metadata for the upload including:
                - title: File title/name
                - subject: File subject/description
                - keywords: Comma-separated keywords
                - category: File category
                - originalFilename: Override detected filename
                
        Returns:
            ResponseData: Final result when upload and processing completes
            
        Raises:
            FileNotFoundError: If the specified file doesn't exist
            JobTimeoutException: If processing doesn't complete within timeout
            JobFailedException: If file processing fails
            PIXXIOException: If the upload request fails
            
        Example:
            ```python
            files = File(client)
            
            # Simple upload with job tracking
            result = files.upload_and_wait("/path/to/image.jpg")
            
            # Upload with metadata and extended timeout
            result = files.upload_and_wait(
                "/path/to/large_video.mp4",
                timeout=1800,  # 30 minutes
                poll_interval=10.0,
                title="Product Demo Video",
                keywords="product,demo,marketing",
                category="videos"
            )
            ```
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

        
    
    
    
    
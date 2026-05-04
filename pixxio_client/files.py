import tempfile
import requests
import os

from typing import Optional, Any

from ._base import ResourceBase, ResourceUploadMixin, ResourceJobMixin, _ResponseObject
from .pixxio_types import PIXXIOId, ResponseData

class FileUpdateBuilder:
    """
    Builder for PIXXIO file update (filesPut) form fields.
    Supports fluent, chainable methods for all documented fields.
    Automatically JSON-encodes metadata fields as needed.
    Enforces mutual exclusion for ids/filter (last one wins).
    Usage:
        builder = FileUpdateBuilder()
        form_data = (
            builder
                .ids([123, 456])
                .description("Updated desc")
                .metadata_standard([...])
                .build()
        )
        files.update(**form_data)
    """
    def __init__(self):
        self._fields = {}

    def ids(self, value):
        self._fields["ids"] = value
        if "filter" in self._fields:
            del self._fields["filter"]
        return self

    def filter(self, value):
        self._fields["filter"] = value
        if "ids" in self._fields:
            del self._fields["ids"]
        return self

    def append_description(self, value: str):
        self._fields["appendDescription"] = value
        return self

    def create_date(self, value: str):
        self._fields["createDate"] = value
        return self

    def creator(self, value: str):
        self._fields["creator"] = value
        return self

    def description(self, value: str):
        self._fields["description"] = value
        return self

    def directory_id(self, value: int):
        self._fields["directoryID"] = value
        return self

    def download_locked(self, value: bool):
        self._fields["downloadLocked"] = value
        return self

    def file_name(self, value: str):
        self._fields["fileName"] = value
        return self

    def file_name_with_extension(self, value: str):
        self._fields["fileNameWithExtension"] = value
        return self

    def file_state_change_comment(self, value: str):
        self._fields["fileStateChangeComment"] = value
        return self

    def file_state_id(self, value: int):
        self._fields["fileStateID"] = value
        return self

    def keywords_recognition_to_add(self, value):
        self._fields["keywordsRecognitionToAdd"] = value
        return self

    def keywords_recognition_to_remove(self, value):
        self._fields["keywordsRecognitionToRemove"] = value
        return self

    def keywords_to_add(self, value):
        self._fields["keywordsToAdd"] = value
        return self

    def keywords_to_remove(self, value):
        self._fields["keywordsToRemove"] = value
        return self

    def language_codes_to_add(self, value):
        self._fields["languageCodesToAdd"] = value
        return self

    def language_codes_to_remove(self, value):
        self._fields["languageCodesToRemove"] = value
        return self

    def license_releases_to_add(self, value):
        self._fields["licenseReleasesToAdd"] = value
        return self

    def license_releases_to_remove(self, value):
        self._fields["licenseReleasesToRemove"] = value
        return self

    def location(self, value):
        self._fields["location"] = value
        return self

    def metadata_append_text(self, value):
        self._fields["metadataAppendText"] = value
        return self

    def metadata_custom(self, value):
        self._fields["metadataCustom"] = value
        return self

    def metadata_date(self, value):
        self._fields["metadataDate"] = value
        return self

    def metadata_focal_point(self, value):
        self._fields["metadataFocalPoint"] = value
        return self

    def metadata_language_to_add(self, value):
        self._fields["metadataLanguageToAdd"] = value
        return self

    def metadata_language_to_remove(self, value):
        self._fields["metadataLanguageToRemove"] = value
        return self

    def metadata_location(self, value):
        self._fields["metadataLocation"] = value
        return self

    def metadata_multi_selection_to_add(self, value):
        self._fields["metadataMultiSelectionToAdd"] = value
        return self

    def metadata_multi_selection_to_remove(self, value):
        self._fields["metadataMultiSelectionToRemove"] = value
        return self

    def metadata_selection(self, value):
        self._fields["metadataSelection"] = value
        return self

    def metadata_standard(self, value):
        self._fields["metadataStandard"] = value
        return self

    def metadata_text(self, value):
        self._fields["metadataText"] = value
        return self

    def model_releases_to_add(self, value):
        self._fields["modelReleasesToAdd"] = value
        return self

    def model_releases_to_remove(self, value):
        self._fields["modelReleasesToRemove"] = value
        return self

    def property_releases_to_add(self, value):
        self._fields["propertyReleasesToAdd"] = value
        return self

    def property_releases_to_remove(self, value):
        self._fields["propertyReleasesToRemove"] = value
        return self

    def rating(self, value: int):
        self._fields["rating"] = value
        return self

    def rotate_90_degrees_clockwise(self, value: bool):
        self._fields["rotate90DegreesClockwise"] = value
        return self

    def rotate_90_degrees_counter_clockwise(self, value: bool):
        self._fields["rotate90DegreesCounterClockwise"] = value
        return self

    def show_sub_versions(self, value: bool):
        self._fields["showSubVersions"] = value
        return self

    def subject(self, value: str):
        self._fields["subject"] = value
        return self

    def truncate_create_date(self, value: bool):
        self._fields["truncateCreateDate"] = value
        return self

    def truncate_creator(self, value: bool):
        self._fields["truncateCreator"] = value
        return self

    def truncate_description(self, value: bool):
        self._fields["truncateDescription"] = value
        return self

    def truncate_file_state(self, value: bool):
        self._fields["truncateFileState"] = value
        return self

    def truncate_location(self, value: bool):
        self._fields["truncateLocation"] = value
        return self

    def truncate_metadata_fields(self, value):
        self._fields["truncateMetadataFields"] = value
        return self

    def truncate_rating(self, value: bool):
        self._fields["truncateRating"] = value
        return self

    def truncate_subject(self, value: bool):
        self._fields["truncateSubject"] = value
        return self

    def upload_date(self, value: str):
        self._fields["uploadDate"] = value
        return self

    def user_id(self, value: int):
        self._fields["userID"] = value
        return self

    def set(self, key, value):
        self._fields[key] = value
        return self

    def build(self):
        import json
        result = dict(self._fields)
        for key in ("metadataStandard", "metadataCustom"):
            if key in result and not isinstance(result[key], str):
                result[key] = json.dumps(result[key])
        return result

class FileUploadBuilder:
    """
    Builder for PIXXIO file upload/update form fields.
    Supports fluent, chainable methods for all documented fields.
    Automatically JSON-encodes metadata fields as needed.
    Usage:
        builder = FileUploadBuilder()
        form_data = (
            builder
                .file_name("myfile.jpg")
                .description("Desc")
                .keywords(["tag1", "tag2"])
                .metadata_standard([...])
                .metadata_custom([...])
                .build()
        )
        files.upload_and_wait(path, **form_data)
    """
    def __init__(self):
        self._fields = {}

    def add_file_name_to_keywords(self, value: bool):
        """addFileNameToKeywords: bool"""
        self._fields["addFileNameToKeywords"] = value
        return self

    def add_keywords(self, value):
        """addKeywords: list[str]"""
        self._fields["addKeywords"] = value
        return self

    def add_seconds_to_newstamp(self, value: int):
        self._fields["addSecondsToNewstamp"] = value
        return self

    def append_description(self, value: str):
        self._fields["appendDescription"] = value
        return self

    def asynchronous_conversion(self, value: bool):
        self._fields["asynchronousConversion"] = value
        return self

    def clip_server_name(self, value: str):
        self._fields["clipServerName"] = value
        return self

    def collection_ids(self, value):
        self._fields["collectionIDs"] = value
        return self

    def colorspace(self, value: str):
        self._fields["colorspace"] = value
        return self

    def create_date(self, value: str):
        self._fields["createDate"] = value
        return self

    def creator(self, value: str):
        self._fields["creator"] = value
        return self

    def description(self, value: str):
        self._fields["description"] = value
        return self

    def directory_id(self, value: int):
        self._fields["directoryID"] = value
        return self

    def download_locked(self, value: bool):
        self._fields["downloadLocked"] = value
        return self

    def file_name(self, value: str):
        self._fields["fileName"] = value
        return self

    def file_state_id(self, value: int):
        self._fields["fileStateID"] = value
        return self

    def is_convertible(self, value: bool):
        self._fields["isConvertible"] = value
        return self

    def keywords(self, value):
        self._fields["keywords"] = value
        return self

    def keywords_based_on_settings(self, value):
        self._fields["keywordsBasedOnSettings"] = value
        return self

    def keywords_recognition(self, value):
        self._fields["keywordsRecognition"] = value
        return self

    def language_codes(self, value):
        self._fields["languageCodes"] = value
        return self

    def license_releases(self, value):
        self._fields["licenseReleases"] = value
        return self

    def location(self, value):
        self._fields["location"] = value
        return self

    def metadata_append_text(self, value):
        self._fields["metadataAppendText"] = value
        return self

    def metadata_custom(self, value):
        self._fields["metadataCustom"] = value
        return self

    def metadata_date(self, value):
        self._fields["metadataDate"] = value
        return self

    def metadata_focal_point(self, value):
        self._fields["metadataFocalPoint"] = value
        return self

    def metadata_language(self, value):
        self._fields["metadataLanguage"] = value
        return self

    def metadata_location(self, value):
        self._fields["metadataLocation"] = value
        return self

    def metadata_multi_selection(self, value):
        self._fields["metadataMultiSelection"] = value
        return self

    def metadata_selection(self, value):
        self._fields["metadataSelection"] = value
        return self

    def metadata_standard(self, value):
        self._fields["metadataStandard"] = value
        return self

    def metadata_text(self, value):
        self._fields["metadataText"] = value
        return self

    def metadata_to_copy(self, value):
        self._fields["metadataToCopy"] = value
        return self

    def migration_id(self, value: int):
        self._fields["migrationID"] = value
        return self

    def migration_md5_hash(self, value: str):
        self._fields["migrationMD5Hash"] = value
        return self

    def model_releases(self, value):
        self._fields["modelReleases"] = value
        return self

    def original_file_server_name(self, value: str):
        self._fields["originalFileServerName"] = value
        return self

    def original_height(self, value: int):
        self._fields["originalHeight"] = value
        return self

    def original_width(self, value: int):
        self._fields["originalWidth"] = value
        return self

    def property_releases(self, value):
        self._fields["propertyReleases"] = value
        return self

    def rating(self, value: int):
        self._fields["rating"] = value
        return self

    def replace_id(self, value: int):
        # mutually exclusive with version_id
        self._fields["replaceID"] = value
        if "versionID" in self._fields:
            del self._fields["versionID"]
        return self

    def rotation(self, value: int):
        self._fields["rotation"] = value
        return self

    def scan_clarifai(self, value: bool):
        self._fields["scanClarifai"] = value
        return self

    def subject(self, value: str):
        self._fields["subject"] = value
        return self

    def upload_date(self, value: str):
        self._fields["uploadDate"] = value
        return self

    def upload_link_guest_user_email(self, value: str):
        self._fields["uploadLinkGuestUserEmail"] = value
        return self

    def upload_link_guest_user_name(self, value: str):
        self._fields["uploadLinkGuestUserName"] = value
        return self

    def variant_file_id(self, value: int):
        self._fields["variantFileID"] = value
        return self

    def variant_stack_link_name(self, value: str):
        self._fields["variantStackLinkName"] = value
        return self

    def version_id(self, value: int):
        # mutually exclusive with replace_id
        self._fields["versionID"] = value
        if "replaceID" in self._fields:
            del self._fields["replaceID"]
        return self

    def set(self, key, value):
        self._fields[key] = value
        return self

    def build(self):
        import json
        result = dict(self._fields)
        for key in ("metadataStandard", "metadataCustom"):
            if key in result and not isinstance(result[key], str):
                result[key] = json.dumps(result[key])
        return result

class FileDeleteBuilder:
    """
    Builder for PIXXIO file delete (filesDelete) query fields.

    Enforces mutual exclusion for ids/filter (last one wins).
    Usage:
        delete_params = (
            FileDeleteBuilder()
                .ids([123, 456])
                .show_subversions(True)
                .build()
        )
        files.delete(**delete_params)
    """

    def __init__(self):
        self._fields = {}

    def ids(self, value):
        self._fields["ids"] = value
        if "filter" in self._fields:
            del self._fields["filter"]
        return self

    def filter(self, value):
        self._fields["filter"] = value
        if "ids" in self._fields:
            del self._fields["ids"]
        return self

    def show_subversions(self, value: bool):
        self._fields["showSubversions"] = value
        return self

    def showSubversions(self, value: bool):
        self._fields["showSubversions"] = value
        return self

    def set(self, key, value):
        self._fields[key] = value
        return self

    def build(self):
        return dict(self._fields)

class FileResponseObject(_ResponseObject):
    pass

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
    _response_field_filter = {
        "GET_LIST": ["uploadDate", "modifyDate", "createDate", "id", "fileName", "fileExtension", "fileType", "subject", "description", "width", "height", "pixel", "colorspace", "orientation", "fileSize", "md5sum", "keywords", "keywordsRecognition", "rating", "rotation", "fileState", "isDownloadLocked", "isArchived", "isRotatable", "isConvertible", "isCheckedOut", "isMainVersion", "hasSubversions", "originalFileURL", "previewFileURL", "clipFileURL", "modifiedPreviewFileURLs", "user", "creator", "location", "directory", "permissions", "metadataFields", "dominantColor", "variantStack", "languageCodes", "isMarked", "staticCollections", "versions", "importantMetadata", "licenseReleases", "modelReleases", "propertyReleases"],
        "GET_SINGLE": ["uploadDate", "modifyDate", "createDate", "id", "fileName", "fileExtension", "fileType", "subject", "description", "width", "height", "pixel", "colorspace", "orientation", "fileSize", "md5sum", "keywords", "keywordsRecognition", "rating", "rotation", "fileState", "isDownloadLocked", "isArchived", "isRotatable", "isConvertible", "isCheckedOut", "isMainVersion", "hasSubversions", "originalFileURL", "previewFileURL", "clipFileURL", "modifiedPreviewFileURLs", "user", "creator", "location", "directory", "permissions", "metadataFields", "dominantColor", "variantStack", "languageCodes", "isMarked", "staticCollections", "versions", "metadata", "importantMetadata", "unimportantMetadata", "usePanoramaViewer", "licenseReleases", "modelReleases", "propertyReleases"]
        }
    
    _get_single_response_cls = FileResponseObject

    def upload_url_and_wait(self, file_url: str,  timeout: int = 300, poll_interval: float = 2.0, **form_data: Any) -> ResponseData:
        """
        Upload a file using a remote file URL and wait for processing to complete.
        Optionally specify a filename for the uploaded asset.
        Additional metadata can be passed via form_data.
        """
        try:
            # Download remote file to temp location
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                response = requests.get(file_url)
                response.raise_for_status()
                tmp_file.write(response.content)
                tmp_file_path = tmp_file.name
        except Exception as e:
            raise RuntimeError(f"Failed to download file from URL: {e}")
        try:
            # Upload the downloaded file
            result = self.upload_and_wait(
                tmp_file_path,
                timeout=timeout,
                poll_interval=poll_interval,
                **form_data
            )
        finally:
            # Clean up temp file
            os.unlink(tmp_file_path)
        return result

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
        # The /convert endpoint does not support responseFields parameter
        with self._without_response_fields():
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

    def put(
        self,
        id: PIXXIOId,
        json_data=None,
        form_data=None,
        **params: Any,
    ) -> ResponseData:
        """
        Compatibility wrapper for file updates by a single file ID.

        The API exposes collection-level filesPut (PUT /files) with ids/filter,
        not PUT /files/{id}. This maps ResourceBase.put-style calls to filesPut.
        """
        if json_data is not None and form_data is not None:
            raise ValueError("Use either 'json_data' or 'form_data', not both.")

        fields = {}
        if json_data is not None:
            fields.update(json_data)
        if form_data is not None:
            fields.update(form_data)
        fields.update(params)

        return self.update(ids=[id], **fields)

    def delete(
        self,
        ids=None,
        filter=None,
        show_subversions: Optional[bool] = None,
        **params: Any,
    ) -> ResponseData:
        """
        Delete files using the filesDelete endpoint.

        Exactly one of ``ids`` or ``filter`` must be provided.

        Args:
            ids: List of file IDs to delete
            filter: Filter object selecting files to delete
            show_subversions: Maps to API parameter ``showSubversions``
            **params: Additional query parameters

        Returns:
            ResponseData: Deletion result (e.g. deletedFileIDs/notDeletedFileIDs)
        """
        # Enforce same contract as filesPut: exactly one selector is required.
        if (ids is None and filter is None) or (ids is not None and filter is not None):
            raise ValueError("Exactly one of 'ids' or 'filter' must be provided.")

        delete_params = dict(params)
        if ids is not None:
            delete_params["ids"] = ids
        if filter is not None:
            delete_params["filter"] = filter

        # Support both pythonic snake_case and raw API camelCase.
        if show_subversions is not None:
            if "showSubversions" in delete_params:
                raise ValueError("Use either 'show_subversions' or 'showSubversions', not both.")
            delete_params["showSubversions"] = show_subversions

        return self._delete(endpoint_base=self.endpoint_base, **delete_params)
        
    
    
    
    
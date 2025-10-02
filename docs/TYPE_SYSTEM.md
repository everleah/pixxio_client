# Type System Guide

This guide covers the comprehensive type system used throughout the PIXXIO Python client library.

## Overview

The PIXXIO client library includes full type hints based on the OpenAPI specification. This provides:

- **IDE Support**: Better autocomplete and error detection
- **Static Type Checking**: Catch errors before runtime with mypy
- **Documentation**: Types serve as inline documentation
- **API Contract**: Types match OpenAPI specification exactly

## Core Type Definitions

### Basic Types

Located in `pixxio_client/pixxio_types.py`:

```python
from typing import Union, Dict, List, Any, Optional, IO
from types import SimpleNamespace

# Resource identifiers
PIXXIOId = Union[int, str]

# API response data
ResponseData = Union[SimpleNamespace, Dict[str, Any]]

# JSON data structures
JSONDict = Dict[str, Any]
QueryParams = Dict[str, Any]

# Response field filtering
ResponseFields = List[str]

# File handling
FileHandle = Union[IO[bytes], IO[str]]
FileParams = Dict[str, FileHandle]

# API key type
APIKey = str
```

### Usage Examples

```python
from pixxio_client.pixxio_types import PIXXIOId, ResponseData, JSONDict

def get_file(file_id: PIXXIOId) -> ResponseData:
    """Get file by ID - accepts int or string ID."""
    return files.get(file_id)

def create_collection(data: JSONDict) -> ResponseData:
    """Create collection with JSON data."""
    return collections.post(json_data=data)

# Type-safe usage
file_info = get_file(123)        # int ID
file_info = get_file("abc123")   # string ID

collection_data: JSONDict = {
    'name': 'My Collection',
    'description': 'Test collection'
}
new_collection = create_collection(collection_data)
```

## Job System Types

### Job Status Enum

```python
from enum import Enum

class JobStatus(str, Enum):
    """Job execution status values."""
    PENDING = "pending"
    RUNNING = "running"  
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
```

### Job Information Dataclass

```python
from dataclasses import dataclass
from typing import Optional, Any
from datetime import datetime

@dataclass
class JobInfo:
    """Comprehensive job information."""
    id: PIXXIOId
    status: JobStatus
    progress: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result_data: Optional[ResponseData] = None
    
    def is_complete(self) -> bool:
        """Check if job has finished (success or failure)."""
        return self.status in [JobStatus.SUCCESS, JobStatus.FAILED, JobStatus.CANCELLED]
    
    def is_successful(self) -> bool:
        """Check if job completed successfully."""
        return self.status == JobStatus.SUCCESS
```

### Usage Examples

```python
from pixxio_client.pixxio_types import JobStatus, JobInfo

def monitor_job(job_id: PIXXIOId) -> JobInfo:
    """Monitor job with proper typing."""
    jobs = Job(client)
    
    while True:
        job_info: JobInfo = jobs.get_job_info(job_id)
        
        print(f"Job {job_info.id}: {job_info.status.value} ({job_info.progress}%)")
        
        if job_info.is_complete():
            if job_info.is_successful():
                print("Job completed successfully!")
                return job_info
            else:
                print(f"Job failed: {job_info.error_message}")
                raise JobFailedException(job_info.error_message)
        
        time.sleep(2.0)
```

## Callback Types

### Function Signatures

```python
from typing import Callable, Optional, Awaitable

# Progress callback for job monitoring
ProgressCallback = Callable[[JobInfo], None]

# Completion callback for job completion
CompletionCallback = Callable[[JobInfo], None]

# Async callback types
AsyncProgressCallback = Callable[[JobInfo], Awaitable[None]]
AsyncCompletionCallback = Callable[[JobInfo], Awaitable[None]]

# Error callback for exception handling
ErrorCallback = Callable[[Exception], None]
```

### Usage with Callbacks

```python
def progress_handler(job_info: JobInfo) -> None:
    """Handle job progress updates."""
    print(f"Progress: {job_info.progress}%")
    
    if job_info.progress >= 50:
        print("Job is halfway complete!")

def completion_handler(job_info: JobInfo) -> None:
    """Handle job completion."""
    if job_info.is_successful():
        print("Upload completed successfully!")
    else:
        print(f"Upload failed: {job_info.error_message}")

# Type-safe callback usage
result = files.upload_with_callbacks(
    "/path/to/file.jpg",
    progress_callback=progress_handler,
    completion_callback=completion_handler
)
```

## Resource-Specific Types

### File Types

```python
from typing import Literal, Union

# File formats supported by PIXXIO
FileFormat = Literal[
    "JPG", "JPEG", "PNG", "GIF", "BMP", "TIFF",
    "PDF", "DOC", "DOCX", "PPT", "PPTX", "XLS", "XLSX",
    "MP4", "AVI", "MOV", "WMV", "FLV", "MKV"
]

# Image size specifications
ImageSize = Union[
    Literal["thumbnail", "small", "medium", "large", "original"],
    str  # Custom size like "800x600"
]

# Document page sizes
PageSize = Literal["A4", "A3", "Letter", "Legal", "Custom"]
```

### Collection Types

```python
# Collection sort options
CollectionSortBy = Literal[
    "name", "created", "updated", "fileCount", "size"
]

# Collection visibility
CollectionVisibility = Literal["private", "public", "shared"]
```

### Usage Examples

```python
def convert_image(
    file_id: PIXXIOId,
    target_format: FileFormat,
    size: ImageSize = "medium"
) -> ResponseData:
    """Convert image with type-safe parameters."""
    return files.download(
        file_id,
        format=target_format,
        size=size
    )

# Type-safe usage
result = convert_image(123, "PNG", "800x600")  # Custom size
result = convert_image(456, "JPG", "large")    # Predefined size
```

## Generic Types and Type Variables

### Resource Type Variables

```python
from typing import TypeVar, Generic, Type

# Type variable for resource classes
ResourceType = TypeVar('ResourceType', bound='ReadOnlyResourceBase')

class ResourceFactory(Generic[ResourceType]):
    """Factory for creating resource instances with proper typing."""
    
    def __init__(self, resource_class: Type[ResourceType]):
        self.resource_class = resource_class
    
    def create(self, client: 'Client') -> ResourceType:
        """Create resource instance with proper type."""
        return self.resource_class(client)

# Usage
file_factory = ResourceFactory(File)
files: File = file_factory.create(client)  # Properly typed as File
```

### Response Type Mapping

```python
from typing import TypedDict, NotRequired

class FileResponse(TypedDict):
    """Typed response for file operations."""
    id: PIXXIOId
    fileName: str
    fileSize: int
    mimeType: str
    createdAt: str
    updatedAt: str
    # Optional fields
    subject: NotRequired[str]
    description: NotRequired[str]
    keywords: NotRequired[str]

class CollectionResponse(TypedDict):
    """Typed response for collection operations."""
    id: PIXXIOId
    name: str
    description: NotRequired[str]
    fileCount: int
    createdAt: str
    updatedAt: str
```

## Type Checking with mypy

### Configuration

Create `mypy.ini` in project root:

```ini
[mypy]
python_version = 3.8
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True

# Per-module options
[mypy-requests.*]
ignore_missing_imports = True

[mypy-dateutil.*]
ignore_missing_imports = True
```

### Running Type Checks

```bash
# Check entire project
mypy pixxio_client/

# Check specific module
mypy pixxio_client/files.py

# Check with strict mode
mypy --strict pixxio_client/

# Generate type coverage report
mypy --html-report mypy_report pixxio_client/
```

### Common Type Issues and Fixes

**Issue 1: Missing return type**
```python
# Error
def get_file(id):  # Missing return type
    return files.get(id)

# Fix
def get_file(id: PIXXIOId) -> ResponseData:
    return files.get(id)
```

**Issue 2: Untyped function parameters**
```python
# Error
def upload_file(path, **kwargs):  # Missing parameter types
    return files.upload(path, **kwargs)

# Fix  
def upload_file(path: str, **kwargs: Any) -> ResponseData:
    return files.upload(path, **kwargs)
```

**Issue 3: Optional types not handled**
```python
# Error
def process_file(file_data):
    return file_data.id  # Could be None

# Fix
def process_file(file_data: Optional[ResponseData]) -> Optional[PIXXIOId]:
    if file_data is None:
        return None
    return getattr(file_data, 'id', None)
```

## Advanced Type Patterns

### Protocol for Resource Classes

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class SupportsUpload(Protocol):
    """Protocol for resources that support file upload."""
    
    def upload(self, file_path: str, **form_data: Any) -> ResponseData:
        """Upload a file."""
        ...

@runtime_checkable  
class SupportsJobTracking(Protocol):
    """Protocol for resources with job tracking."""
    
    def post_and_wait(
        self, 
        timeout: int = 300,
        poll_interval: float = 2.0,
        **params: Any
    ) -> ResponseData:
        """Post operation and wait for completion."""
        ...

# Type-safe resource usage
def upload_if_supported(resource: Any, file_path: str) -> Optional[ResponseData]:
    """Upload file if resource supports it."""
    if isinstance(resource, SupportsUpload):
        return resource.upload(file_path)
    return None

def wait_if_supported(resource: Any, **params: Any) -> Optional[ResponseData]:
    """Use job tracking if resource supports it."""
    if isinstance(resource, SupportsJobTracking):
        return resource.post_and_wait(**params)
    return None
```

### Union Types for Flexible Parameters

```python
from typing import Union, overload

# Flexible ID parameter
IdParameter = Union[PIXXIOId, List[PIXXIOId]]

@overload
def get_files(ids: PIXXIOId) -> ResponseData: ...

@overload  
def get_files(ids: List[PIXXIOId]) -> List[ResponseData]: ...

def get_files(ids: IdParameter) -> Union[ResponseData, List[ResponseData]]:
    """Get single file or multiple files based on input type."""
    if isinstance(ids, (int, str)):
        return files.get(ids)
    else:
        return [files.get(id) for id in ids]

# Type-safe usage
single_file = get_files(123)              # ResponseData
multiple_files = get_files([123, 456])    # List[ResponseData]
```

### Literal Types for API Parameters

```python
from typing import Literal

# Strictly typed API parameters
SortOrder = Literal["asc", "desc"]
SortField = Literal["name", "created", "updated", "size"]

def get_files_sorted(
    sort_by: SortField = "created",
    sort_order: SortOrder = "desc"
) -> ResponseData:
    """Get files with type-safe sorting parameters."""
    return files.get(sortBy=sort_by, sortOrder=sort_order)

# IDE will provide autocomplete and catch typos
result = get_files_sorted("name", "asc")    # Valid
result = get_files_sorted("invalid", "up")  # Type error
```

## Integration with IDE

### VS Code Configuration

Create `.vscode/settings.json`:

```json
{
    "python.linting.mypyEnabled": true,
    "python.linting.enabled": true,
    "python.analysis.typeCheckingMode": "strict",
    "python.analysis.autoImportCompletions": true,
    "python.analysis.completeFunctionParens": true
}
```

### PyCharm Configuration

1. Enable type checking: **Settings → Editor → Inspections → Python → Type checker**
2. Configure mypy: **Settings → Tools → External Tools → Add mypy**
3. Enable parameter hints: **Settings → Editor → Inlay Hints → Python**

## Type Documentation

### Documenting Types in Docstrings

```python
def upload_with_metadata(
    file_path: str,
    metadata: JSONDict,
    timeout: int = 300
) -> ResponseData:
    """
    Upload file with metadata.
    
    Args:
        file_path: Path to local file (must be valid file path string)
        metadata: File metadata dictionary. Expected keys:
            - title (str): File title  
            - description (str, optional): File description
            - keywords (str, optional): Comma-separated keywords
            - category (str, optional): File category
        timeout: Maximum wait time in seconds for upload completion
        
    Returns:
        ResponseData: Upload result with file information. Contains:
            - id (PIXXIOId): Unique file identifier
            - fileName (str): Uploaded file name
            - fileSize (int): File size in bytes
            - status (str): Upload status
            
    Raises:
        FileNotFoundError: If file_path does not exist
        JobTimeoutException: If upload doesn't complete within timeout
        PIXXIOException: If API request fails
        
    Example:
        ```python
        metadata = {
            'title': 'Product Photo',
            'keywords': 'product,photography,marketing',
            'category': 'images'
        }
        
        result = upload_with_metadata(
            '/path/to/photo.jpg',
            metadata,
            timeout=600
        )
        
        print(f"Uploaded file ID: {result.id}")
        ```
    """
    return files.upload_and_wait(file_path, timeout=timeout, **metadata)
```

### Type Stub Files

Create `.pyi` files for complex type definitions:

```python
# pixxio_client/types.pyi
from typing import Union, Dict, List, Any, Protocol
from types import SimpleNamespace

class PIXXIOResponse(Protocol):
    id: Union[int, str]
    status: str
    
    def __getattr__(self, name: str) -> Any: ...

ResponseData = Union[PIXXIOResponse, SimpleNamespace, Dict[str, Any]]
```

## Best Practices

### 1. Use Specific Types

```python
# Good: Specific type
def get_file_size(file_id: PIXXIOId) -> int:
    file_info = files.get(file_id)
    return file_info.fileSize

# Avoid: Generic type  
def get_file_size(file_id: Any) -> Any:
    file_info = files.get(file_id)
    return file_info.fileSize
```

### 2. Handle Optional Values

```python
# Good: Handle None values
def get_file_title(file_id: PIXXIOId) -> str:
    file_info = files.get(file_id)
    title = getattr(file_info, 'title', None)
    return title or 'Untitled'

# Avoid: Assume values exist
def get_file_title(file_id: PIXXIOId) -> str:
    file_info = files.get(file_id)
    return file_info.title  # Could be None
```

### 3. Use Type Guards

```python
from typing import TypeGuard

def is_file_response(data: ResponseData) -> TypeGuard[FileResponse]:
    """Type guard to check if response is file data."""
    return (
        hasattr(data, 'id') and
        hasattr(data, 'fileName') and
        hasattr(data, 'fileSize')
    )

def process_response(data: ResponseData) -> None:
    """Process response with type safety."""
    if is_file_response(data):
        # TypeScript knows data is FileResponse here
        print(f"File: {data.fileName} ({data.fileSize} bytes)")
    else:
        print("Unknown response format")
```

### 4. Gradual Typing

```python
# Start with basic types
def upload_file(path: str) -> Any:
    return files.upload(path)

# Add more specific types gradually  
def upload_file(path: str, **kwargs: Any) -> ResponseData:
    return files.upload(path, **kwargs)

# Eventually use fully typed versions
def upload_file(
    path: str,
    title: Optional[str] = None,
    keywords: Optional[str] = None,
    timeout: int = 300
) -> ResponseData:
    form_data = {}
    if title:
        form_data['title'] = title
    if keywords:
        form_data['keywords'] = keywords
    
    return files.upload_and_wait(path, timeout=timeout, **form_data)
```

---

For more information, see:
- [API Reference](API_REFERENCE.md) - Complete API documentation with types
- [Developer Guide](DEVELOPER_GUIDE.md) - Architecture and development patterns
- [Error Handling](ERROR_HANDLING.md) - Exception types and handling
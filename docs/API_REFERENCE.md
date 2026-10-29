# PIXXIO Client API Reference

This document provides comprehensive API reference documentation for the PIXXIO Python client library.

## Quick Start

```python
from pixxio_client import Client, Authentication
from pixxio_client.files import File
from pixxio_client.collections import Collection

# Create client
client = Client.create_client("your-api-key", "company.pixxio.com")

# Use resources
files = File(client)
collections = Collection(client)

# Basic operations
all_files = files.get()
file_123 = files.get(123)
new_collection = collections.post(json_data={'name': 'My Collection'})
```

## Core Classes

### Authentication

Handles Bearer token authentication for API requests.

```python
auth = Authentication("your-api-key")
client = Client(auth, "company.pixxio.com")
```

**Methods:**
- `authenticate_client(session)` - Adds auth headers to requests session

### Client

Main client for API communication with session management.

```python
# Factory method (recommended)
client = Client.create_client("api-key", "company.pixxio.com")

# Direct instantiation
auth = Authentication("api-key")
client = Client(auth, "company.pixxio.com", version="v1")

# Opt-in retries for GET/PUT/DELETE on 429/503 and connection errors
client = Client.create_client("api-key", "company.pixxio.com", max_retries=3)
```

**Properties:**
- `location_base` - Base API URL
- `session` - Authenticated HTTP session
- `logger` - Logging instance

**Methods:**
- `create_client(api_key, host, max_retries=0, retry_backoff_factor=1.0)` - Factory method for client creation
- `reset()` - Reset session, force re-authentication

`max_retries` is disabled by default. When enabled, `Retry-After` headers are respected, read timeouts are not retried, and POST requests are never retried.

## Base Classes

### ReadOnlyResourceBase

Foundation for read-only API resources.

**Features:**
- GET operations with automatic URL construction
- Response field filtering
- Error handling and response parsing
- Logging integration

**Methods:**
- `get(id=None, **params)` - Get resource(s) by ID or list one page (default `page=1`, `pageSize=50`)
- `iter_all(page_size=100, max_items=None, **params)` - Lazily iterate over all pages of a list endpoint
- `get_all(page_size=100, max_items=None, **params)` - `iter_all()` collected into a list
- `set_response_fields(fields)` - Configure field filtering
- `set_response_field(field)` - Add single field to filter

Object-valued parameters (for example `filter`) are JSON-encoded automatically in GET and DELETE query strings. `iter_all()` reads the list attribute named by the class attribute `_list_response_key` (for example `files`, `customMetadata`) or auto-detects the single list attribute of the response.

### ResourceBase

Extends ReadOnlyResourceBase with full CRUD operations.

**Additional Methods:**
- `post(json_data=None, form_data=None, files=None, **params)` - Create resources
- `put(id, json_data=None, form_data=None, **params)` - Update resources
- `delete(**params)` - Delete resources

### ResourceUploadMixin

Adds file upload capability to resources.

**Methods:**
- `upload(file_path, **form_data)` - Upload file with metadata

### ResourceJobMixin

Provides async job tracking for long-running operations.

**Methods:**
- `post_and_wait(timeout=300, poll_interval=2.0, **params)` - POST with job tracking
- `async_post_and_wait(...)` - Async version using asyncio

## Resource Classes

### File

Complete file management with upload, download, update, delete, and conversion.

```python
from pixxio_client.files import File, FileUpdateBuilder, FileDeleteBuilder

files = File(client)

# Upload operations
result = files.upload("/path/to/file.jpg", title="My Image")
result = files.upload_and_wait("/path/to/video.mp4", timeout=600)

# Download/conversion
converted = files.download(123, format="PDF", size="A4")
resized = files.download(123, format="JPG", width=800, height=600)

# Update multiple files at once using the builder
files.update(
    **FileUpdateBuilder()
        .ids([100, 101, 102])
        .subject("Campaign Assets")
        .keywords_to_add(["campaign", "2024"])
        .build()
)

# Update and wait for the background job (the API starts one only for >1 file)
job = files.update_and_wait(
    ids=[100, 101],
    metadataCustom=[{"action": "replace", "id": 7, "value": "Summer"}],
    timeout=600,
)

# Load all files matching a filter (JSON-encoded automatically)
for file in files.iter_all(page_size=200, filter={"filterType": "rating", "rating": 5}):
    print(file.id, file.metadataFields)

# Delete by IDs or filter
files.delete(
    **FileDeleteBuilder()
        .ids([100, 101])
        .build()
)

# Async operations
result = await files.async_upload_and_wait("/path/to/file.jpg")
```

**Mixins:** ResourceBase, ResourceUploadMixin, ResourceJobMixin

### Builder Classes

All CRUD resources expose typed builder classes for creating and updating records.
Builders provide IDE autocompletion and prevent typos in field names.

```python
from pixxio_client.collections import Collection, CollectionCreateBuilder, CollectionUpdateBuilder
from pixxio_client.users import User, UserCreateBuilder, UserUpdateBuilder
from pixxio_client.uploadlinks import UploadLink, UploadLinkCreateBuilder

# --- Collections ---
collections = Collection(client)

new_col = collections.create(
    **CollectionCreateBuilder()
        .name("Q1 Campaign")
        .description("Assets for the Q1 campaign")
        .build()
)

collections.update(
    new_col.id,
    **CollectionUpdateBuilder()
        .description("Updated description")
        .build()
)

collections.delete(id=new_col.id)

# --- Users ---
users = User(client)

new_user = users.create(
    **UserCreateBuilder()
        .first_name("Jane")
        .last_name("Doe")
        .email("jane.doe@example.com")
        .user_name("jane.doe")
        .password("secure-password")
        .is_active(True)
        .build()
)

users.update(
    new_user.id,
    **UserUpdateBuilder()
        .first_name("Jane-Updated")
        .permission_group_ids_to_add([5])
        .build()
)

# --- Upload Links ---
links = UploadLink(client)

new_link = links.create(
    **UploadLinkCreateBuilder()
        .name("Agency Upload")
        .directory_id(10)
        .validity_period(14)
        .keywords_to_add(["agency", "2024"])
        .build()
)
```

### Convenience Methods

All CRUD resources also provide convenience wrappers that accept keyword
arguments directly — useful for quick calls without a builder:

```python
# list() is an alias for get() with paging defaults
all_collections = collections.list()

# create() wraps post(form_data=...)
new_collection = collections.create(name="My Collection", description="...")

# update() wraps put(id, form_data=...)
collections.update(42, description="New description")

# delete() with a single id
collections.delete(id=42)
```

### Other Resources

All resource classes follow the same pattern. Low-level base methods remain
available for advanced use:

```python
from pixxio_client.collections import Collection
from pixxio_client.users import User
from pixxio_client.keywords import Keyword

collections = Collection(client)
users = User(client)
keywords = Keyword(client)

# Low-level base methods (still fully supported)
items = resource.get()
item = resource.get(123)
new_item = resource.post(json_data={...})
updated = resource.put(123, json_data={...})
result = resource.delete(id=123)
```

## Error Handling

The library includes comprehensive exception handling:

```python
from pixxio_client.exceptions import (
    PIXXIOException,           # Base exception
    BadRequestException,       # 400 errors
    UnauthorizedException,     # 401 errors
    ForbiddenException,        # 403 errors
    NotFoundException,         # 404 errors
    JobTimeoutException,       # Job timeout
    JobFailedException,        # Job failure
)

try:
    result = files.get(123)
except NotFoundException:
    print("File not found")
except UnauthorizedException:
    print("Invalid API key")
except PIXXIOException as e:
    print(f"API error: {e}")
```

## Type System

The library includes comprehensive type hints:

```python
from pixxio_client.pixxio_types import (
    PIXXIOId,           # Resource ID type
    ResponseData,       # API response type  
    JSONDict,           # JSON data type
    QueryParams,        # Query parameters
    ResponseFields,     # Field filtering
    FileHandle,         # File upload type
)
```

## Async Operations

Support for both synchronous and asynchronous job tracking:

```python
import asyncio

# Synchronous job tracking
result = files.post_and_wait(
    json_data={'operation': 'convert'},
    timeout=600,
    poll_interval=5.0
)

# Asynchronous job tracking
async def async_operation():
    result = await files.async_post_and_wait(
        json_data={'operation': 'batch_process'},
        timeout=1800,
        poll_interval=10.0
    )
    return result

result = asyncio.run(async_operation())
```

## Response Field Filtering

Optimize API responses by requesting only needed fields:

```python
files = File(client)

# Configure response filtering
files.set_response_fields(['id', 'fileName', 'subject'])
files.set_response_field('fileSize')

# Requests will only return specified fields
result = files.get()  # Returns limited field set
```

## Logging

Built-in logging support for debugging and monitoring:

```python
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("pixxio_api")

# Use custom logger
client = Client.create_client(
    "api-key", 
    "company.pixxio.com",
    logger=logger
)

# Or set logger on resources
files = File(client, logger=logger)
```

## Best Practices

1. **Use factory method for client creation:**
   ```python
   client = Client.create_client("api-key", "company.pixxio.com")
   ```

2. **Handle exceptions appropriately:**
   ```python
   try:
       result = files.get(file_id)
   except NotFoundException:
       # Handle missing resource
   except PIXXIOException as e:
       # Handle other API errors
   ```

3. **Use job tracking for long operations:**
   ```python
   result = files.upload_and_wait("/large/video.mp4", timeout=1800)
   ```

4. **Filter responses for better performance:**
   ```python
   files.set_response_fields(['id', 'fileName', 'fileSize'])
   ```

5. **Use async operations for concurrent tasks:**
   ```python
   tasks = [files.async_upload_and_wait(path) for path in file_paths]
   results = await asyncio.gather(*tasks)
   ```

## OpenAPI Integration

The library is built from the official PIXXIO OpenAPI specification (`openapi.json`):

- All endpoints and parameters are based on the official API specification
- Type hints are derived from OpenAPI schema definitions
- Response handling matches documented API behavior
- New resources can be implemented using the OpenAPI specification as reference

For the complete API specification and additional endpoint details, refer to:
- **Official API Documentation**: https://api.pixxio.com/docs
- **Local OpenAPI Specification**: `openapi.json` in the project root
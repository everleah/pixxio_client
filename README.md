# PIXXIO Python Client Library

A comprehensive Python client library for the PIXXIO Digital Asset Management (DAM) REST API. This library provides object-oriented access to PIXXIO resources with full async support, type safety, and comprehensive error handling.

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#-license)
[![API Version](https://img.shields.io/badge/PIXXIO%20API-v1-orange.svg)](https://api.pixxio.com/docs)
[![Version](https://img.shields.io/badge/version-0.4.2-orange.svg)](CHANGELOG.md)

## ✨ Features

- **🚀 Full CRUD Operations**: Complete support for Create, Read, Update, Delete operations
- **🧩 27 Resource Classes**: One class per PIXXIO endpoint, from `File` to `VariantStack`
- **📁 File Management**: Upload, download and convert files, with job tracking and progress polling
- **🛠️ Builder Classes**: Fluent builders for create, update, delete and query payloads on every CRUD resource
- **⚡ Async Support**: Built-in async/await support for non-blocking operations
- **🔔 Webhook Parsing**: Schema-agnostic parser for 200+ PIXXIO webhook event types, plus dispatch middleware
- **🔒 Type Safety**: Comprehensive type hints based on the OpenAPI specification
- **🛡️ Error Handling**: Specific exceptions for different HTTP status codes and business logic
- **📊 Job Tracking**: Monitor long-running operations with automatic polling
- **🎯 Response Filtering**: Optimize API calls by requesting only needed fields, with automatic suppression on endpoints that do not support it
- **📄 Pagination**: Transparent paging for list requests, disabled per resource where the endpoint forbids it

## 📦 Installation

The library is distributed through the internal PIXXIO Forgejo package index (there is no public PyPI release). Add that index as an extra index and install:

```bash
pip install pixxio_client --extra-index-url https://git.claudiapps.de/api/packages/Hoerl-IM/pypi/simple/
```

**Development Installation:**
```bash
git clone https://git.claudiapps.de/Hoerl-IM/PixxIO-Client.git
cd PixxIO-Client
python -m pip install -r requirements.txt
```

## 🧪 Tests

A live PIXXIO test environment (`hoerl-demo.px.media`) is used for integration testing. See **[docs/TEST_ENVIRONMENT.md](docs/TEST_ENVIRONMENT.md)** for credentials, ready-to-run scenarios and safety guidelines for the shared environment.

**Running the suite:**
```bash
# Comprehensive integration suite
python tests/integration_tests.py

# Quick functionality test  
python tests/quick_test.py

# Offline unit tests (no live environment required)
python -m unittest tests.response_fields_injection_checks tests.test_webhook_parser_generalized -v
```

```python
# Quick test with live environment
from pixxio_client import Client

# See docs/TEST_ENVIRONMENT.md for actual credentials
client = Client.create_client("your-test-api-key", "hoerl-demo.px.media")
print("✅ Connected to test environment!")
```

**Test inventory:**

| File | Purpose |
|------|---------|
| [`integration_tests.py`](tests/integration_tests.py) | Full integration suite across files, collections, users and jobs |
| [`quick_test.py`](tests/quick_test.py) | Fast connection and basic-operation smoke test |
| [`debug_test.py`](tests/debug_test.py), [`debug_integration.py`](tests/debug_integration.py) | Connectivity troubleshooting with verbose raw responses |
| [`test_auth_error.py`](tests/test_auth_error.py) | Verifies the exception type raised for invalid API keys |
| [`test_upload_params.py`](tests/test_upload_params.py), [`test_upload_with_metadata.py`](tests/test_upload_with_metadata.py) | Upload parameters and metadata handling |
| [`test_get_single_asset.py`](tests/test_get_single_asset.py) | Retrieves a single asset's metadata |
| [`test_metadata_standard_requests.py`](tests/test_metadata_standard_requests.py) | Raw `requests` probe of the standard-metadata endpoint |
| [`response_fields_injection_checks.py`](tests/response_fields_injection_checks.py) | Unit tests for `responseFields` injection and opt-out behavior |
| [`test_webhook_parser_generalized.py`](tests/test_webhook_parser_generalized.py) | Webhook parser tests |

## 🚀 Quick Start

```python
from pixxio_client import Client
from pixxio_client.files import File

# Create authenticated client
client = Client.create_client("your-api-key", "company.pixxio.com")

# Work with files
files = File(client)

# Upload a file
result = files.upload("/path/to/image.jpg", title="My Image")

# Get all files
all_files = files.get()

# Get specific file
file_info = files.get(123)

# Upload with job tracking (for large files)
result = files.upload_and_wait(
    "/path/to/video.mp4",
    timeout=600,
    title="Product Demo"
)
```

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[Documentation Index](docs/README.md)** | Index of all reference, guide, testing and webhook documentation |
| **[API Reference](docs/API_REFERENCE.md)** | Complete API documentation with examples |
| **[Developer Guide](docs/DEVELOPER_GUIDE.md)** | Architecture, patterns, and contribution guidelines |
| **[Test Environment](docs/TEST_ENVIRONMENT.md)** | Live test environment setup and integration tests |
| **[Async Operations](docs/ASYNC_OPERATIONS.md)** | Asynchronous interfaces and job-tracking patterns |
| **[Async Jobs](docs/ASYNC_JOBS.md)** | Deep dive into the async job-tracking implementation |
| **[Error Handling](docs/ERROR_HANDLING.md)** | Exception types and error handling patterns |
| **[Type System](docs/TYPE_SYSTEM.md)** | Type hints and custom types documentation |
| **[Metadata Builders](docs/METADATA_BUILDERS.md)** | Builders for standard and custom metadata payloads |
| **[Webhook Quick Start](docs/webhook/QUICK_START.md)** | Five-minute introduction to webhook parsing |
| **[Webhook Implementation](docs/webhook/PARSER_IMPLEMENTATION.md)** | Webhook parser architecture and usage patterns |
| **[Webhook Examples](docs/webhook/USAGE_EXAMPLES.md)** | Practical webhook handling examples |
| **[Contributing](docs/CONTRIBUTING.md)** | Contribution workflow and code standards |

## 🏷️ Builder Classes

Every CRUD resource ships fluent builders for its payloads, so query parameters and form fields never have to be assembled by hand.

```python
from pixxio_client.collections import Collection, CollectionCreateBuilder, CollectionUpdateBuilder

collections = Collection(client)

# Build the payload, then create/update through the convenience methods
new_collection = collections.create(**CollectionCreateBuilder().name("Marketing Assets").build())
collections.update(new_collection.id, **CollectionUpdateBuilder().description("Campaign assets").build())
```

Resources with payload builders: `Collection`, `DirectLink`, `Directory`, `ExternalShare`, `File`, `License`, `LicenseRelease`, `Model`, `ModelRelease`, `Property`, `PropertyRelease`, `UploadLink`, `User` and `VariantStack`.

### Metadata builders

`StandardMetadataBuilder` and `CustomMetadataBuilder` format metadata values for all field types (text, date, selection, multiselection) and resolve field IDs and selection options from the API.

See [docs/METADATA_BUILDERS.md](docs/METADATA_BUILDERS.md) for full usage examples.

```python
from pixxio_client.metadata import StandardMetadataBuilder, CustomMetadataBuilder

standard_builder = StandardMetadataBuilder(client)
standard_builder.add("Title", "Test Asset Title")
standard_metadata_payload = standard_builder.build()

custom_builder = CustomMetadataBuilder(client)
custom_builder.add("Produktbereich", [98765])
custom_metadata_payload = custom_builder.build()
```

### Convenience methods

CRUD resources also expose `list()`, `create()`, `update()` and `delete()` shortcuts on top of the low-level `get()`, `post()`, `put()` and `delete()` methods.

```python
collections.list()                             # alias for get() with paging defaults
collections.create(name="New Collection")      # wraps post(form_data=...)
collections.update(42, name="Renamed")         # wraps put(id, form_data=...)
collections.delete(42)                         # single id
collections.delete(ids=[1, 2, 3])              # multiple ids
```

## 🏗️ Architecture Overview

The library follows a resource-based architecture with mixin patterns:

```text
ReadOnlyResourceBase            # GET operations
└── ResourceBase                # + POST, PUT, DELETE
    ├── ResourceUploadMixin     # + upload()          → File, Keyword
    └── ResourceJobMixin        # + post_and_wait()   → File
```

`File` combines all three: `class File(ResourceBase, ResourceUploadMixin, ResourceJobMixin)`, while read-only resources (for example `FileState`, `Portal`) stop at `ReadOnlyResourceBase`.

**Core Components:**
- **Client**: Session management, host/base-URL construction and logging
- **Authentication**: Bearer token handling and request headers
- **Resources**: One class per endpoint (File, Collection, User, …)
- **Mixins**: `ResourceUploadMixin` for file uploads, `ResourceJobMixin` for `post_and_wait`
- **Builders**: Payload builders per resource plus the metadata builders
- **Types**: Comprehensive type system based on the OpenAPI spec
- **WebhookParser**: Schema-agnostic parsing of inbound PIXXIO webhook payloads
- **WebhookDispatcher**: Routes parsed events to registered handlers

## 📋 Available Resources

One class per PIXXIO endpoint. `Upload 📁` marks `ResourceUploadMixin` support, `Jobs ⚡` marks job tracking (`ResourceJobMixin` or the `Job` helpers).

### Read/write resources

| Resource | Endpoint | Upload 📁 | Jobs ⚡ | Description |
|----------|----------|-----------|---------|-------------|
| **File** | `/files` | ✅ | ✅ | Asset upload, download, conversion, bulk update and delete |
| **Collection** | `/collections` | ❌ | ❌ | Asset collections and organization |
| **Directory** | `/directories` | ❌ | ❌ | Folder structure, including `get_tree()` |
| **Keyword** | `/keywords` | ✅ | ❌ | Keyword management and CSV export |
| **Synonym** | `/synonyms` | ✅ | ❌ | Synonyms per keyword column (extends `Keyword`) |
| **User** | `/users` | ❌ | ❌ | User management |
| **License** | `/licenses` | ❌ | ❌ | License definitions |
| **LicenseRelease** | `/licenseReleases` | ❌ | ❌ | License releases on assets |
| **Model** | `/models` | ❌ | ❌ | Model definitions |
| **ModelRelease** | `/modelReleases` | ❌ | ❌ | Model releases on assets |
| **Property** | `/properties` | ❌ | ❌ | Property definitions |
| **PropertyRelease** | `/propertyReleases` | ❌ | ❌ | Property releases on assets |
| **VariantStack** | `/variantStacks` | ❌ | ❌ | Variant stacks grouping file versions |
| **UploadLink** | `/uploadLinks` | ❌ | ❌ | Guest upload links |
| **DirectLink** | `/directLinks` | ❌ | ❌ | Direct share links |
| **ExternalShare** | `/externalShares` | ❌ | ❌ | External shares |
| **StandardMetadata** | `/metadata/standard` | ❌ | ❌ | Standard metadata fields |
| **CustomMetadata** | `/metadata/custom` | ❌ | ❌ | Custom metadata fields |

### Read-only resources

| Resource | Endpoint | Description |
|----------|----------|-------------|
| **Job** | `/jobs` | Job status, `wait_for_completion()`, `async_wait_for_completion()`, `abort()` |
| **Portal** | `/portals` | Portal list and details |
| **PortalPage** | `/portals/{id}/pages` | Pages inside a portal |
| **PortalUser** | `/portals/{id}/users` | Current or specific portal user |
| **FileState** | `/fileStates` | File state definitions |
| **DownloadFormat** | `/downloadFormats` | Supported download formats |
| **PermissionGroup** | `/permissionGroups` | Permission groups |
| **ImportantMetadata** | `/metadata/important` | Important metadata fields |
| **InternalMetadata** | `/metadata/internal` | Internal metadata fields |

**Example usage:**
```python
from pixxio_client.collections import Collection
from pixxio_client.users import User
from pixxio_client.variantstacks import VariantStack

collections = Collection(client)
users = User(client)
variant_stacks = VariantStack(client)

# Standard operations work across all resources
my_collections = collections.get()
user_info = users.get(user_id)
```

### Pagination

List requests page automatically for endpoints that support it. Paging is disabled per resource via the `_paged` flag for endpoints that do not: `DownloadFormat`, `FileState`, `LicenseRelease`, `ModelRelease`, `Portal`, `PropertyRelease` (and the `PortalPage` / `PortalUser` sub-endpoints).

## 🔔 Webhooks

`WebhookParser` handles the full range of PIXXIO webhook events through a single schema-agnostic `EventData` class, so new event types work without client changes.

```python
from pixxio_client import WebhookParser

parser = WebhookParser()
events = parser.parse_webhook(webhook_json)

for event in events:
    print(f"{event.event_key} ({event.action}) on {event.resource}")
    print(f"User: {event.user.email}")

    # Event data is available in both snake_case and camelCase
    if hasattr(event.data, "new_text"):
        print(f"Changed to: {event.data.new_text}")
```

**Public exports:** `WebhookParser`, `WebhookEvent`, `EventData`, `EventAction`, `ResourceType`, `EventKey` and the `parse_pixxio_webhook()` convenience function. For HTTP integrations, [`pixxio_client.webhook_middleware`](pixxio_client/webhook_middleware.py) provides `WebhookDispatcher`, `WebhookEventHandler` and `WebhookResponse`.

**Docs & fixtures:** [docs/webhook/](docs/webhook/README.md) (quick start, implementation guide, examples) and [event_json_examples/](event_json_examples) for real payload fixtures.

## 🔄 Async Operations

The library provides both synchronous and asynchronous interfaces:

```python
import asyncio

# Synchronous with job tracking
result = files.upload_and_wait("/large/file.mp4", timeout=600)

# Asynchronous with job tracking
async def batch_upload():
    tasks = [
        files.async_upload_and_wait("/file1.jpg"),
        files.async_upload_and_wait("/file2.jpg"),
        files.async_upload_and_wait("/file3.jpg")
    ]
    return await asyncio.gather(*tasks)

results = asyncio.run(batch_upload())
```

## 🛡️ Error Handling

Comprehensive exception hierarchy for robust error handling:

```python
from pixxio_client.exceptions import (
    PIXXIOException,          # Base exception
    UnauthorizedException,    # 401 - Invalid credentials
    NotFoundException,        # 404 - Resource not found
    JobTimeoutException,      # Job didn't complete in time
    JobFailedException,       # Job execution failed
)

try:
    result = files.get(file_id)
except NotFoundException:
    print("File not found")
except UnauthorizedException:
    print("Check your API key")
except PIXXIOException as e:
    print(f"API error: {e}")
```

## ⚙️ Configuration

**Environment Variables:**
```bash
PIXXIO_API_KEY=your-api-key-here
PIXXIO_HOST=company.pixxio.com
```

**Programmatic Configuration:**
```python
import logging

# Custom logging
logger = logging.getLogger("pixxio_api")
client = Client.create_client("api-key", "host.com", logger=logger)

# Response field filtering
files = File(client)
files.set_response_fields(['id', 'fileName', 'fileSize'])

# Custom timeouts for job tracking
result = files.upload_and_wait(
    "file.mp4",
    timeout=1800,      # 30 minutes
    poll_interval=10   # Check every 10 seconds
)
```

## 📁 Examples

**📁 [examples/](examples/)** - Runnable example collection:

| Script | Purpose |
|--------|---------|
| [`basic_usage.py`](examples/basic_usage.py) | Core functionality, collections and builders |
| [`advanced_async.py`](examples/advanced_async.py) | Concurrent operations and async job tracking |
| [`async_jobs.py`](examples/async_jobs.py) | Job tracking and monitoring |
| [`error_handling.py`](examples/error_handling.py) | Exception handling patterns |
| [`download_collection_assets.py`](examples/download_collection_assets.py) | Download every asset of a collection into an `id;filename` CSV |
| [`build_pixxio_image_mapping_csv.py`](examples/build_pixxio_image_mapping_csv.py) | Build a filename → asset mapping CSV for InDesign workflows |
| [`analyze_indd_links_com.py`](examples/analyze_indd_links_com.py) | Extract linked image filenames from InDesign documents (COM) |
| [`apply_pixxio_labels_to_indd.py`](examples/apply_pixxio_labels_to_indd.py) | Apply PIXXIO labels to InDesign links from a mapping CSV |
| [`upload_changed_indd_files.py`](examples/upload_changed_indd_files.py) | Replace changed InDesign files in PIXXIO via `replaceID` |

The InDesign scripts require Windows with Adobe InDesign installed; see [examples/AGENTS.md](examples/AGENTS.md) for fixture and safety contracts.

**Basic File Operations:**
```python
# Upload with metadata
result = files.upload(
    "/path/to/image.jpg",
    title="Product Photo",
    keywords="product,photography",
    category="marketing"
)

# Download with conversion
pdf_result = files.download(123, format="PDF", size="A4")
thumbnail = files.download(123, format="JPG", width=200, height=200)
```

**Collection Management:**
```python
from pixxio_client.collections import Collection

collections = Collection(client)

# Create new collection
new_collection = collections.post(json_data={
    'name': 'Marketing Assets',
    'description': 'Assets for marketing campaigns'
})

# Update collection
updated = collections.put(collection_id, json_data={
    'name': 'Updated Marketing Assets'
})
```

**Async Batch Operations:**
```python
async def process_files():
    files = File(client)
    
    # Process multiple files concurrently
    file_paths = ["/file1.jpg", "/file2.pdf", "/file3.mp4"]
    
    tasks = [
        files.async_upload_and_wait(
            path, 
            title=f"File {i+1}",
            timeout=900
        ) for i, path in enumerate(file_paths)
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Handle results
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"File {i+1} failed: {result}")
        else:
            print(f"File {i+1} uploaded: {result.id}")

# Run the async function
asyncio.run(process_files())
```

## 🚧 Development

**Setup Development Environment:**
```bash
git clone https://git.claudiapps.de/Hoerl-IM/PixxIO-Client.git
cd PixxIO-Client

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\Activate.ps1

# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Build and Test:**
```bash
# Compile check all modules
python -m compileall -q pixxio_client

# Run the offline unit tests
python -m unittest tests.response_fields_injection_checks tests.test_webhook_parser_generalized -v

# Build a wheel into dist/ (Windows)
build_wheel.bat
```

**Release (maintainers):**
```bash
# Publish dist/*.whl to the Forgejo package index
upload_wheel_to_forgejo_pypi.bat

# Mirror the current branch to the claudiapps remote
git push claudiapps HEAD:main
```

**Type Checking:**
```bash
pip install mypy
mypy pixxio_client/
```

See **[Developer Guide](docs/DEVELOPER_GUIDE.md)** for detailed development instructions.

## 📖 API Documentation

The library is built from the official PIXXIO OpenAPI specification:

- **Official API Docs**: https://api.pixxio.com/docs
- **OpenAPI Spec**: `openapi.json` (included in repository)
- **Interactive Testing**: Use the official API documentation for testing

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Follow** the existing code patterns and type hints
4. **Add** comprehensive docstrings and examples
5. **Test** your changes thoroughly
6. **Commit** with clear messages (`git commit -m 'Add amazing feature'`)
7. **Push** to your branch (`git push origin feature/amazing-feature`)
8. **Open** a Pull Request

See **[Contributing Guidelines](docs/CONTRIBUTING.md)** for detailed information.

## 📋 Requirements

- **Python**: 3.10 or higher (`metadata.py` uses PEP 604 union syntax)
- **Dependencies**:
  - `requests` - HTTP client
  - `python-dateutil` - Date parsing
  - `pytz` - Timezone handling
  - `dateparser` - Flexible date parsing
  - `requests-toolbelt` - File upload utilities
  - `wheel` - Building distribution wheels
  - `pywin32` - Windows-only COM support (InDesign examples)

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

- **Documentation**: See the [API Reference](docs/API_REFERENCE.md) and [Developer Guide](docs/DEVELOPER_GUIDE.md)
- **Issues**: Open an issue in the [repository](https://git.claudiapps.de/Hoerl-IM/PixxIO-Client/issues)
- **PIXXIO Support**: Contact PIXXIO support for API-related questions

## 🔗 Links

- **PIXXIO Platform**: https://www.pixxio.com
- **API Documentation**: https://api.pixxio.com/docs
- **Repository**: https://git.claudiapps.de/Hoerl-IM/PixxIO-Client
- **Package Index**: https://git.claudiapps.de/api/packages/Hoerl-IM/pypi

---

**Made with ❤️ for the PIXXIO community**
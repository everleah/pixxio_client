# PIXXIO Python Client Library

A comprehensive Python client library for the PIXXIO Digital Asset Management (DAM) REST API. This library provides object-oriented access to PIXXIO resources with full async support, type safety, and comprehensive error handling.

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![API Version](https://img.shields.io/badge/PIXXIO%20API-v1-orange.svg)](https://api.pixxio.com/docs)

## ✨ Features

- **🚀 Full CRUD Operations**: Complete support for Create, Read, Update, Delete operations
- **📁 File Management**: Upload, download, convert files with progress tracking
- **⚡ Async Support**: Built-in async/await support for non-blocking operations
- **🔒 Type Safety**: Comprehensive type hints based on OpenAPI specification
- **🛡️ Error Handling**: Specific exceptions for different HTTP status codes and business logic
- **📊 Job Tracking**: Monitor long-running operations with automatic polling
- **🎯 Response Filtering**: Optimize API calls by requesting only needed fields
- **📝 Comprehensive Docs**: Full API reference and examples

## 📦 Installation

```bash
pip install pixxio-client
```

**Development Installation:**
```bash
git clone https://github.com/your-org/pixxio-client.git
cd pixxio-client
python -m pip install -r requirements.txt
```

## 🧪 Testing Environment

A live test environment is available for testing and development:

**📋 [TEST_ENVIRONMENT.md](TEST_ENVIRONMENT.md)** - Complete testing setup guide with:
- Live demo environment credentials
- Ready-to-run integration tests  
- Example test scenarios
- Safety guidelines for shared testing

```python
# Quick test with live environment
from pixxio_client import Client

# See TEST_ENVIRONMENT.md for actual credentials
client = Client.create_client("your-test-api-key", "test-host.pixxio.com")
print("✅ Connected to test environment!")
```

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
| **[API Reference](API_REFERENCE.md)** | Complete API documentation with examples |
| **[Developer Guide](docs/DEVELOPER_GUIDE.md)** | Architecture, patterns, and contribution guidelines |
| **[Test Environment](TEST_ENVIRONMENT.md)** | Live test environment setup and integration tests |
| **[Async Operations](docs/ASYNC_OPERATIONS.md)** | Job tracking and async operation examples |
| **[Error Handling](docs/ERROR_HANDLING.md)** | Exception types and error handling patterns |
| **[Type System](docs/TYPE_SYSTEM.md)** | Type hints and custom types documentation |

## 🏗️ Architecture Overview

The library follows a resource-based architecture with mixin patterns:

```python
# Base hierarchy
ReadOnlyResourceBase          # GET operations
└── ResourceBase              # + POST, PUT, DELETE
    ├── ResourceUploadMixin   # + file upload capability
    └── ResourceJobMixin      # + async job tracking
```

**Core Components:**
- **Client**: Session management and authentication
- **Authentication**: Bearer token handling
- **Resources**: API endpoint classes (File, Collection, User, etc.)
- **Mixins**: Reusable functionality for uploads and job tracking
- **Types**: Comprehensive type system based on OpenAPI spec

## 📋 Available Resources

All resources support standard CRUD operations. Special capabilities marked with icons:

| Resource | Endpoints | Upload 📁 | Jobs ⚡ | Description |
|----------|-----------|-----------|---------|-------------|
| **File** | `/files` | ✅ | ✅ | File upload, download, conversion |
| **Collection** | `/collections` | ❌ | ❌ | Asset collections and organization |
| **User** | `/users` | ❌ | ❌ | User management |
| **Directory** | `/directories` | ❌ | ❌ | Folder structure |
| **Job** | `/jobs` | ❌ | ✅ | Job status tracking |
| **Keyword** | `/keywords` | ❌ | ❌ | Keyword management |
| **License** | `/licenses` | ❌ | ❌ | License information |

**Example usage:**
```python
from pixxio_client.collections import Collection
from pixxio_client.users import User

collections = Collection(client)
users = User(client)

# Standard operations work across all resources
my_collections = collections.get()
user_info = users.get(user_id)
```

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

## 🧪 Examples

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
git clone https://github.com/your-org/pixxio-client.git
cd pixxio-client

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
python -m py_compile pixxio_client/*.py

# Build wheel
./build_wheel.bat  # Windows
```

**Type Checking:**
```bash
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

- **Python**: 3.8 or higher
- **Dependencies**: 
  - `requests` - HTTP client
  - `python-dateutil` - Date parsing
  - `pytz` - Timezone handling
  - `dateparser` - Flexible date parsing
  - `requests-toolbelt` - File upload utilities

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the [API Reference](API_REFERENCE.md) and [Developer Guide](docs/DEVELOPER_GUIDE.md)
- **Issues**: Use GitHub Issues for bug reports and feature requests
- **PIXXIO Support**: Contact PIXXIO support for API-related questions
- **Community**: Join discussions in GitHub Discussions

## 🔗 Links

- **PIXXIO Platform**: https://www.pixxio.com
- **API Documentation**: https://api.pixxio.com/docs
- **Python Package**: https://pypi.org/project/pixxio-client/
- **Repository**: https://github.com/your-org/pixxio-client

---

**Made with ❤️ for the PIXXIO community**
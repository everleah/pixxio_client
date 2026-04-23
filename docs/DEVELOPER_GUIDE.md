# Developer Guide

This guide provides detailed information for developers working on or contributing to the PIXXIO Python client library.

## Table of Contents

- [Project Architecture](#project-architecture)
- [Development Setup](#development-setup)
- [Code Organization](#code-organization)
- [Design Patterns](#design-patterns)
- [Adding New Resources](#adding-new-resources)
- [Testing Strategy](#testing-strategy)
- [Contributing Guidelines](#contributing-guidelines)

## Project Architecture

### Overall Design Philosophy

The PIXXIO client follows a **resource-based architecture** where each API endpoint is represented by a Python class. This design provides:

- **Intuitive API**: Each resource (files, collections, users) has its own class
- **Consistent Interface**: All resources follow the same CRUD patterns
- **Extensibility**: New resources can be added following established patterns
- **Type Safety**: Full type hints based on OpenAPI specification
- **Async Support**: Built-in async operations with job tracking

### Core Components

```
pixxio_client/
├── __init__.py           # Client and Authentication classes
├── _base.py              # Base classes and mixins
├── pixxio_types.py       # Type definitions
├── exceptions.py         # Exception hierarchy
├── files.py              # File resource (example implementation)
├── collections.py        # Collection resource
├── users.py              # User resource
├── jobs.py               # Job tracking resource
└── ...                   # Other resource modules
```

### Class Hierarchy

```python
# Base Classes
ReadOnlyResourceBase
├── Provides: GET operations, response parsing, field filtering
├── Used for: Read-only resources

ResourceBase (extends ReadOnlyResourceBase)
├── Adds: POST, PUT, DELETE operations
├── Used for: Full CRUD resources

# Mixins (composition pattern)
ResourceUploadMixin
├── Adds: file upload capability via upload() method
├── Requires: ResourceBase (for post() method)

ResourceJobMixin
├── Adds: async job tracking with post_and_wait()
├── Requires: ResourceBase (for post() method)
├── Provides: Both sync and async job monitoring
```

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment tool (venv, conda, etc.)

### Initial Setup

```bash
# Clone repository
git clone https://github.com/your-org/pixxio-client.git
cd pixxio-client

# Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\Activate.ps1

# Linux/Mac  
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "from pixxio_client import Client; print('Success!')"
```

### Development Tools

**Type Checking:**
```bash
# Install mypy
pip install mypy

# Run type checking
mypy pixxio_client/
```

**Code Compilation Check:**
```bash
# Check individual modules
python -m py_compile pixxio_client/files.py

# Check all modules
python -m py_compile pixxio_client/*.py
```

**Build Distribution:**
```bash
# Windows
./build_wheel.bat

# Manual build
python setup.py bdist_wheel
```

## Code Organization

### File Structure Patterns

Each resource follows a consistent structure:

```python
# Example: pixxio_client/files.py
from typing import Optional, Any
from ._base import ResourceBase, ResourceUploadMixin, ResourceJobMixin
from .pixxio_types import PIXXIOId, ResponseData

class File(ResourceBase, ResourceUploadMixin, ResourceJobMixin):
    """Resource class for file operations."""
    
    NAME = "files"  # Must match API endpoint
    
    # Override methods only when API differs from standard REST
    def custom_method(self, **params):
        return self._get(endpoint_base=f"{self.endpoint_base}/special", **params)
```

### Mixin Usage Guidelines

**ResourceUploadMixin:**
- Use when resource supports file uploads
- Provides `upload(file_path, **form_data)` method
- Requires class to have `post()` method (from ResourceBase)

**ResourceJobMixin:**
- Use when resource operations may return job IDs
- Provides `post_and_wait()` and `async_post_and_wait()` methods
- Requires access to Job resource for status tracking

**Example Combinations:**
```python
# Read-only resource
class User(ReadOnlyResourceBase):
    NAME = "users"

# Full CRUD resource
class Collection(ResourceBase):
    NAME = "collections"

# File resource with uploads and job tracking
class File(ResourceBase, ResourceUploadMixin, ResourceJobMixin):
    NAME = "files"
```

## Design Patterns

### 1. Resource Pattern

Each API endpoint is represented by a class:

```python
class ResourceName(ResourceBase):
    NAME = "api_endpoint"  # Must match actual endpoint
    
    # Inherit standard CRUD operations:
    # get(), post(), put(), delete()
    
    # Add custom methods when needed
    def custom_operation(self, **params):
        return self._get(endpoint_base=f"{self.endpoint_base}/custom", **params)
```

### 2. Mixin Pattern

Functionality is added through mixins rather than inheritance:

```python
# Instead of complex inheritance hierarchies:
class File(FileUploadResource, JobTrackingResource, CRUDResource):
    pass

# Use composition with mixins:
class File(ResourceBase, ResourceUploadMixin, ResourceJobMixin):
    pass
```

### 3. Factory Pattern

Client creation uses factory method:

```python
# Recommended approach
client = Client.create_client("api-key", "host.com")

# Instead of manual construction
auth = Authentication("api-key")
client = Client(auth, "host.com")
```

### 4. Response Object Pattern

API responses are converted to objects with dot notation access:

```python
# Raw JSON: {"id": 123, "user": {"name": "John"}}
# Becomes: response.id, response.user.name
# Missing attributes return None instead of raising AttributeError
```

## Adding New Resources

### Step 1: Check OpenAPI Specification

```bash
# Review available endpoints in openapi.json
# Look for endpoints not yet implemented
grep -r "\"/{endpoint}\"" openapi.json
```

### Step 2: Create Resource Module

```python
# pixxio_client/newresource.py
from typing import Optional, Any
from ._base import ResourceBase  # Add mixins as needed
from .pixxio_types import PIXXIOId, ResponseData

class NewResource(ResourceBase):
    """
    Resource for managing [description].
    
    Provides [list of capabilities].
    
    Example:
        ```python
        client = Client.create_client("api-key", "host.com")
        resource = NewResource(client)
        
        # Basic operations
        all_items = resource.get()
        item = resource.get(123)
        ```
    """
    
    NAME = "newresources"  # Must match API endpoint
    
    # Override methods only when API differs from REST standard
    def special_operation(self, id: PIXXIOId, **params: Any) -> ResponseData:
        """
        Custom operation description.
        
        Args:
            id: Resource ID
            **params: Additional parameters
            
        Returns:
            ResponseData: Operation result
        """
        return self._post(
            endpoint_base=f"{self.endpoint_base}/{id}/special",
            **params
        )
```

### Step 3: Add Type Definitions (if needed)

```python
# pixxio_client/pixxio_types.py

# Add new types based on OpenAPI schema
NewResourceData = Union[SimpleNamespace, Dict[str, Any]]
NewResourceId = Union[int, str]
```

### Step 4: Update Imports

```python
# pixxio_client/__init__.py
from .newresource import NewResource

__all__ = [
    'Client',
    'Authentication', 
    'NewResource',  # Add to exports
    # ... other exports
]
```

### Step 5: Add Documentation

Follow the established documentation patterns:
- Comprehensive class docstring with examples
- Method docstrings with Args, Returns, Raises sections
- Real-world usage examples
- Parameter descriptions with types

## Testing Strategy

### Manual Testing

```python
# Create test script
from pixxio_client import Client
from pixxio_client.newresource import NewResource

# Test basic functionality
client = Client.create_client("test-api-key", "test.pixxio.com")
resource = NewResource(client)

try:
    # Test read operations
    items = resource.get()
    print(f"Found {len(items)} items")
    
    # Test create operations (if applicable)
    new_item = resource.post(json_data={'name': 'Test Item'})
    print(f"Created item with ID: {new_item.id}")
    
except Exception as e:
    print(f"Error: {e}")
```

### Type Checking

```bash
# Verify type hints
mypy pixxio_client/newresource.py

# Check entire codebase
mypy pixxio_client/
```

### Integration Testing

```python
# Test with actual API (use test environment)
def test_integration():
    client = Client.create_client(
        "real-api-key", 
        "test-environment.pixxio.com"
    )
    
    resource = NewResource(client)
    
    # Test full CRUD cycle
    # 1. Create
    created = resource.post(json_data={'name': 'Test'})
    assert created.id is not None
    
    # 2. Read
    retrieved = resource.get(created.id)
    assert retrieved.name == 'Test'
    
    # 3. Update
    updated = resource.put(created.id, json_data={'name': 'Updated'})
    assert updated.name == 'Updated'
    
    # 4. Delete
    result = resource.delete(id=created.id)
    assert result.success is True
```

## Contributing Guidelines

### Code Style

1. **Follow existing patterns**: Look at files.py, collections.py for examples
2. **Use type hints**: All public methods must have complete type annotations
3. **Write docstrings**: Follow Google/Sphinx style with examples
4. **Handle errors**: Use appropriate exceptions from exceptions.py
5. **Add examples**: Include practical usage examples in docstrings

### Documentation Requirements

1. **Class docstrings**: Must include purpose, capabilities, and examples
2. **Method docstrings**: Args, Returns, Raises sections with types
3. **Inline comments**: Explain complex logic or API-specific behavior
4. **Usage examples**: Real-world scenarios in docstrings

### Pull Request Process

1. **Branch naming**: `feature/resource-name` or `fix/issue-description`
2. **Commit messages**: Clear, descriptive messages
3. **Type checking**: Ensure `mypy pixxio_client/` passes
4. **Documentation**: Update relevant docs and examples
5. **Testing**: Include manual testing evidence

### Example Pull Request Checklist

- [ ] New resource follows established patterns
- [ ] Type hints added for all public methods
- [ ] Comprehensive docstrings with examples
- [ ] Updated __init__.py imports if needed  
- [ ] Manual testing completed
- [ ] mypy type checking passes
- [ ] Documentation updated (docs/API_REFERENCE.md if needed)

## Architecture Decisions

### Why Mixins Instead of Inheritance?

**Problem**: Different resources need different combinations of capabilities:
- Some need uploads (File)
- Some need job tracking (File, some Collections operations)
- Some are read-only (User, in some contexts)

**Solution**: Composition through mixins allows flexible capability combination:

```python
# Flexible combinations
class File(ResourceBase, ResourceUploadMixin, ResourceJobMixin):
    pass

class Collection(ResourceBase):  # No upload or jobs needed
    pass

class User(ReadOnlyResourceBase):  # Read-only
    pass
```

### Why Factory Methods?

**Problem**: Client setup involves multiple steps and configuration.

**Solution**: Factory method provides simple, one-line client creation:

```python
# Simple
client = Client.create_client("api-key", "host.com")

# vs Complex
auth = Authentication("api-key")
client = Client(auth, "host.com", version="v1")
```

### Why Custom Response Objects?

**Problem**: API responses vary in structure, missing fields cause AttributeError.

**Solution**: Custom `_ResponseObject` returns None for missing attributes:

```python
# Graceful handling
response = api_call()
name = response.name  # Returns None if missing
email = response.user.email  # Returns None if user or email missing
```

## OpenAPI Integration

The library is built from the official PIXXIO OpenAPI specification (`openapi.json`):

### Using OpenAPI for Development

1. **Endpoint Discovery**:
   ```bash
   # Find available endpoints
   jq '.paths | keys[]' openapi.json
   ```

2. **Parameter Reference**:
   ```bash
   # Check parameters for specific endpoint
   jq '.paths."/files".get.parameters' openapi.json
   ```

3. **Response Schema**:
   ```bash
   # Check response structure
   jq '.paths."/files".get.responses."200".content' openapi.json
   ```

### Validation Against OpenAPI

When implementing new resources:

1. Check endpoint exists in OpenAPI spec
2. Verify parameter names and types
3. Confirm response structure
4. Validate HTTP methods supported
5. Check for special endpoint behaviors (like /files/convert)

This ensures the Python client stays synchronized with the official API specification.

## Response Fields Behavior on Specialized GET Endpoints

The client automatically appends `responseFields` for standard list and single-item
GET endpoints. Some specialized PIXXIO endpoints reject `responseFields` and must
be called without that query parameter.

The base resource class provides a shared opt-out mechanism that specialized
methods use internally. This keeps default behavior unchanged for standard CRUD
GET requests while preventing 400 errors on unsupported endpoints.

Currently protected specialized GET methods:

- `File.download()` (`/files/convert` and `/files/{id}/convert`)
- `Directory.get_tree()` (`/directories/tree`)
- `Keyword.download()` (`/keywords/csv`)
- `Synonym.get_columns()` (`/synonymColumns`)
- `PortalPage.get()` (`/portals/{id}/pages`)
- `PortalUser.get()` (`/portals/{id}/users/current`, `/portals/{id}/users/{user_id}`)

---

For more specific information, see:
- [API Reference](API_REFERENCE.md) - Complete API documentation
- [Async Operations](ASYNC_OPERATIONS.md) - Job tracking details
- [Error Handling](ERROR_HANDLING.md) - Exception handling patterns
- [Type System](TYPE_SYSTEM.md) - Type definitions and usage
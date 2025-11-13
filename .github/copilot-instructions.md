# PIXXIO API Python Client - Copilot Instructions

## Project Overview
This is a **Python client library** for the PIXX!O digital asset management (DAM) REST API. The project provides **object-oriented access** to the PIXXIO system for other software projects. The library follows a resource-based architecture where each API endpoint is represented by a dedicated class inheriting from base classes.

**⚠️ Project Status: Early Development**
- Library is incomplete and not fully tested
- Some resources may be missing implementations
- Use `openapi.json` for API reference and validation

## Architecture Patterns

### Base Class Hierarchy
- **`ReadOnlyResourceBase`** (`_base.py`): Provides GET operations and response parsing
- **`ResourceBase`** (extends ReadOnlyResourceBase): Adds POST, PUT, DELETE operations  
- **`ResourceUploadMixin`**: Adds file upload capability via `upload()` method

### Resource Implementation Pattern
All API resources follow this consistent pattern:
```python
from ._base import ResourceBase, ResourceUploadMixin

class ResourceName(ResourceBase, ResourceUploadMixin):  # Mixins as needed
    NAME = "api_endpoint_name"  # Must match API endpoint
    
    # Override methods only when API differs from standard REST
    def custom_method(self, **params):
        return self._get(endpoint_base=f"{self.endpoint_base}/special", **params)
```

Examples:
- `File` class uses both mixins for upload and standard CRUD operations
- `Keyword` class overrides `post()` to use `/csv` endpoint instead of standard endpoint
- Simple resources like `User` and `Collection` use base class methods unchanged

### Client Architecture
- **`Client`** class manages session, authentication, and base URL construction
- **`Authentication`** class handles Bearer token authentication 
- URL format: `{host}/api/{version}/{resource_name}`
- All requests go through `client.session` (requests.Session with auth headers)

### Response Handling
- **`Objectifier`** converts JSON responses to `SimpleNamespace` objects for dot notation access
- **`_ResponseObject`** returns `None` for missing attributes instead of raising `AttributeError`
- Custom exception hierarchy in `exceptions.py` for API error handling
- 204 No Content responses return `SimpleNamespace(success=True)`

## Key Conventions

### Resource Naming
- Class names use singular form (e.g., `File`, `User`, `Keyword`)
- `NAME` attribute defines the API endpoint path (often plural, e.g., "files", "users")
- File names match class names in lowercase (e.g., `files.py` for `File` class)

### Method Overrides
When API endpoints deviate from standard REST:
- Override specific HTTP methods (`post()`, `put()`, etc.) 
- Use `self._method()` for custom endpoint construction
- Common pattern: `f"{self.endpoint_base}/{custom_path}"`

### Response Fields
- Use `response_fields` parameter to limit API response data
- Set via `set_response_fields()` or `set_response_field()` methods
- Automatically added to GET request parameters when configured

## Development Workflow

### Building
```bash
# Activate virtual environment and build wheel
build_wheel.bat
```

### Dependencies
- Core: `requests`, `python-dateutil`, `pytz`, `dateparser`
- File uploads: `requests-toolbelt`
- No test framework currently configured

### Package Structure
- All resources in `pixxio_client/` package
- `__init__.py` contains `Client` and `Authentication` classes
- Each API resource gets its own module file
- `_base.py` contains shared base classes and utilities

## Common Patterns for New Resources

1. **Standard CRUD Resource**:
```python
from ._base import ResourceBase
class NewResource(ResourceBase):
    NAME = "newresources"
```

2. **Resource with File Upload**:
```python
from ._base import ResourceBase, ResourceUploadMixin
class UploadableResource(ResourceBase, ResourceUploadMixin):
    NAME = "uploadableresources"
```

3. **Resource with Custom Endpoints**:
```python
from ._base import ResourceBase
class CustomResource(ResourceBase):
    NAME = "customresources"
    
    def special_action(self, id, **params):
        return self._post(
            endpoint_base=f"{self.endpoint_base}/{id}/action",
            **params)
```

## OpenAPI Integration
The project includes `openapi.json` - the complete PIXXIO REST API specification:
- Use for understanding available endpoints and parameters  
- Validate implementations against API contracts
- Reference for implementing missing resources
- 50+ endpoints covering files, collections, metadata, users, jobs, etc.

## API Documentation References
- **Official API Docs**: https://api.pixxio.com/docs - Complete interactive documentation
- **Local OpenAPI**: `openapi.json` - Machine-readable API specification
- Use official docs for understanding concepts, examples, and best practices
- Use OpenAPI JSON for precise implementation details and validation

## Missing Implementation Guidance
Compare existing Python modules against OpenAPI endpoints to identify gaps:
```bash
# Available endpoints include:
/api/v1/{files,collections,users,directories,jobs,metadata,licenses,portals}
# And specialized endpoints like:
/api/v1/keywords/csv, /api/v1/files/convert, /api/v1/directories/tree
```

When implementing new resources:
1. Check `openapi.json` for endpoint details, parameters, and response schemas
2. Follow existing patterns from `files.py`, `keywords.py`, etc.
3. Override HTTP methods only when API differs from standard REST

## API-Specific Patterns
- **Asynchronous operations**: Many endpoints return `jobID` for long-running tasks
- **Response field filtering**: Use `responseFields` parameter to limit response data
- **Complex filtering**: API supports sophisticated filter objects for searches
- **File operations**: Upload, convert, and download with various format options

## Webhook Support (Production Ready ✅)

**Status: Now Available** - Generalized webhook parser for all PIXXIO event types

**PIXXIO Webhook Parser:**
- **File**: `pixxio_client/webhook_parser.py`
- **Architecture**: Generalized, schema-agnostic design (no hardcoded event classes)
- **Event Coverage**: 200+ known event types + automatic support for future types
- **Documentation**: Complete guides in `docs/webhook/` folder

**Core Components:**
- `WebhookParser`: Main parser class for processing JSON payloads
- `WebhookEvent`: Parsed event with consistent structure
- `EventData`: Flexible container for any event type's data
- `EventKey` enum: Known event types (auto-extensible)
- Helper methods: `is_file_event()`, `is_metadata_event()`, etc.

**Key Features:**
- Automatic camelCase → snake_case field conversion
- Both field name formats always available
- Type-safe dot notation access: `event.data.field_name`
- Fallback to raw dict: `event.data.raw` or `event.data._raw_data`
- 11 comprehensive unit tests (all passing)
- 13 practical usage examples with real payloads

**Helper Methods Available:**
- `is_file_event()`: Check for file-related events
- `is_metadata_event()`: Check for metadata field changes
- `is_language_event()`: Check for language code changes
- `is_state_event()`: Check for file state changes
- `is_file_property_event()`: Check for file property changes (name, dates)
- `is_keywords_event()`: Check for keyword modifications

**Known Event Types (Validated with Real Payloads):**
- File metadata: text changes, multi-selections, truncate
- File properties: name, create date, modify date
- Keywords: added/deleted
- Language codes: added/removed
- File state changes
- Collection/user/portal events
- And 190+ more...

**Documentation:**
- `docs/webhook/QUICK_START.md` - 5-minute getting started
- `docs/webhook/PARSER_IMPLEMENTATION.md` - Complete reference
- `docs/webhook/USAGE_EXAMPLES.md` - 13 practical examples
- `docs/webhook/README.md` - Navigation hub

**Testing:**
- `tests/test_webhook_parser_generalized.py` - 11 unit tests
- `test_webhook_payloads.py` - Batch 1: 4 real PIXXIO payloads
- `test_webhook_payloads_batch2.py` - Batch 2: 4 additional real payloads
- `test_webhook_payloads_batch3.py` - Batch 3: 3 keyword event payloads
- All tests passing, no regressions

## Important Notes
- **Setup bug**: `setup.py` has `find_packages(include=["celum_client*"])` - should be `["pixxio_client*"]`
- **No auth validation**: Invalid API keys cause runtime errors, not startup validation
- **File uploads**: Use `files={"file": file_handle}` format with `ResourceUploadMixin`
- **API documentation**: All exceptions inherit from custom classes in `exceptions.py`
- **Webhook field names**: Use snake_case in Python code (camelCase also available)
- **Type checker hints**: Use `# type: ignore[attr-defined]` for dynamic EventData attributes
- **Setup bug**: `setup.py` has `find_packages(include=["celum_client*"])` - should be `["pixxio_client*"]`
- **No auth validation**: Invalid API keys cause runtime errors, not startup validation
- **File uploads**: Use `files={"file": file_handle}` format with `ResourceUploadMixin`
- **API documentation**: All exceptions inherit from custom classes in `exceptions.py`
- **Webhook field names**: Use snake_case in Python code (camelCase also available)
- **Type checker hints**: Use `# type: ignore[attr-defined]` for dynamic EventData attributes
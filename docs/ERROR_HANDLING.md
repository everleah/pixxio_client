# Error Handling Guide

This guide covers the comprehensive error handling system in the PIXXIO Python client library, including specific exception types, recovery patterns, and best practices.

## Exception Hierarchy

The library provides a structured exception hierarchy for different types of errors:

```
PIXXIOException (Base)
├── HTTPException
│   ├── ClientError (4xx HTTP status codes)
│   │   ├── BadRequestException (400)
│   │   ├── UnauthorizedException (401)
│   │   ├── ForbiddenException (403)
│   │   ├── NotFoundException (404)
│   │   ├── MethodNotAllowedException (405)
│   │   ├── ConflictException (409)
│   │   ├── UnprocessableEntityException (422)
│   │   └── TooManyRequestsException (429)
│   └── ServerError (5xx HTTP status codes)
│       ├── InternalServerErrorException (500)
│       ├── BadGatewayException (502)
│       ├── ServiceUnavailableException (503)
│       └── GatewayTimeoutException (504)
├── FileUploadException
│   ├── FileTooLargeException
│   └── UnsupportedFileTypeException
├── JobException
│   ├── JobTimeoutException
│   ├── JobFailedException
│   └── JobAbortedException
├── APIQuotaExceededException
├── ConnectionException
│   └── TimeoutException
├── FileDownloadException
├── FileConversionException
└── Legacy Exceptions (backwards compatibility)
    ├── ResponseExceptionBase
    ├── ResponseException
    ├── InvalidResponseException
    └── ResponseError
```

## Basic Error Handling

### Import Exceptions

```python
from pixxio_client.exceptions import (
    PIXXIOException,          # Base exception
    UnauthorizedException,    # 401 errors
    NotFoundException,        # 404 errors
    JobTimeoutException,      # Job timeout
    JobFailedException,       # Job failure
    FileUploadException,      # Upload errors
    FileTooLargeException,    # File size errors
    UnsupportedFileTypeException,  # File type errors
)
```

### Simple Error Handling

```python
from pixxio_client import Client
from pixxio_client.files import File
from pixxio_client.exceptions import PIXXIOException, NotFoundException

client = Client.create_client("api-key", "company.pixxio.com")
files = File(client)

try:
    file_info = files.get(123)
    print(f"File: {file_info.fileName}")
    
except NotFoundException:
    print("File not found")
    
except PIXXIOException as e:
    print(f"API error: {e}")
```

## HTTP Status Code Exceptions

### Client Errors (4xx)

#### Authentication Errors (401)

```python
from pixxio_client.exceptions import UnauthorizedException

try:
    client = Client.create_client("invalid-key", "company.pixxio.com")
    files = File(client)
    result = files.get()
    
except UnauthorizedException as e:
    print(f"Authentication failed: {e}")
    print("Invalid API key - check your credentials")
    # Handle: prompt for new key, refresh token, etc.
```

#### Permission Errors (403)

```python
from pixxio_client.exceptions import ForbiddenException

try:
    result = files.delete(file_id=123)
    
except ForbiddenException as e:
    print(f"Insufficient permissions: {e}")
    print("Insufficient permissions to delete this file")
    # Handle: check user permissions, request access, etc.
```

#### Resource Not Found (404)

```python
from pixxio_client.exceptions import NotFoundException

try:
    file_info = files.get(999999)
    
except NotFoundException as e:
    print(f"Resource not found: {e}")
    print("File does not exist")
    # Handle: validate ID, show error message, etc.
```

#### Validation Errors (400, 422)

```python
from pixxio_client.exceptions import (
    BadRequestException, 
    UnprocessableEntityException
)

try:
    # Invalid request format
    result = files.post(json_data={'invalid': 'data'})
    
except BadRequestException as e:
    print(f"Invalid request: {e}")
    print(f"Status: {e.status_code}")
    # Handle: validate input, show field errors, etc.
    
except UnprocessableEntityException as e:
    print(f"Validation failed: {e}")
    # Handle: show specific validation errors, correct input, etc.
```

#### Rate Limiting (429)

```python
from pixxio_client.exceptions import TooManyRequestsException
import time

def upload_with_rate_limiting(file_path):
    max_retries = 3
    retry_delay = 60  # Start with 1 minute
    
    for attempt in range(max_retries):
        try:
            return files.upload(file_path)
            
        except TooManyRequestsException as e:
            print(f"Rate limited: {e}")
            if e.retry_after:
                print(f"Retry after {e.retry_after} seconds")
                time.sleep(e.retry_after)
                continue
                
            if attempt == max_retries - 1:
                raise  # Final attempt failed
                
            print(f"Rate limited, waiting {retry_delay} seconds...")
            time.sleep(retry_delay)
            retry_delay *= 2  # Exponential backoff
    
# Usage
try:
    result = upload_with_rate_limiting("/path/to/file.jpg")
except TooManyRequestsException:
    print("Rate limit exceeded after retries")
```

### Server Errors (5xx)

```python
from pixxio_client.exceptions import (
    InternalServerErrorException,
    BadGatewayException,
    ServiceUnavailableException,
    GatewayTimeoutException
)

def robust_api_call(operation_func, max_retries=3):
    """Wrapper for API calls with server error retry logic."""
    
    for attempt in range(max_retries):
        try:
            return operation_func()
            
        except InternalServerErrorException as e:
            print(f"Server error: {e}")
            if attempt == max_retries - 1:
                raise
            # Retry after delay or contact support
                
        except ServiceUnavailableException as e:
            print(f"Service unavailable: {e}")
            if e.retry_after:
                time.sleep(e.retry_after)
            elif attempt == max_retries - 1:
                raise
            else:
                wait_time = (attempt + 1) * 30  # 30, 60, 90 seconds
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            
        except (BadGatewayException, GatewayTimeoutException) as e:
            if attempt == max_retries - 1:
                raise  # Final attempt failed
                
            wait_time = (attempt + 1) * 30  # 30, 60, 90 seconds
            print(f"Gateway error ({e}), retrying in {wait_time} seconds...")
            time.sleep(wait_time)

# Usage
try:
    result = robust_api_call(lambda: files.get())
except (InternalServerErrorException, ServiceUnavailableException):
    print("Server is currently unavailable")
```

## File Operation Exceptions

## ResponseFields Parameter Mismatches

Some PIXXIO specialized endpoints do not support the `responseFields` query
parameter even though they return structured data.

To avoid 400 Bad Request failures, the client now automatically bypasses
`responseFields` on these methods:

- `Directory.get_tree()`
- `Keyword.download()`
- `Synonym.get_columns()`
- `File.download()` convert paths
- `PortalPage.get()`
- `PortalUser.get()`

If you set resource-level response fields via `set_response_fields(...)`,
the setting is still honored on standard GET endpoints and safely ignored on
the specialized endpoints listed above.

### Upload Error Handling

```python
from pixxio_client.exceptions import (
    FileUploadException, 
    FileTooLargeException, 
    UnsupportedFileTypeException
)
import os

def safe_file_upload(file_path, **metadata):
    try:
        # Validate file before upload
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        file_size = os.path.getsize(file_path)
        if file_size > 100 * 1024 * 1024:  # 100MB
            print(f"Large file detected ({file_size / 1024 / 1024:.1f}MB)")
            
        return files.upload_and_wait(file_path, timeout=1800, **metadata)
        
    except FileNotFoundError:
        print("Source file not found")
        return None
        
    except FileTooLargeException as e:
        print(f"File too large: {e}")
        print(f"File size: {e.file_size} bytes")
        print(f"Max allowed: {e.max_size} bytes")
        # Compress or split file
        return None
        
    except UnsupportedFileTypeException as e:
        print(f"Unsupported file type: {e.file_type}")
        if e.supported_types:
            print(f"Supported: {', '.join(e.supported_types)}")
        # Convert to supported format
        return None
        
    except FileUploadException as e:
        print(f"Upload failed: {e}")
        print(f"File: {e.file_path}")
        
        # Handle specific upload errors
        if "file too large" in str(e).lower():
            print("File exceeds maximum size limit")
        elif "invalid format" in str(e).lower():
            print("File format not supported")
        else:
            print("Unknown upload error")
        return None
        
    except JobTimeoutException:
        print("Upload timed out - may still be processing")
        return None
        
    except PIXXIOException as e:
        print(f"API error during upload: {e}")
        return None

# Usage
result = safe_file_upload(
    "/path/to/image.jpg",
    title="Product Photo",
    keywords="product,photography"
)

if result:
    print(f"Upload successful: {result.id}")
else:
    print("Upload failed")
```

### Download Error Handling

```python
from pixxio_client.exceptions import FileDownloadException, FileConversionException

try:
    # Download with conversion
    result = files.download(123, format="PDF", size="A4")
    
except NotFoundException:
    print("File not found")
    
except FileConversionException as e:
    print(f"Conversion failed: {e}")
    
    # Try downloading original format
    try:
        original = files.download(123)
        print("Downloaded original format instead")
    except FileDownloadException:
        print("Cannot download in any format")
        
except FileDownloadException as e:
    print(f"Download failed: {e}")
```

## Job Processing Exceptions

### Job Timeout and Failure Handling

```python
from pixxio_client.exceptions import JobTimeoutException, JobFailedException, JobAbortedException

try:
    result = files.upload_and_wait(
        "/path/to/large_file.mp4",
        timeout=300  # 5 minutes
    )
    
except JobTimeoutException as e:
    print(f"Job {e.job_id} timed out after {e.timeout}s")
    print("Upload timed out, but may still be processing")
    
    # Option 1: Continue monitoring manually
    job_id = extract_job_id_from_last_response()  # Custom logic
    extended_result = monitor_job_manually(job_id, timeout=1800)
    
    # Option 2: Accept timeout and notify user
    notify_user("Upload is taking longer than expected")

# Job failure handling
try:
    result = files.upload_and_wait("/path/to/corrupted_file.pdf")
    
except JobFailedException as e:
    print(f"Job {e.job_id} failed: {e.error_message}")
    print(f"File processing failed: {e}")
    
    # Extract error details if available
    if hasattr(e, 'job_info') and e.job_info:
        error_details = e.job_info.error_message
        print(f"Detailed error: {error_details}")
    
    # Handle based on error type
    if "unsupported format" in str(e).lower():
        print("File format not supported")
    elif "corrupted" in str(e).lower():
        print("File appears to be corrupted")
    else:
        print("Unknown processing error")

# Job cancellation handling
try:
    jobs.wait_for_completion(job_id=123)
except JobAbortedException as e:
    print(f"Job {e.job_id} was cancelled")
    # Restart job if needed
```

## Connection and API Quota Exceptions

### Connection Exceptions

```python
from pixxio_client.exceptions import ConnectionException, TimeoutException

try:
    client = Client.create_client("key", "invalid-host.com")
    files.get()
except ConnectionException as e:
    print(f"Connection failed to {e.host}: {e}")
    # Check network and host URL

try:
    files.get()
except TimeoutException as e:
    print(f"Request timed out after {e.timeout_seconds}s")
    # Increase timeout or check network
```

### API Quota Exception

```python
from pixxio_client.exceptions import APIQuotaExceededException

try:
    files.upload("file.jpg")
except APIQuotaExceededException as e:
    print(f"Quota exceeded for {e.quota_type}")
    print(f"Limit: {e.limit}")
    if e.reset_time:
        print(f"Resets at: {e.reset_time}")
    # Wait for reset or upgrade plan
```

## Advanced Error Handling Patterns

### Retry with Exponential Backoff

```python
import time
import random
from pixxio_client.exceptions import (
    TooManyRequestsException,
    InternalServerErrorException,
    ServiceUnavailableException,
    ConnectionException,
    ServerError
)

def exponential_backoff_retry(
    operation_func,
    max_retries=5,
    base_delay=1.0,
    max_delay=60.0,
    exponential_base=2.0,
    jitter=True
):
    """
    Retry operation with exponential backoff.
    
    Args:
        operation_func: Function to retry
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay between retries
        exponential_base: Multiplier for delay calculation
        jitter: Add random jitter to prevent thundering herd
    """
    
    retryable_exceptions = (
        TooManyRequestsException,
        InternalServerErrorException,
        ServiceUnavailableException,
        ConnectionException,
        TimeoutError
    )
    
    for attempt in range(max_retries + 1):
        try:
            return operation_func()
            
        except TooManyRequestsException as e:
            if attempt == max_retries:
                raise  # Final attempt failed
                
            if e.retry_after:
                time.sleep(e.retry_after)
            else:
                delay = min(base_delay * (exponential_base ** attempt), max_delay)
                if jitter:
                    delay *= (0.5 + random.random() * 0.5)
                print(f"Rate limited, retrying in {delay:.1f}s...")
                time.sleep(delay)
                
        except ServiceUnavailableException as e:
            if attempt == max_retries:
                raise
                
            if e.retry_after:
                time.sleep(e.retry_after)
            else:
                delay = min(base_delay * (exponential_base ** attempt), max_delay)
                if jitter:
                    delay *= (0.5 + random.random() * 0.5)
                time.sleep(delay)
                
        except (ConnectionException, ServerError) as e:
            if attempt == max_retries:
                raise
                
            # Calculate delay with exponential backoff
            delay = min(base_delay * (exponential_base ** attempt), max_delay)
            
            # Add jitter to prevent thundering herd
            if jitter:
                delay *= (0.5 + random.random() * 0.5)
                
            print(f"Attempt {attempt + 1} failed ({e}), retrying in {delay:.1f}s...")
            time.sleep(delay)
        
        except Exception as e:
            # Non-retryable exception
            print(f"Non-retryable error: {e}")
            raise

# Usage
try:
    result = exponential_backoff_retry(
        lambda: files.upload("/path/to/file.jpg"),
        max_retries=3
    )
    print("Upload successful after retries")
except Exception as e:
    print(f"Upload failed after all retries: {e}")
```

### Circuit Breaker Pattern

```python
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"         # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def call(self, operation_func):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise ServiceUnavailableException("Circuit breaker is OPEN")
        
        try:
            result = operation_func()
            self._on_success()
            return result
            
        except (InternalServerErrorException, 
                ServiceUnavailableException,
                GatewayTimeoutException,
                ConnectionException) as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

# Usage
circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30)

def protected_api_call():
    try:
        return circuit_breaker.call(lambda: files.get())
    except ServiceUnavailableException as e:
        if "Circuit breaker" in str(e):
            print("Service temporarily unavailable (circuit breaker open)")
        else:
            print(f"Service error: {e}")
        return None

result = protected_api_call()
```

### Contextual Error Handler

```python
from contextlib import contextmanager

@contextmanager
def pixxio_error_handler(operation_name="API operation"):
    """Context manager for standardized error handling."""
    try:
        yield
        
    except UnauthorizedException:
        print(f"{operation_name} failed: Invalid authentication")
        print("Please check your API key")
        
    except ForbiddenException:
        print(f"{operation_name} failed: Insufficient permissions")
        print("Contact your administrator for access")
        
    except NotFoundException as e:
        print(f"{operation_name} failed: Resource not found")
        print(f"Details: {e}")
        
    except JobTimeoutException:
        print(f"{operation_name} timed out")
        print("The operation may still be processing in the background")
        
    except JobFailedException as e:
        print(f"{operation_name} processing failed: {e}")
        
    except TooManyRequestsException:
        print(f"{operation_name} failed: Rate limit exceeded")
        print("Please wait before trying again")
        
    except PIXXIOException as e:
        print(f"{operation_name} failed with API error: {e}")
        
    except Exception as e:
        print(f"{operation_name} failed with unexpected error: {e}")
        raise  # Re-raise unexpected exceptions

# Usage
with pixxio_error_handler("File upload"):
    result = files.upload("/path/to/file.jpg", title="My File")
    print(f"Upload successful: {result.id}")

with pixxio_error_handler("File conversion"):
    converted = files.download(123, format="PDF")
    print(f"Conversion successful")
```

## Comprehensive Error Handling Pattern

```python
def comprehensive_error_handler(operation_func, operation_name="API operation"):
    """
    Comprehensive error handling for all PIXXIO exception types.
    Returns a standardized result dictionary.
    """
    try:
        result = operation_func()
        return {
            'success': True,
            'data': result,
            'message': f'{operation_name} completed successfully'
        }
        
    except UnauthorizedException:
        return {
            'success': False,
            'error_type': 'authentication',
            'message': 'Authentication failed. Please check your API credentials.',
            'retry': False
        }
        
    except ForbiddenException:
        return {
            'success': False,
            'error_type': 'permission',
            'message': 'Insufficient permissions for this operation.',
            'retry': False
        }
        
    except NotFoundException:
        return {
            'success': False,
            'error_type': 'not_found',
            'message': 'The requested resource was not found.',
            'retry': False
        }
        
    except TooManyRequestsException as e:
        return {
            'success': False,
            'error_type': 'rate_limit',
            'message': 'Rate limit exceeded. Please wait and try again.',
            'retry': True,
            'retry_after': getattr(e, 'retry_after', 60)
        }
        
    except FileTooLargeException as e:
        return {
            'success': False,
            'error_type': 'file_too_large',
            'message': f'File is too large. Maximum size: {getattr(e, "max_size", "unknown")} bytes',
            'retry': False
        }
        
    except UnsupportedFileTypeException as e:
        return {
            'success': False,
            'error_type': 'unsupported_file_type',
            'message': f'File type not supported: {getattr(e, "file_type", "unknown")}',
            'retry': False,
            'supported_types': getattr(e, 'supported_types', [])
        }
        
    except JobTimeoutException as e:
        return {
            'success': False,
            'error_type': 'timeout',
            'message': f'{operation_name} timed out but may still be processing.',
            'retry': True,
            'retry_after': 300,
            'job_id': getattr(e, 'job_id', None)
        }
        
    except JobFailedException as e:
        return {
            'success': False,
            'error_type': 'job_failed',
            'message': f'Processing failed: {getattr(e, "error_message", str(e))}',
            'retry': False,
            'job_id': getattr(e, 'job_id', None)
        }
        
    except APIQuotaExceededException as e:
        return {
            'success': False,
            'error_type': 'quota_exceeded',
            'message': 'API quota exceeded.',
            'retry': True,
            'retry_after': getattr(e, 'reset_time', None)
        }
        
    except ServiceUnavailableException:
        return {
            'success': False,
            'error_type': 'service_unavailable',
            'message': 'Service is temporarily unavailable.',
            'retry': True,
            'retry_after': 60
        }
        
    except PIXXIOException as e:
        return {
            'success': False,
            'error_type': 'api_error',
            'message': f'API error: {str(e)}',
            'retry': True,
            'retry_after': 30
        }
        
    except Exception as e:
        return {
            'success': False,
            'error_type': 'unexpected',
            'message': f'Unexpected error: {str(e)}',
            'retry': False
        }

# Usage
result = comprehensive_error_handler(
    lambda: files.upload("/path/to/file.jpg"),
    "File upload"
)

if result['success']:
    print(f"Success: {result['message']}")
    print(f"File ID: {result['data'].id}")
else:
    print(f"Error: {result['message']}")
    if result.get('retry'):
        print(f"Retry recommended after {result.get('retry_after', 60)} seconds")
```

## Exception Properties and Context

All PIXXIO exceptions include these properties for detailed error analysis:

```python
try:
    result = files.post(json_data={'invalid': 'data'})
    
except PIXXIOException as e:
    # Basic error information
    print(f"Error message: {e}")
    print(f"Error type: {type(e).__name__}")
    
    # HTTP response details (if available)
    if hasattr(e, 'status_code'):
        print(f"HTTP status: {e.status_code}")
    
    if hasattr(e, 'response') and e.response:
        print(f"Response body: {e.response.text}")
    
    # Parsed response object (if available)
    if hasattr(e, 'response_object') and e.response_object:
        print(f"Parsed response: {e.response_object}")
    
    # Structured error data (if available)
    if hasattr(e, 'error_data') and e.error_data:
        print(f"Error code: {e.error_data.get('code')}")
        print(f"Error details: {e.error_data.get('details')}")
        
        # Field-specific validation errors
        if 'validation_errors' in e.error_data:
            for field, errors in e.error_data['validation_errors'].items():
                print(f"Field '{field}': {', '.join(errors)}")
```

## Error Logging and Monitoring

### Structured Error Logging

```python
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pixxio_client.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('pixxio_client')

def log_pixxio_error(e: PIXXIOException, context: dict = None):
    """Log structured error data for analysis."""
    error_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "error_type": type(e).__name__,
        "message": str(e),
        "status_code": getattr(e, 'status_code', None),
        "context": context or {}
    }
    
    # Add exception-specific data
    if isinstance(e, FileUploadException):
        error_data["file_path"] = getattr(e, 'file_path', None)
        error_data["file_size"] = getattr(e, 'file_size', None)
    elif isinstance(e, JobException):
        error_data["job_id"] = getattr(e, 'job_id', None)
        error_data["job_status"] = getattr(e, 'job_status', None)
    elif isinstance(e, TooManyRequestsException):
        error_data["retry_after"] = getattr(e, 'retry_after', None)
    
    logger.error(json.dumps(error_data, indent=2))

def logged_operation(operation_func, operation_name="API operation", context=None):
    """Wrapper that logs all errors for analysis."""
    try:
        logger.info(f"Starting {operation_name}")
        result = operation_func()
        logger.info(f"Completed {operation_name} successfully")
        return result
        
    except PIXXIOException as e:
        log_pixxio_error(e, context)
        raise
        
    except Exception as e:
        logger.exception(f"{operation_name} failed with unexpected error")
        raise

# Usage
try:
    result = logged_operation(
        lambda: files.upload("/path/to/file.jpg"),
        "File upload",
        {"user_id": 123, "file_type": "image"}
    )
except PIXXIOException:
    pass  # Already logged
```

## Best Practices

### 1. Be Specific with Exception Handling

```python
# ✅ Good: Handle specific exceptions
try:
    result = files.get(file_id)
except NotFoundException:
    handle_missing_file()
except UnauthorizedException:
    handle_auth_error()
except PIXXIOException as e:
    handle_general_api_error(e)

# ❌ Avoid: Catching all exceptions
try:
    result = files.get(file_id)
except Exception as e:  # Too broad
    handle_error(e)
```

### 2. Implement Appropriate Retry Strategies

```python
# ✅ Good: Retry transient errors with backoff
retryable = (TooManyRequestsException, ServiceUnavailableException)
try:
    result = exponential_backoff_retry(lambda: files.upload("file.jpg"))
except retryable:
    # Handle after all retries failed
    pass

# ❌ Avoid: Retrying non-retryable errors
try:
    result = files.upload("file.jpg")
except NotFoundException:  # Don't retry
    retry_upload()  # File will still not exist
```

### 3. Provide User-Friendly Error Messages

```python
def user_friendly_error_handler(operation_func, operation_name):
    try:
        return operation_func()
    except UnauthorizedException:
        return {
            'success': False,
            'message': 'Please check your login credentials and try again.',
            'retry': False
        }
    except NotFoundException:
        return {
            'success': False,
            'message': 'The requested item could not be found.',
            'retry': False
        }
    except TooManyRequestsException:
        return {
            'success': False,
            'message': 'Too many requests. Please wait a moment and try again.',
            'retry': True,
            'retry_after': 60
        }
```

### 4. Use Context Managers for Cleanup

```python
@contextmanager
def file_upload_context(file_path):
    """Ensure proper cleanup even if upload fails."""
    temp_file = None
    try:
        # Prepare file (e.g., compress, convert)
        temp_file = prepare_file(file_path)
        yield temp_file
    except PIXXIOException as e:
        logger.error(f"Upload failed: {e}")
        raise
    finally:
        # Cleanup temporary files
        if temp_file and os.path.exists(temp_file):
            os.unlink(temp_file)

# Usage
with file_upload_context("/path/to/file.jpg") as prepared_file:
    result = files.upload(prepared_file)
```

### 5. Graceful Degradation

```python
def upload_with_fallback(file_path):
    try:
        # Try high quality upload
        return files.upload(file_path, quality="high")
        
    except FileTooLargeException:
        # Fallback to compressed upload
        return files.upload(file_path, quality="medium", compress=True)
        
    except UnsupportedFileTypeException as e:
        if e.file_type in ["heic", "raw"]:
            # Convert and retry
            converted_path = convert_image(file_path, "jpg")
            return files.upload(converted_path)
        raise
        
    except APIQuotaExceededException:
        # Queue for later processing
        queue_upload(file_path)
        return {"queued": True, "message": "Upload queued due to quota"}

def get_file_with_fallback(file_id):
    """Get file info with fallback options."""
    try:
        # Try to get full file information
        return files.get(file_id)
        
    except NotFoundException:
        # File doesn't exist
        return None
        
    except UnauthorizedException:
        # Can't access - try basic info only
        try:
            return get_basic_file_info(file_id)  # Custom implementation
        except:
            return None
            
    except PIXXIOException:
        # API issue - use cached data if available
        cached_data = get_cached_file_info(file_id)  # Custom implementation
        if cached_data:
            return cached_data
        return None
```

## Migration from Legacy Exceptions

The enhanced exception system is backwards compatible. Legacy code continues to work:

```python
# Legacy code (still works)
try:
    files.get()
except ResponseException as e:
    print(f"Error: {e}")

# Enhanced code (recommended)
try:
    files.get()
except UnauthorizedException as e:
    print(f"Auth error: {e}")
except NotFoundException as e:
    print(f"Not found: {e}")
except PIXXIOException as e:
    print(f"API error: {e}")
```

## Summary

This comprehensive error handling system provides:

- **Specific Exception Types**: Handle different error scenarios appropriately
- **Detailed Error Context**: Access HTTP status, response data, and error details
- **Recovery Patterns**: Retry, circuit breaker, and graceful degradation strategies
- **User-Friendly Messages**: Convert technical errors to actionable user feedback
- **Monitoring Support**: Structured logging and error pattern detection
- **Best Practices**: Guidelines for robust error handling implementation

By following these patterns, you can build resilient applications that handle PIXXIO API errors gracefully and provide excellent user experiences even when things go wrong.

---

For more information, see:
- [API Reference](API_REFERENCE.md) - Complete API documentation
- [Async Operations](ASYNC_OPERATIONS.md) - Job tracking and async patterns
- [Developer Guide](DEVELOPER_GUIDE.md) - Architecture and contribution guidelines
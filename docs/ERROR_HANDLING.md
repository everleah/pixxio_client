# Error Handling Guide

This guide covers the comprehensive error handling system in the PIXXIO Python client library.

## Exception Hierarchy

The library provides a structured exception hierarchy for different types of errors:

```python
PIXXIOException                    # Base exception
├── BadRequestException           # 400 Bad Request
├── UnauthorizedException         # 401 Unauthorized  
├── ForbiddenException           # 403 Forbidden
├── NotFoundException            # 404 Not Found
├── ConflictException            # 409 Conflict
├── UnprocessableEntityException # 422 Unprocessable Entity
├── TooManyRequestsException     # 429 Too Many Requests
├── InternalServerErrorException # 500 Internal Server Error
├── BadGatewayException          # 502 Bad Gateway
├── ServiceUnavailableException  # 503 Service Unavailable
├── GatewayTimeoutException      # 504 Gateway Timeout
├── JobTimeoutException          # Job didn't complete in time
├── JobFailedException           # Job execution failed
├── FileUploadException          # File upload specific errors
├── FileDownloadException        # File download specific errors
└── FileConversionException      # File conversion specific errors
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

### Authentication Errors (401)

```python
from pixxio_client.exceptions import UnauthorizedException

try:
    client = Client.create_client("invalid-key", "company.pixxio.com")
    files = File(client)
    result = files.get()
    
except UnauthorizedException:
    print("Invalid API key - check your credentials")
    # Handle: prompt for new key, refresh token, etc.
```

### Permission Errors (403)

```python
from pixxio_client.exceptions import ForbiddenException

try:
    result = files.delete(file_id=123)
    
except ForbiddenException:
    print("Insufficient permissions to delete this file")
    # Handle: check user permissions, request access, etc.
```

### Resource Not Found (404)

```python
from pixxio_client.exceptions import NotFoundException

try:
    file_info = files.get(999999)
    
except NotFoundException:
    print("File does not exist")
    # Handle: validate ID, show error message, etc.
```

### Validation Errors (400, 422)

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
    # Handle: validate input, show field errors, etc.
    
except UnprocessableEntityException as e:
    print(f"Validation failed: {e}")
    # Handle: show specific validation errors, correct input, etc.
```

### Rate Limiting (429)

```python
from pixxio_client.exceptions import TooManyRequestsException
import time

def upload_with_rate_limiting(file_path):
    max_retries = 3
    retry_delay = 60  # Start with 1 minute
    
    for attempt in range(max_retries):
        try:
            return files.upload(file_path)
            
        except TooManyRequestsException:
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

### Server Errors (500, 502, 503, 504)

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
            
        except (InternalServerErrorException, 
                BadGatewayException, 
                ServiceUnavailableException,
                GatewayTimeoutException) as e:
                
            if attempt == max_retries - 1:
                raise  # Final attempt failed
                
            wait_time = (attempt + 1) * 30  # 30, 60, 90 seconds
            print(f"Server error ({e}), retrying in {wait_time} seconds...")
            time.sleep(wait_time)

# Usage
try:
    result = robust_api_call(lambda: files.get())
except (InternalServerErrorException, ServiceUnavailableException):
    print("Server is currently unavailable")
```

## Job-Related Exceptions

### Job Timeout Handling

```python
from pixxio_client.exceptions import JobTimeoutException

try:
    result = files.upload_and_wait(
        "/path/to/large_file.mp4",
        timeout=300  # 5 minutes
    )
    
except JobTimeoutException:
    print("Upload timed out, but may still be processing")
    
    # Option 1: Continue monitoring manually
    job_id = extract_job_id_from_last_response()  # Custom logic
    extended_result = monitor_job_manually(job_id, timeout=1800)
    
    # Option 2: Accept timeout and notify user
    notify_user("Upload is taking longer than expected")
```

### Job Failure Handling

```python
from pixxio_client.exceptions import JobFailedException

try:
    result = files.upload_and_wait("/path/to/corrupted_file.pdf")
    
except JobFailedException as e:
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
```

## File Operation Exceptions

### Upload Error Handling

```python
from pixxio_client.exceptions import FileUploadException

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
        
    except FileUploadException as e:
        print(f"Upload failed: {e}")
        
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

## Advanced Error Handling Patterns

### Retry with Exponential Backoff

```python
import time
import random
from pixxio_client.exceptions import (
    TooManyRequestsException,
    InternalServerErrorException,
    ServiceUnavailableException
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
        ConnectionError,
        TimeoutError
    )
    
    for attempt in range(max_retries + 1):
        try:
            return operation_func()
            
        except retryable_exceptions as e:
            if attempt == max_retries:
                raise  # Final attempt failed
                
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
                GatewayTimeoutException) as e:
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
from pixxio_client.exceptions import PIXXIOException

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

## Error Response Details

### Extracting Error Information

```python
try:
    result = files.post(json_data={'invalid': 'data'})
    
except PIXXIOException as e:
    # Basic error information
    print(f"Error message: {e}")
    print(f"Error type: {type(e).__name__}")
    
    # Detailed error information (if available)
    if hasattr(e, 'response') and e.response:
        print(f"HTTP status: {e.response.status_code}")
        print(f"Response body: {e.response.text}")
    
    # Structured error data (if available)
    if hasattr(e, 'error_data') and e.error_data:
        print(f"Error code: {e.error_data.get('code')}")
        print(f"Error details: {e.error_data.get('details')}")
        
        # Field-specific validation errors
        if 'validation_errors' in e.error_data:
            for field, errors in e.error_data['validation_errors'].items():
                print(f"Field '{field}': {', '.join(errors)}")
```

### Logging Errors

```python
import logging

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

def logged_operation(operation_func, operation_name="API operation"):
    """Wrapper that logs all errors for analysis."""
    try:
        logger.info(f"Starting {operation_name}")
        result = operation_func()
        logger.info(f"Completed {operation_name} successfully")
        return result
        
    except PIXXIOException as e:
        logger.error(f"{operation_name} failed: {type(e).__name__}: {e}")
        
        # Log additional context
        if hasattr(e, 'response'):
            logger.error(f"HTTP {e.response.status_code}: {e.response.text}")
            
        raise
        
    except Exception as e:
        logger.exception(f"{operation_name} failed with unexpected error")
        raise

# Usage
try:
    result = logged_operation(
        lambda: files.upload("/path/to/file.jpg"),
        "File upload"
    )
except PIXXIOException:
    pass  # Already logged
```

## Best Practices

### 1. Be Specific with Exception Handling

```python
# Good: Handle specific exceptions
try:
    result = files.get(file_id)
except NotFoundException:
    handle_missing_file()
except UnauthorizedException:
    handle_auth_error()
except PIXXIOException as e:
    handle_general_api_error(e)

# Avoid: Catching all exceptions
try:
    result = files.get(file_id)
except Exception as e:  # Too broad
    handle_error(e)
```

### 2. Provide User-Friendly Error Messages

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
    except JobTimeoutException:
        return {
            'success': False,
            'message': f'{operation_name} is taking longer than expected. It may still complete in the background.',
            'retry': True,
            'retry_after': 300
        }
```

### 3. Implement Graceful Degradation

```python
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

### 4. Monitor and Alert on Errors

```python
import json
from datetime import datetime

def error_monitoring_wrapper(operation_func, operation_name):
    """Wrapper that monitors error patterns for alerting."""
    try:
        return operation_func()
    except PIXXIOException as e:
        # Log structured error data
        error_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'operation': operation_name,
            'error_type': type(e).__name__,
            'error_message': str(e),
            'http_status': getattr(e, 'response', {}).get('status_code'),
        }
        
        # Send to monitoring system
        send_to_monitoring(error_record)  # Custom implementation
        
        # Check if this indicates a service outage
        if isinstance(e, (ServiceUnavailableException, InternalServerErrorException)):
            check_for_service_outage()  # Custom implementation
        
        raise

def send_to_monitoring(error_record):
    """Send error data to monitoring system."""
    # Implementation depends on your monitoring setup
    # Could be: logging, metrics, alerts, etc.
    pass

def check_for_service_outage():
    """Check error patterns to detect service outages."""
    # Custom logic to determine if errors indicate outage
    pass
```

---

For more information, see:
- [API Reference](../API_REFERENCE.md) - Complete API documentation
- [Async Operations](ASYNC_OPERATIONS.md) - Job tracking and async patterns
- [Developer Guide](DEVELOPER_GUIDE.md) - Architecture and contribution guidelines
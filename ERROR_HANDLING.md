# Enhanced Error Handling

This document describes the comprehensive exception hierarchy and error handling capabilities in the PIXXIO client library.

## Overview

The enhanced error handling system provides specific exception types for different error scenarios, enabling precise error handling and better debugging capabilities. All exceptions inherit from a common base class and include detailed context information.

## Exception Hierarchy

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
└── Legacy Exceptions (backwards compatibility)
    ├── ResponseExceptionBase
    ├── ResponseException
    ├── InvalidResponseException
    └── ResponseError
```

## HTTP Status Code Exceptions

### Client Errors (4xx)

#### BadRequestException (400)
```python
try:
    files.get(invalid_parameter="value")
except BadRequestException as e:
    print(f"Invalid request: {e}")
    print(f"Status: {e.status_code}")
```

#### UnauthorizedException (401)
```python
try:
    client = Client.create_client("invalid-key", "host.com")
    files.get()
except UnauthorizedException as e:
    print(f"Authentication failed: {e}")
    # Check API key and regenerate if needed
```

#### ForbiddenException (403)
```python
try:
    files.delete(file_id=123)
except ForbiddenException as e:
    print(f"Insufficient permissions: {e}")
    # Contact administrator for proper access
```

#### NotFoundException (404)
```python
try:
    files.get(id=99999)
except NotFoundException as e:
    print(f"Resource not found: {e}")
    # Verify resource exists
```

#### TooManyRequestsException (429)
```python
try:
    files.get()
except TooManyRequestsException as e:
    print(f"Rate limited: {e}")
    if e.retry_after:
        print(f"Retry after {e.retry_after} seconds")
        time.sleep(e.retry_after)
```

### Server Errors (5xx)

#### InternalServerErrorException (500)
```python
try:
    files.post(data=large_dataset)
except InternalServerErrorException as e:
    print(f"Server error: {e}")
    # Retry after delay or contact support
```

#### ServiceUnavailableException (503)
```python
try:
    files.get()
except ServiceUnavailableException as e:
    print(f"Service unavailable: {e}")
    if e.retry_after:
        time.sleep(e.retry_after)
    # Implement exponential backoff retry
```

## File Upload Exceptions

### FileTooLargeException
```python
try:
    files.upload("huge-video.mp4")
except FileTooLargeException as e:
    print(f"File too large: {e}")
    print(f"File size: {e.file_size} bytes")
    print(f"Max allowed: {e.max_size} bytes")
    # Compress or split file
```

### UnsupportedFileTypeException
```python
try:
    files.upload("document.xyz")
except UnsupportedFileTypeException as e:
    print(f"Unsupported file type: {e.file_type}")
    if e.supported_types:
        print(f"Supported: {', '.join(e.supported_types)}")
    # Convert to supported format
```

### Generic FileUploadException
```python
try:
    files.upload("file.jpg")
except FileUploadException as e:
    print(f"Upload failed: {e}")
    print(f"File: {e.file_path}")
    # Check file permissions and network
```

## Job Processing Exceptions

### JobTimeoutException
```python
try:
    jobs.wait_for_completion(job_id=123, timeout=60)
except JobTimeoutException as e:
    print(f"Job {e.job_id} timed out after {e.timeout}s")
    # Check job status manually or increase timeout
```

### JobFailedException
```python
try:
    jobs.wait_for_completion(job_id=123)
except JobFailedException as e:
    print(f"Job {e.job_id} failed: {e.error_message}")
    # Check job parameters and retry
```

### JobAbortedException
```python
try:
    jobs.wait_for_completion(job_id=123)
except JobAbortedException as e:
    print(f"Job {e.job_id} was cancelled")
    # Restart job if needed
```

## Connection Exceptions

### ConnectionException
```python
try:
    client = Client.create_client("key", "invalid-host.com")
    files.get()
except ConnectionException as e:
    print(f"Connection failed to {e.host}: {e}")
    # Check network and host URL
```

### TimeoutException
```python
try:
    files.get()
except TimeoutException as e:
    print(f"Request timed out after {e.timeout_seconds}s")
    # Increase timeout or check network
```

## API Quota Exception

### APIQuotaExceededException
```python
try:
    files.upload("file.jpg")
except APIQuotaExceededException as e:
    print(f"Quota exceeded for {e.quota_type}")
    print(f"Limit: {e.limit}")
    if e.reset_time:
        print(f"Resets at: {e.reset_time}")
    # Wait for reset or upgrade plan
```

## Exception Properties

All PIXXIO exceptions include these properties:

```python
except PIXXIOException as e:
    print(f"Exception type: {type(e).__name__}")
    print(f"Message: {e}")
    print(f"Status code: {e.status_code}")  # If HTTP response
    print(f"Response: {e.response}")        # Raw HTTP response
    print(f"Response object: {e.response_object}")  # Parsed API response
```

## Error Recovery Patterns

### Retry with Exponential Backoff
```python
import time
import random

def retry_with_backoff(func, max_retries=3, base_delay=1.0):
    for attempt in range(max_retries):
        try:
            return func()
            
        except TooManyRequestsException as e:
            if e.retry_after:
                time.sleep(e.retry_after)
            else:
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                time.sleep(delay)
                
        except ServiceUnavailableException as e:
            if e.retry_after:
                time.sleep(e.retry_after)
            else:
                delay = base_delay * (2 ** attempt)
                time.sleep(delay)
                
        except (ConnectionException, ServerError) as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)
            time.sleep(delay)
            
        except ClientError as e:
            # Don't retry client errors
            raise
            
    raise Exception(f"Max retries ({max_retries}) exceeded")

# Usage
try:
    result = retry_with_backoff(lambda: files.upload("file.jpg"))
except PIXXIOException as e:
    print(f"Upload failed after retries: {e}")
```

### Graceful Degradation
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
```

### Circuit Breaker Pattern
```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    def call(self, func, *args, **kwargs):
        if self.state == "open":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half-open"
            else:
                raise ServiceUnavailableException("Circuit breaker is open")
        
        try:
            result = func(*args, **kwargs)
            if self.state == "half-open":
                self.state = "closed"
                self.failure_count = 0
            return result
            
        except (ServerError, ConnectionException) as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
            
            raise

# Usage
breaker = CircuitBreaker()

try:
    result = breaker.call(files.upload, "file.jpg")
except ServiceUnavailableException as e:
    print("Service temporarily unavailable")
```

## Comprehensive Error Handling

### Catch All Pattern
```python
try:
    result = files.upload("file.jpg")
    
except ClientError as e:
    # Handle all 4xx errors
    if isinstance(e, UnauthorizedException):
        # Refresh authentication
        pass
    elif isinstance(e, ForbiddenException):
        # Request permissions
        pass
    elif isinstance(e, TooManyRequestsException):
        # Implement rate limiting
        pass
    else:
        # Generic client error
        print(f"Client error: {e}")
        
except ServerError as e:
    # Handle all 5xx errors
    print(f"Server error: {e}")
    # Implement retry logic
    
except FileUploadException as e:
    # Handle file-specific errors
    if isinstance(e, FileTooLargeException):
        # Compress file
        pass
    elif isinstance(e, UnsupportedFileTypeException):
        # Convert format
        pass
    else:
        print(f"Upload error: {e}")
        
except JobException as e:
    # Handle job-specific errors
    if isinstance(e, JobTimeoutException):
        # Increase timeout or check status
        pass
    elif isinstance(e, JobFailedException):
        # Retry with different parameters
        pass
    else:
        print(f"Job error: {e}")
        
except PIXXIOException as e:
    # Catch-all for any PIXXIO API error
    print(f"PIXXIO API error: {e}")
    
except Exception as e:
    # Unexpected non-PIXXIO errors
    print(f"Unexpected error: {e}")
```

### Structured Error Logging
```python
import logging
import json

def log_pixxio_error(e: PIXXIOException, context: dict = None):
    error_data = {
        "error_type": type(e).__name__,
        "message": str(e),
        "status_code": getattr(e, 'status_code', None),
        "context": context or {}
    }
    
    # Add exception-specific data
    if isinstance(e, FileUploadException):
        error_data["file_path"] = e.file_path
        error_data["file_size"] = e.file_size
    elif isinstance(e, JobException):
        error_data["job_id"] = e.job_id
        error_data["job_status"] = e.job_status
    elif isinstance(e, TooManyRequestsException):
        error_data["retry_after"] = e.retry_after
    
    logging.error(json.dumps(error_data, indent=2))

# Usage
try:
    files.upload("large-file.mp4")
except PIXXIOException as e:
    log_pixxio_error(e, {"operation": "upload", "user_id": 123})
    raise
```

## Best Practices

1. **Specific Exception Handling**: Catch specific exception types rather than generic ones
2. **Error Context**: Use exception properties to access detailed error information
3. **Retry Logic**: Implement appropriate retry strategies for transient errors
4. **Graceful Degradation**: Provide fallback options when operations fail
5. **User Feedback**: Convert technical errors to user-friendly messages
6. **Logging**: Log detailed error information for debugging
7. **Circuit Breaking**: Prevent cascade failures with circuit breaker patterns
8. **Rate Limiting**: Respect API rate limits and implement backoff strategies

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

This enhanced error handling system provides robust, specific error management capabilities that enable better error recovery, debugging, and user experience in PIXXIO client applications.
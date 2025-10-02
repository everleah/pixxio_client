
"""
Enhanced exception hierarchy for PIXXIO API client.

This module provides specific exception types for different HTTP status codes
and PIXXIO API error conditions to enable better error handling and debugging.
"""

from typing import Optional, Any, Dict
from requests import Response


class PIXXIOException(Exception):
    """Base exception class for all PIXXIO API related errors."""
    
    def __init__(self, message: Optional[str] = None, response: Optional[Response] = None, 
                 response_object: Any = None):
        if message is None:
            message = "PIXXIO API error occurred"
        self.response = response
        self.response_object = response_object
        self.status_code = response.status_code if response else None
        super().__init__(message)


class ResponseExceptionBase(PIXXIOException):
    """Legacy base exception for backwards compatibility."""

    def __init__(self, message: Optional[str] = None):
        if message is None:
            message = "no response message"
        self.response_object = None
        super().__init__(message)

class ResponseException(ResponseExceptionBase):

    def __init__(self, response_object = None):
        self.response_object = response_object
        if response_object:
            try:
                # Try different possible error message field names
                message = (getattr(response_object, 'errormessage', None) or 
                          getattr(response_object, 'errorMessage', None) or
                          getattr(response_object, 'message', None) or
                          f"API error (code: {getattr(response_object, 'errorcode', 'unknown')})")
            except Exception as ex: 
                message = f"??? invalid response object ??? ({ex})"
        else:
            message = "no response object"
        return super().__init__(message)
    
class InvalidResponseException(ResponseException):

    def __init__(self, invalid_response_object = None):
        self.response_object = invalid_response_object
        if self.response_object:
            message = f"invalid response"
        else:
            message = "no response object"
        return super().__init__(message)
    
class ResponseError(ResponseException):

    def __init__(self, exception, message = None):
        self.exception = exception
        if message is None:
            message = str(exception)
        return super().__init__(message)


# HTTP Status Code Specific Exceptions
class HTTPException(PIXXIOException):
    """Base class for HTTP status code related errors."""
    pass


class ClientError(HTTPException):
    """Base class for 4xx client errors."""
    pass


class ServerError(HTTPException):
    """Base class for 5xx server errors."""
    pass


# 4xx Client Error Exceptions
class BadRequestException(ClientError):
    """400 Bad Request - Invalid request parameters or format."""
    
    def __init__(self, message: Optional[str] = None, response: Optional[Response] = None, 
                 response_object: Any = None):
        if message is None:
            message = "Bad request: Invalid parameters or request format"
        super().__init__(message, response, response_object)


class UnauthorizedException(ClientError):
    """401 Unauthorized - Invalid or missing authentication credentials."""
    
    def __init__(self, message: Optional[str] = None, response: Optional[Response] = None,
                 response_object: Any = None):
        if message is None:
            message = "Unauthorized: Invalid or missing API key"
        super().__init__(message, response, response_object)


class ForbiddenException(ClientError):
    """403 Forbidden - Authentication valid but insufficient permissions."""
    
    def __init__(self, message: Optional[str] = None, response: Optional[Response] = None,
                 response_object: Any = None):
        if message is None:
            message = "Forbidden: Insufficient permissions for this operation"
        super().__init__(message, response, response_object)


class NotFoundException(ClientError):
    """404 Not Found - Requested resource does not exist."""
    
    def __init__(self, message: Optional[str] = None, response: Optional[Response] = None,
                 response_object: Any = None):
        if message is None:
            message = "Not found: Requested resource does not exist"
        super().__init__(message, response, response_object)


class MethodNotAllowedException(ClientError):
    """405 Method Not Allowed - HTTP method not supported for this endpoint."""
    
    def __init__(self, message: Optional[str] = None, response: Optional[Response] = None,
                 response_object: Any = None):
        if message is None:
            message = "Method not allowed: HTTP method not supported for this endpoint"
        super().__init__(message, response, response_object)


class ConflictException(ClientError):
    """409 Conflict - Request conflicts with current state of resource."""
    
    def __init__(self, message: Optional[str] = None, response: Optional[Response] = None,
                 response_object: Any = None):
        if message is None:
            message = "Conflict: Request conflicts with current state of resource"
        super().__init__(message, response, response_object)


class UnprocessableEntityException(ClientError):
    """422 Unprocessable Entity - Request format correct but contains semantic errors."""
    
    def __init__(self, message: Optional[str] = None, response: Optional[Response] = None,
                 response_object: Any = None):
        if message is None:
            message = "Unprocessable entity: Request contains semantic errors"
        super().__init__(message, response, response_object)


class TooManyRequestsException(ClientError):
    """429 Too Many Requests - Rate limit exceeded."""
    
    def __init__(self, message: Optional[str] = None, response: Optional[Response] = None,
                 response_object: Any = None, retry_after: Optional[int] = None):
        if message is None:
            retry_msg = f" (retry after {retry_after}s)" if retry_after else ""
            message = f"Rate limit exceeded{retry_msg}"
        self.retry_after = retry_after
        super().__init__(message, response, response_object)


# 5xx Server Error Exceptions
class InternalServerErrorException(ServerError):
    """500 Internal Server Error - Unexpected server error."""
    
    def __init__(self, message: Optional[str] = None, response: Optional[Response] = None,
                 response_object: Any = None):
        if message is None:
            message = "Internal server error: Unexpected server-side error occurred"
        super().__init__(message, response, response_object)


class BadGatewayException(ServerError):
    """502 Bad Gateway - Server received invalid response from upstream."""
    
    def __init__(self, message: Optional[str] = None, response: Optional[Response] = None,
                 response_object: Any = None):
        if message is None:
            message = "Bad gateway: Server received invalid response from upstream"
        super().__init__(message, response, response_object)


class ServiceUnavailableException(ServerError):
    """503 Service Unavailable - Server temporarily unavailable."""
    
    def __init__(self, message: Optional[str] = None, response: Optional[Response] = None,
                 response_object: Any = None, retry_after: Optional[int] = None):
        if message is None:
            retry_msg = f" (retry after {retry_after}s)" if retry_after else ""
            message = f"Service unavailable{retry_msg}"
        self.retry_after = retry_after
        super().__init__(message, response, response_object)


class GatewayTimeoutException(ServerError):
    """504 Gateway Timeout - Server timeout waiting for upstream response."""
    
    def __init__(self, message: Optional[str] = None, response: Optional[Response] = None,
                 response_object: Any = None):
        if message is None:
            message = "Gateway timeout: Server timeout waiting for upstream response"
        super().__init__(message, response, response_object)


# PIXXIO-Specific Business Logic Exceptions
class APIQuotaExceededException(PIXXIOException):
    """API quota or usage limit exceeded."""
    
    def __init__(self, message: Optional[str] = None, quota_type: Optional[str] = None,
                 limit: Optional[int] = None, reset_time: Optional[str] = None):
        if message is None:
            message = f"API quota exceeded for {quota_type}" if quota_type else "API quota exceeded"
        self.quota_type = quota_type
        self.limit = limit
        self.reset_time = reset_time
        super().__init__(message)


class FileUploadException(PIXXIOException):
    """File upload related errors."""
    
    def __init__(self, message: Optional[str] = None, file_path: Optional[str] = None,
                 file_size: Optional[int] = None, max_size: Optional[int] = None):
        if message is None:
            message = "File upload failed"
        self.file_path = file_path
        self.file_size = file_size
        self.max_size = max_size
        super().__init__(message)


class FileTooLargeException(FileUploadException):
    """File exceeds maximum allowed size."""
    
    def __init__(self, file_path: Optional[str] = None, file_size: Optional[int] = None,
                 max_size: Optional[int] = None):
        message = f"File too large: {file_size} bytes exceeds limit of {max_size} bytes" \
                  if file_size and max_size else "File exceeds maximum allowed size"
        super().__init__(message, file_path, file_size, max_size)


class UnsupportedFileTypeException(FileUploadException):
    """File type not supported by PIXXIO."""
    
    def __init__(self, file_path: Optional[str] = None, file_type: Optional[str] = None,
                 supported_types: Optional[list] = None):
        message = f"Unsupported file type: {file_type}" if file_type else "Unsupported file type"
        if supported_types:
            message += f". Supported types: {', '.join(supported_types)}"
        self.file_type = file_type
        self.supported_types = supported_types
        super().__init__(message, file_path)


class JobException(PIXXIOException):
    """Job processing related errors."""
    
    def __init__(self, message: Optional[str] = None, job_id: Optional[int] = None,
                 job_status: Optional[str] = None):
        if message is None:
            message = f"Job {job_id} error" if job_id else "Job processing error"
        self.job_id = job_id
        self.job_status = job_status
        super().__init__(message)


class JobTimeoutException(JobException):
    """Job processing timeout."""
    
    def __init__(self, job_id: Optional[int] = None, timeout: Optional[int] = None):
        message = f"Job {job_id} timed out after {timeout} seconds" if job_id and timeout \
                  else f"Job {job_id} timed out" if job_id else "Job processing timed out"
        super().__init__(message, job_id)
        self.timeout = timeout


class JobFailedException(JobException):
    """Job processing failed."""
    
    def __init__(self, job_id: Optional[int] = None, error_message: Optional[str] = None):
        message = f"Job {job_id} failed: {error_message}" if job_id and error_message \
                  else f"Job {job_id} failed" if job_id else "Job processing failed"
        super().__init__(message, job_id, "failed")
        self.error_message = error_message


class JobAbortedException(JobException):
    """Job was aborted/cancelled."""
    
    def __init__(self, job_id: Optional[int] = None):
        message = f"Job {job_id} was aborted" if job_id else "Job was aborted"
        super().__init__(message, job_id, "aborted")


# Connection and Network Exceptions
class ConnectionException(PIXXIOException):
    """Network connection related errors."""
    
    def __init__(self, message: Optional[str] = None, host: Optional[str] = None):
        if message is None:
            message = f"Connection error to {host}" if host else "Connection error"
        self.host = host
        super().__init__(message)


class TimeoutException(ConnectionException):
    """Request timeout."""
    
    def __init__(self, timeout_seconds: Optional[float] = None, host: Optional[str] = None):
        message = f"Request timed out after {timeout_seconds}s" if timeout_seconds \
                  else "Request timed out"
        if host:
            message += f" connecting to {host}"
        self.timeout_seconds = timeout_seconds
        super().__init__(message, host)


    
def get_response_exception(
        response_object=None, message: Optional[str] = None, 
        exception=None, response: Optional[Response] = None) -> PIXXIOException:
    """
    Create appropriate exception based on response details.
    
    Args:
        response_object: Parsed response object from API
        message: Custom error message
        exception: Original exception that occurred
        response: HTTP response object
        
    Returns:
        Appropriate PIXXIOException subclass based on error type
    """
    
    # Extract message from response if not provided
    if response and message is None:
        if hasattr(response, 'reason') and response.reason:
            message = response.reason
    
    # Extract additional error details from response object
    if response_object and hasattr(response_object, 'errorMessage'):
        api_message = getattr(response_object, 'errorMessage', '')
        if api_message and (not message or message == getattr(response, 'reason', '')):
            message = api_message
    
    # Handle network/connection errors
    if exception:
        if isinstance(exception, (ConnectionError, OSError)):
            return ConnectionException(message or str(exception))
        elif 'timeout' in str(exception).lower():
            return TimeoutException()
        else:
            return ResponseError(exception, message)
    
    # Handle HTTP status code errors
    if response and hasattr(response, 'status_code'):
        status_code = response.status_code
        
        # Get retry-after header for rate limiting
        retry_after = None
        if hasattr(response, 'headers') and 'Retry-After' in response.headers:
            try:
                retry_after = int(response.headers['Retry-After'])
            except (ValueError, TypeError):
                retry_after = None
        
        # Map status codes to specific exceptions
        if status_code == 400:
            return BadRequestException(message, response, response_object)
        elif status_code == 401:
            return UnauthorizedException(message, response, response_object)
        elif status_code == 403:
            return ForbiddenException(message, response, response_object)
        elif status_code == 404:
            return NotFoundException(message, response, response_object)
        elif status_code == 405:
            return MethodNotAllowedException(message, response, response_object)
        elif status_code == 409:
            return ConflictException(message, response, response_object)
        elif status_code == 422:
            return UnprocessableEntityException(message, response, response_object)
        elif status_code == 429:
            return TooManyRequestsException(message, response, response_object, retry_after)
        elif status_code == 500:
            return InternalServerErrorException(message, response, response_object)
        elif status_code == 502:
            return BadGatewayException(message, response, response_object)
        elif status_code == 503:
            return ServiceUnavailableException(message, response, response_object, retry_after)
        elif status_code == 504:
            return GatewayTimeoutException(message, response, response_object)
    
    # Handle PIXXIO-specific business logic errors
    if response_object:
        # Check for specific error codes
        if hasattr(response_object, 'errorcode'):
            error_code_num = getattr(response_object, 'errorcode', None)
            
            # File not found error
            if error_code_num == 2454:
                return NotFoundException(message, response, response_object)
            # Authentication error
            elif error_code_num == 15007:
                return UnauthorizedException(message, response, response_object)
        
        # Check for quota exceeded
        if hasattr(response_object, 'errorCode'):
            error_code = getattr(response_object, 'errorCode', '') or ''
            
            if 'quota' in error_code.lower() or 'limit' in error_code.lower():
                return APIQuotaExceededException(message)
            
            # File upload specific errors
            elif 'file' in error_code.lower():
                if 'size' in error_code.lower() or 'large' in error_code.lower():
                    return FileTooLargeException()
                elif 'type' in error_code.lower() or 'format' in error_code.lower():
                    return UnsupportedFileTypeException()
                else:
                    return FileUploadException(message)
            
            # Job specific errors
            elif 'job' in error_code.lower():
                if 'timeout' in error_code.lower():
                    return JobTimeoutException()
                elif 'failed' in error_code.lower():
                    return JobFailedException(error_message=message)
                elif 'abort' in error_code.lower():
                    return JobAbortedException()
                else:
                    return JobException(message)
            
            # Generic API error with error code
            return ResponseException(response_object)
        
        # Invalid response object
        return InvalidResponseException(response_object)
    
    # Fallback to base exception
    return ResponseExceptionBase(message)


# Enhanced exception creation helpers
def create_http_exception(status_code: int, message: Optional[str] = None, 
                         response: Optional[Response] = None, 
                         response_object: Any = None) -> PIXXIOException:
    """Create specific HTTP exception based on status code."""
    return get_response_exception(response_object, message, None, response)


def create_job_exception(job_id: Optional[int] = None, status: Optional[str] = None,
                        message: Optional[str] = None) -> JobException:
    """Create job-specific exception based on job status."""
    if status == 'failed':
        return JobFailedException(job_id, message)
    elif status == 'aborted':
        return JobAbortedException(job_id)
    elif status == 'timeout':
        return JobTimeoutException(job_id)
    else:
        return JobException(message, job_id, status)


def create_file_exception(error_type: str, file_path: Optional[str] = None,
                         **kwargs) -> FileUploadException:
    """Create file-specific exception based on error type."""
    if error_type == 'too_large':
        return FileTooLargeException(file_path, **kwargs)
    elif error_type == 'unsupported_type':
        return UnsupportedFileTypeException(file_path, **kwargs)
    else:
        return FileUploadException(file_path=file_path, **kwargs)
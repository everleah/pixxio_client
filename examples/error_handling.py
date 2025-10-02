"""
Enhanced Error Handling Examples for PIXXIO Client

This file demonstrates the comprehensive exception handling capabilities
with specific exception types for different error scenarios.
"""

import time
from typing import Optional

from pixxio_client import Client, Authentication
from pixxio_client.files import File
from pixxio_client.jobs import Job

# Import specific exception types
from pixxio_client.exceptions import (
    # HTTP Status Code Exceptions
    BadRequestException, UnauthorizedException, ForbiddenException,
    NotFoundException, TooManyRequestsException, InternalServerErrorException,
    ServiceUnavailableException,
    
    # PIXXIO Business Logic Exceptions
    FileUploadException, FileTooLargeException, UnsupportedFileTypeException,
    JobException, JobTimeoutException, JobFailedException, JobAbortedException,
    APIQuotaExceededException,
    
    # Connection Exceptions
    ConnectionException, TimeoutException,
    
    # Base Exception Types
    PIXXIOException, ClientError, ServerError
)


def demonstrate_http_error_handling():
    """Demonstrate handling of HTTP status code exceptions."""
    
    client = Client.create_client("invalid-api-key", "api.pixxio.com")
    files = File(client)
    
    try:
        # This will likely cause authentication error
        files.get()
        
    except UnauthorizedException as e:
        print(f"Authentication failed: {e}")
        print(f"Status code: {e.status_code}")
        print("Action: Check your API key")
        
    except ForbiddenException as e:
        print(f"Insufficient permissions: {e}")
        print("Action: Contact administrator for proper access rights")
        
    except TooManyRequestsException as e:
        print(f"Rate limit exceeded: {e}")
        if e.retry_after:
            print(f"Retry after: {e.retry_after} seconds")
            time.sleep(e.retry_after)
        print("Action: Implement exponential backoff")
        
    except BadRequestException as e:
        print(f"Invalid request parameters: {e}")
        print("Action: Check API documentation for correct parameters")
        
    except NotFoundException as e:
        print(f"Resource not found: {e}")
        print("Action: Verify resource ID or endpoint URL")
        
    except InternalServerErrorException as e:
        print(f"Server error: {e}")
        print("Action: Retry after some time or contact support")
        
    except ServiceUnavailableException as e:
        print(f"Service temporarily unavailable: {e}")
        if e.retry_after:
            print(f"Retry after: {e.retry_after} seconds")
        print("Action: Implement retry with exponential backoff")
        
    except ClientError as e:
        # Catch-all for 4xx errors
        print(f"Client error (4xx): {e}")
        print(f"Status code: {e.status_code}")
        
    except ServerError as e:
        # Catch-all for 5xx errors
        print(f"Server error (5xx): {e}")
        print(f"Status code: {e.status_code}")


def demonstrate_file_upload_error_handling():
    """Demonstrate handling of file upload specific exceptions."""
    
    client = Client.create_client("your-api-key", "your-host.com")
    files = File(client)
    
    file_path = "path/to/large-video.mp4"
    
    try:
        result = files.upload(file_path, description="Large video upload")
        print(f"Upload successful: {result}")
        
    except FileTooLargeException as e:
        print(f"File too large: {e}")
        print(f"File size: {e.file_size} bytes")
        print(f"Max allowed: {e.max_size} bytes")
        print("Action: Compress file or split into smaller chunks")
        
    except UnsupportedFileTypeException as e:
        print(f"Unsupported file type: {e}")
        print(f"File type: {e.file_type}")
        if e.supported_types:
            print(f"Supported types: {', '.join(e.supported_types)}")
        print("Action: Convert to supported format")
        
    except FileUploadException as e:
        # Generic file upload error
        print(f"File upload failed: {e}")
        print(f"File path: {e.file_path}")
        print("Action: Check file permissions and network connection")
        
    except APIQuotaExceededException as e:
        print(f"API quota exceeded: {e}")
        print(f"Quota type: {e.quota_type}")
        print(f"Limit: {e.limit}")
        if e.reset_time:
            print(f"Resets at: {e.reset_time}")
        print("Action: Wait for quota reset or upgrade plan")


def demonstrate_job_error_handling():
    """Demonstrate handling of job processing exceptions."""
    
    client = Client.create_client("your-api-key", "your-host.com")
    jobs = Job(client)
    
    job_id = 12345  # Replace with actual job ID
    
    try:
        # Wait for job completion
        result = jobs.wait_for_completion(
            job_id=job_id, 
            timeout=300,  # 5 minutes
            poll_interval=2.0
        )
        print(f"Job completed successfully: {result}")
        
    except JobTimeoutException as e:
        print(f"Job timed out: {e}")
        print(f"Job ID: {e.job_id}")
        print(f"Timeout: {e.timeout} seconds")
        print("Action: Increase timeout or check job status manually")
        
        # Try to check job status
        try:
            status = jobs.get_status(job_id)
            print(f"Current job status: {status.status.value}")
            print(f"Progress: {status.progress}%")
        except Exception as status_ex:
            print(f"Could not get job status: {status_ex}")
            
    except JobFailedException as e:
        print(f"Job failed: {e}")
        print(f"Job ID: {e.job_id}")
        print(f"Error message: {e.error_message}")
        print("Action: Check job parameters and retry")
        
    except JobAbortedException as e:
        print(f"Job was aborted: {e}")
        print(f"Job ID: {e.job_id}")
        print("Action: Job was cancelled, restart if needed")
        
    except JobException as e:
        # Generic job error
        print(f"Job processing error: {e}")
        print(f"Job ID: {e.job_id}")
        print(f"Status: {e.job_status}")


def demonstrate_connection_error_handling():
    """Demonstrate handling of connection and network exceptions."""
    
    # Try connecting to invalid host
    try:
        client = Client.create_client("api-key", "invalid-host.example.com")
        files = File(client)
        files.get()
        
    except TimeoutException as e:
        print(f"Request timed out: {e}")
        print(f"Timeout: {e.timeout_seconds} seconds")
        print(f"Host: {e.host}")
        print("Action: Check network connection or increase timeout")
        
    except ConnectionException as e:
        print(f"Connection error: {e}")
        print(f"Host: {e.host}")
        print("Action: Check host URL and network connectivity")


def demonstrate_async_error_handling():
    """Demonstrate error handling in async operations."""
    
    import asyncio
    
    async def async_operation():
        client = Client.create_client("your-api-key", "your-host.com")
        files = File(client)
        
        try:
            # Async upload with job tracking
            result = await files.async_upload_and_wait(
                "path/to/file.jpg",
                timeout=60,
                description="Async upload test"
            )
            print(f"Async upload completed: {result}")
            
        except JobTimeoutException as e:
            print(f"Async job timed out: {e}")
            print(f"Job ID: {e.job_id}")
            
        except FileUploadException as e:
            print(f"Async upload failed: {e}")
            print(f"File: {e.file_path}")
            
        except PIXXIOException as e:
            # Catch all PIXXIO exceptions
            print(f"PIXXIO API error in async operation: {e}")
            if hasattr(e, 'status_code'):
                print(f"HTTP status: {e.status_code}")
    
    # Run async example
    try:
        asyncio.run(async_operation())
    except Exception as e:
        print(f"Async operation failed: {e}")


def demonstrate_error_recovery_patterns():
    """Demonstrate error recovery and retry patterns."""
    
    import random
    import time
    
    def retry_with_backoff(func, max_retries=3, base_delay=1.0):
        """Retry function with exponential backoff."""
        
        for attempt in range(max_retries):
            try:
                return func()
                
            except TooManyRequestsException as e:
                if e.retry_after:
                    print(f"Rate limited, waiting {e.retry_after}s...")
                    time.sleep(e.retry_after)
                else:
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    print(f"Rate limited, waiting {delay:.1f}s...")
                    time.sleep(delay)
                    
            except ServiceUnavailableException as e:
                if e.retry_after:
                    print(f"Service unavailable, waiting {e.retry_after}s...")
                    time.sleep(e.retry_after)
                else:
                    delay = base_delay * (2 ** attempt)
                    print(f"Service unavailable, waiting {delay}s...")
                    time.sleep(delay)
                    
            except (ConnectionException, TimeoutException) as e:
                delay = base_delay * (2 ** attempt)
                print(f"Connection error, retrying in {delay}s...")
                time.sleep(delay)
                
            except ServerError as e:
                if attempt == max_retries - 1:
                    raise  # Re-raise on final attempt
                delay = base_delay * (2 ** attempt)
                print(f"Server error, retrying in {delay}s...")
                time.sleep(delay)
                
            except ClientError as e:
                # Don't retry client errors (4xx)
                raise
                
            if attempt == max_retries - 1:
                raise Exception(f"Max retries ({max_retries}) exceeded")
    
    # Example usage
    client = Client.create_client("your-api-key", "your-host.com")
    files = File(client)
    
    def upload_operation():
        return files.upload("test-file.jpg", description="Test upload")
    
    try:
        result = retry_with_backoff(upload_operation, max_retries=3)
        print(f"Upload succeeded after retries: {result}")
        
    except PIXXIOException as e:
        print(f"Upload failed after all retries: {e}")


def demonstrate_comprehensive_error_logging():
    """Demonstrate comprehensive error logging for debugging."""
    
    import logging
    import traceback
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger('pixxio_client')
    
    client = Client.create_client("your-api-key", "your-host.com")
    files = File(client)
    
    try:
        result = files.upload("non-existent-file.jpg")
        
    except PIXXIOException as e:
        # Log comprehensive error details
        logger.error(f"PIXXIO API Error: {type(e).__name__}: {e}")
        
        if hasattr(e, 'status_code') and e.status_code:
            logger.error(f"HTTP Status Code: {e.status_code}")
            
        if hasattr(e, 'response') and e.response:
            logger.error(f"Response Headers: {dict(e.response.headers)}")
            
        if hasattr(e, 'response_object') and e.response_object:
            logger.error(f"Response Object: {e.response_object}")
            
        # Log full traceback for debugging
        logger.error(f"Full Traceback: {traceback.format_exc()}")
        
        # Log context-specific details
        if isinstance(e, FileUploadException):
            logger.error(f"File Path: {e.file_path}")
            logger.error(f"File Size: {e.file_size}")
            
        elif isinstance(e, JobException):
            logger.error(f"Job ID: {e.job_id}")
            logger.error(f"Job Status: {e.job_status}")
            
        elif isinstance(e, TooManyRequestsException):
            logger.error(f"Retry After: {e.retry_after}")


if __name__ == "__main__":
    print("=== Enhanced Error Handling Examples ===\\n")
    
    print("1. HTTP Status Code Error Handling")
    demonstrate_http_error_handling()
    print()
    
    print("2. File Upload Error Handling")
    demonstrate_file_upload_error_handling()
    print()
    
    print("3. Job Processing Error Handling")
    demonstrate_job_error_handling()
    print()
    
    print("4. Connection Error Handling")
    demonstrate_connection_error_handling()
    print()
    
    print("5. Async Error Handling")
    demonstrate_async_error_handling()
    print()
    
    print("6. Error Recovery Patterns")
    demonstrate_error_recovery_patterns()
    print()
    
    print("7. Comprehensive Error Logging")
    demonstrate_comprehensive_error_logging()
    
    print("\\n=== Examples completed ===")
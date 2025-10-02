# Async Operations Guide

This guide covers asynchronous operations and job tracking in the PIXXIO Python client library.

## Overview

The PIXXIO API supports long-running operations that return job IDs for tracking progress. The client library provides both synchronous and asynchronous interfaces for handling these operations.

## Job Tracking System

### How It Works

1. **Operation Starts**: Some API calls return a `jobID` instead of immediate results
2. **Job Monitoring**: The client polls the `/jobs/{id}` endpoint for status updates
3. **Completion Detection**: Polling continues until job reaches success/failure state
4. **Result Retrieval**: Final operation results are returned when job completes

### Job States

Jobs progress through these states:

```python
from pixxio_client.pixxio_types import JobStatus

JobStatus.PENDING      # Job queued, not yet started
JobStatus.RUNNING      # Job actively processing
JobStatus.SUCCESS      # Job completed successfully  
JobStatus.FAILED       # Job failed with error
JobStatus.CANCELLED    # Job was cancelled
```

## ResourceJobMixin

Resources that support job tracking inherit from `ResourceJobMixin`:

```python
class File(ResourceBase, ResourceJobMixin, ResourceUploadMixin):
    NAME = "files"
    
    # Inherits job tracking methods:
    # - post_and_wait()
    # - async_post_and_wait()
    # - _extract_job_id()
    # - _get_job_resource()
```

### Automatic Job Detection

The mixin automatically detects job IDs in responses:

```python
# These response formats are automatically detected:
response.jobID      # Primary format
response.jobId      # Alternative format  
response.job_id     # Snake case format
```

## Synchronous Job Tracking

### Basic Usage

```python
from pixxio_client import Client
from pixxio_client.files import File

client = Client.create_client("api-key", "company.pixxio.com")
files = File(client)

# Upload with automatic job tracking
result = files.post_and_wait(
    form_data={'title': 'My File'},
    files={'file': open('/path/to/file.pdf', 'rb')},
    timeout=600,        # 10 minutes max
    poll_interval=5.0   # Check every 5 seconds
)

print(f"Upload completed: {result.id}")
```

### File Upload with Job Tracking

```python
# Method 1: Using upload_and_wait (recommended for files)
result = files.upload_and_wait(
    "/path/to/large_video.mp4",
    timeout=1800,       # 30 minutes
    poll_interval=10.0, # Check every 10 seconds
    title="Product Demo",
    keywords="product,demo,video"
)

# Method 2: Using post_and_wait directly
with open("/path/to/file.pdf", "rb") as f:
    result = files.post_and_wait(
        form_data={'title': 'Document'},
        files={'file': f},
        timeout=300
    )
```

### Configuration Options

```python
result = files.post_and_wait(
    json_data={'operation': 'batch_convert'},
    timeout=1800,        # Maximum wait time (seconds)
    poll_interval=5.0,   # Time between status checks (seconds)
)
```

**Parameters:**
- `timeout`: Maximum time to wait for completion (default: 300 seconds)
- `poll_interval`: Time between status checks (default: 2.0 seconds)

## Asynchronous Job Tracking

### Basic Async Usage

```python
import asyncio
from pixxio_client import Client
from pixxio_client.files import File

async def async_upload():
    client = Client.create_client("api-key", "company.pixxio.com")
    files = File(client)
    
    # Async upload with job tracking
    result = await files.async_upload_and_wait(
        "/path/to/file.mp4",
        timeout=600,
        title="Async Upload"
    )
    
    return result

# Run the async operation
result = asyncio.run(async_upload())
```

### Concurrent Operations

```python
async def batch_upload():
    client = Client.create_client("api-key", "company.pixxio.com")
    files = File(client)
    
    file_paths = [
        "/path/to/file1.jpg",
        "/path/to/file2.pdf", 
        "/path/to/file3.mp4"
    ]
    
    # Upload all files concurrently
    tasks = [
        files.async_upload_and_wait(
            path,
            title=f"File {i+1}",
            timeout=900  # 15 minutes per file
        ) 
        for i, path in enumerate(file_paths)
    ]
    
    # Wait for all uploads to complete
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    successful = []
    failed = []
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            failed.append((file_paths[i], result))
        else:
            successful.append(result)
    
    return successful, failed

# Run batch upload
successful, failed = asyncio.run(batch_upload())
print(f"Successful: {len(successful)}, Failed: {len(failed)}")
```

### Async with Error Handling

```python
from pixxio_client.exceptions import JobTimeoutException, JobFailedException

async def robust_upload():
    files = File(client)
    
    try:
        result = await files.async_upload_and_wait(
            "/path/to/file.mov",
            timeout=1800,
            poll_interval=15.0,
            title="Large Video File"
        )
        return result
        
    except JobTimeoutException:
        print("Upload timed out - job may still be processing")
        # Optionally continue monitoring manually
        
    except JobFailedException as e:
        print(f"Upload failed: {e}")
        # Handle failure (retry, log, etc.)
        
    except FileNotFoundError:
        print("Source file not found")
        
    except Exception as e:
        print(f"Unexpected error: {e}")

result = asyncio.run(robust_upload())
```

## Manual Job Tracking

### Direct Job Management

```python
from pixxio_client.jobs import Job

jobs = Job(client)

# Start an operation that returns a job ID
response = files.post(json_data={'operation': 'convert'})
job_id = response.jobID

# Monitor job manually
job_info = jobs.wait_for_completion(
    job_id=job_id,
    timeout=600,
    poll_interval=5.0
)

print(f"Job status: {job_info.status}")
print(f"Job result: {job_info.result_data}")
```

### Async Manual Job Tracking

```python
# Async job monitoring
job_info = await jobs.async_wait_for_completion(
    job_id=job_id,
    timeout=600,
    poll_interval=5.0
)
```

### Job Status Checking

```python
# Check current job status
status = jobs.get_status(job_id)
print(f"Status: {status.status}")
print(f"Progress: {status.progress}%")

# Get detailed job information
job_detail = jobs.get(job_id)
print(f"Created: {job_detail.createdAt}")
print(f"Updated: {job_detail.updatedAt}")
```

## Advanced Patterns

### Custom Job Polling

```python
from pixxio_client.pixxio_types import JobStatus
import time

def custom_job_monitor(job_id: str, max_time: int = 300):
    """Custom job monitoring with progress reporting."""
    jobs = Job(client)
    start_time = time.time()
    
    while time.time() - start_time < max_time:
        status = jobs.get_status(job_id)
        
        print(f"Job {job_id}: {status.status} ({status.progress}%)")
        
        if status.status == JobStatus.SUCCESS:
            return jobs.get(job_id)
        elif status.status == JobStatus.FAILED:
            raise JobFailedException(f"Job failed: {status.error}")
            
        time.sleep(2.0)
    
    raise JobTimeoutException(f"Job did not complete in {max_time} seconds")

# Usage
job_result = custom_job_monitor("job123", max_time=600)
```

### Callback-Based Job Tracking

```python
from typing import Callable, Optional
from pixxio_client.pixxio_types import JobInfo

async def job_with_callback(
    job_id: str,
    progress_callback: Optional[Callable[[JobInfo], None]] = None,
    completion_callback: Optional[Callable[[JobInfo], None]] = None
):
    """Job tracking with progress and completion callbacks."""
    jobs = Job(client)
    
    try:
        async def monitor():
            while True:
                job_info = jobs.get(job_id)
                
                # Call progress callback if provided
                if progress_callback:
                    progress_callback(job_info)
                
                if job_info.status in [JobStatus.SUCCESS, JobStatus.FAILED]:
                    if completion_callback:
                        completion_callback(job_info)
                    return job_info
                
                await asyncio.sleep(2.0)
        
        return await monitor()
        
    except Exception as e:
        print(f"Job monitoring error: {e}")
        raise

# Usage with callbacks
def on_progress(job_info):
    print(f"Progress: {job_info.progress}%")

def on_completion(job_info):
    if job_info.status == JobStatus.SUCCESS:
        print("Job completed successfully!")
    else:
        print(f"Job failed: {job_info.error}")

result = await job_with_callback(
    "job123",
    progress_callback=on_progress,
    completion_callback=on_completion
)
```

## Best Practices

### 1. Choose Appropriate Timeouts

```python
# File size based timeouts
small_file_timeout = 60     # 1 minute for images/documents
medium_file_timeout = 300   # 5 minutes for larger files  
large_file_timeout = 1800   # 30 minutes for videos

# Operation based timeouts
conversion_timeout = 600    # 10 minutes for format conversion
batch_timeout = 3600       # 1 hour for batch operations
```

### 2. Use Appropriate Poll Intervals

```python
# Balance between responsiveness and API load
quick_poll = 1.0      # For operations expected to complete quickly
normal_poll = 5.0     # For typical file processing
slow_poll = 30.0      # For very long operations
```

### 3. Handle Exceptions Gracefully

```python
from pixxio_client.exceptions import (
    JobTimeoutException, 
    JobFailedException,
    PIXXIOException
)

try:
    result = files.upload_and_wait(file_path, timeout=600)
except JobTimeoutException:
    # Job may still be processing - decide whether to continue waiting
    print("Upload timed out, but may still complete")
except JobFailedException as e:
    # Job definitively failed - handle error
    print(f"Upload failed: {e}")
except FileNotFoundError:
    # Local file issue
    print("Source file not found")
except PIXXIOException as e:
    # API or network issue
    print(f"API error: {e}")
```

### 4. Use Async for Multiple Operations

```python
# Good: Concurrent uploads
tasks = [files.async_upload_and_wait(path) for path in file_paths]
results = await asyncio.gather(*tasks)

# Avoid: Sequential uploads
for path in file_paths:
    result = files.upload_and_wait(path)  # Blocks each upload
```

### 5. Monitor Resource Usage

```python
import psutil
import asyncio

async def resource_aware_upload():
    # Check system resources before starting
    memory_percent = psutil.virtual_memory().percent
    cpu_percent = psutil.cpu_percent(interval=1)
    
    if memory_percent > 80 or cpu_percent > 80:
        print("System under load, using longer poll interval")
        poll_interval = 10.0
    else:
        poll_interval = 2.0
    
    return await files.async_upload_and_wait(
        file_path,
        poll_interval=poll_interval
    )
```

## Troubleshooting

### Common Issues

**1. Job Timeout Errors**
```python
# Increase timeout for large files
result = files.upload_and_wait(
    large_file_path,
    timeout=3600  # 1 hour instead of default 5 minutes
)
```

**2. Too Frequent API Calls**
```python
# Increase poll interval to reduce API load
result = files.upload_and_wait(
    file_path,
    poll_interval=10.0  # Check every 10 seconds instead of 2
)
```

**3. Network Interruptions**
```python
# Add retry logic
import time

def upload_with_retry(file_path, max_retries=3):
    for attempt in range(max_retries):
        try:
            return files.upload_and_wait(file_path, timeout=900)
        except (ConnectionError, TimeoutError) as e:
            if attempt == max_retries - 1:
                raise
            print(f"Attempt {attempt + 1} failed, retrying in 30 seconds...")
            time.sleep(30)
```

### Debugging Job Issues

```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Monitor job progression
job_id = "job123"
jobs = Job(client)

for i in range(10):  # Check 10 times
    status = jobs.get(job_id)
    print(f"Check {i+1}: {status.status} - {status.progress}%")
    if hasattr(status, 'message'):
        print(f"  Message: {status.message}")
    time.sleep(5)
```

---

For more information, see:
- [API Reference](../API_REFERENCE.md) - Complete API documentation
- [Error Handling](ERROR_HANDLING.md) - Exception handling patterns
- [Developer Guide](DEVELOPER_GUIDE.md) - Architecture and contribution guidelines
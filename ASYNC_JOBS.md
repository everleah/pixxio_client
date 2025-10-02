# PIXXIO Async Job Tracking

This documentation covers the async job tracking capabilities added to the PIXXIO client library for managing long-running operations.

## Overview

Many PIXXIO operations (file uploads, conversions, batch operations) are asynchronous and return a `jobID` instead of immediate results. The enhanced client library now provides comprehensive job tracking with both synchronous and asynchronous support.

## Key Features

- ✅ **Job Status Monitoring** - Track job progress with real-time status updates
- ✅ **Automatic Job Tracking** - Built-in wait-for-completion methods 
- ✅ **Async/Await Support** - Non-blocking async operations with `asyncio`
- ✅ **Progress Callbacks** - Custom functions called on status updates
- ✅ **Timeout Handling** - Configurable timeouts with proper error handling
- ✅ **Job Abortion** - Cancel running jobs when needed
- ✅ **Type Safety** - Full type hints for better IDE support

## Job Status Enumeration

```python
from pixxio_client.pixxio_types import JobStatus

class JobStatus(Enum):
    PENDING = "pending"     # Job queued but not started
    RUNNING = "running"     # Job currently processing  
    COMPLETED = "completed" # Job finished successfully
    FAILED = "failed"       # Job encountered an error
    ABORTED = "aborted"     # Job was cancelled
```

## Job Information Structure

```python
from pixxio_client.pixxio_types import JobInfo

@dataclass
class JobInfo:
    id: PIXXIOId                    # Job ID
    status: JobStatus               # Current status
    progress: Optional[int]         # Progress percentage (0-100)
    message: Optional[str]          # Status/error message
    created_date: Optional[str]     # When job was created
    completed_date: Optional[str]   # When job finished
    result_data: Optional[Any]      # Final result data
```

## Basic Usage

### 1. Simple File Upload with Job Tracking

```python
from pixxio_client import Client
from pixxio_client.files import File

# Create client
client = Client.create_client("your-api-key", "your-host.com")
files = File(client)

# Upload and wait for completion automatically
try:
    result = files.upload_and_wait(
        "large-file.jpg",
        timeout=300,           # Wait up to 5 minutes  
        poll_interval=2.0,     # Check status every 2 seconds
        description="My upload"
    )
    print(f"Upload completed! File ID: {result.id}")
    
except TimeoutError:
    print("Upload timed out")
except Exception as e:
    print(f"Upload failed: {e}")
```

### 2. Manual Job Tracking with Progress Callbacks

```python
from pixxio_client.jobs import Job
from pixxio_client.pixxio_types import JobInfo

def progress_callback(job_info: JobInfo):
    print(f"Job {job_info.id}: {job_info.status.value}")
    if job_info.progress:
        print(f"  Progress: {job_info.progress}%")

# Start operation that returns job ID
response = files.post(
    form_data={"description": "Test"},
    files={"file": open("file.jpg", "rb")}
)

job_id = getattr(response, 'jobID', None)
if job_id:
    jobs = Job(client)
    final_result = jobs.wait_for_completion(
        job_id=job_id,
        timeout=300,
        callback=progress_callback  # Called on each status update
    )
    print(f"Job completed: {final_result.status}")
```

### 3. Async Operations with asyncio

```python
import asyncio
from pixxio_client.files import File

async def async_upload_example():
    client = Client.create_client("your-api-key", "your-host.com")
    files = File(client)
    
    # Async upload with automatic job tracking
    result = await files.async_upload_and_wait(
        "large-file.jpg",
        timeout=600,
        poll_interval=1.0,
        description="Async upload"
    )
    print(f"Async upload completed: {result.id}")

# Run async function
asyncio.run(async_upload_example())
```

### 4. Async Progress Callbacks

```python
async def async_progress_callback(job_info: JobInfo):
    print(f"[ASYNC] Job {job_info.id}: {job_info.status.value}")
    
    # You can add async operations here:
    # await send_notification(job_info)
    # await update_database(job_info)

async def manual_async_tracking():
    jobs = Job(client)
    
    final_result = await jobs.async_wait_for_completion(
        job_id=12345,
        timeout=300,
        callback=async_progress_callback
    )
    print("Async job completed!")
```

## Advanced Usage

### Job Status Checking

```python
from pixxio_client.jobs import Job
from pixxio_client.pixxio_types import JobStatus

jobs = Job(client)

# Get current job status
job_info = jobs.get_status(job_id=12345)

print(f"Status: {job_info.status.value}")
print(f"Progress: {job_info.progress}%") 
print(f"Message: {job_info.message}")

# Check if job is complete
if job_info.status == JobStatus.COMPLETED:
    print("Job finished successfully!")
    result_data = job_info.result_data
    
elif job_info.status == JobStatus.FAILED:
    print(f"Job failed: {job_info.message}")
```

### Job Abortion

```python
jobs = Job(client)

# Check if job is running
job_info = jobs.get_status(job_id=12345)

if job_info.status in [JobStatus.PENDING, JobStatus.RUNNING]:
    # Abort the job
    jobs.abort(job_id=12345)
    print("Job abortion requested")
    
    # Verify abortion
    import time
    time.sleep(2)
    updated_info = jobs.get_status(job_id=12345) 
    print(f"New status: {updated_info.status.value}")
```

### Custom Post Operations with Job Tracking

```python
# Any resource that inherits from ResourceJobMixin can use job tracking
files = File(client)  # Inherits ResourceJobMixin

# Generic post operation with automatic job tracking
result = files.post_and_wait(
    timeout=300,
    poll_interval=2.0,
    json_data={"description": "Batch operation"},
    # ... other POST parameters
)

# Async version
result = await files.async_post_and_wait(
    timeout=300,
    poll_interval=1.0, 
    form_data={"category": "processed"}
)
```

## Error Handling

The job tracking system provides comprehensive error handling:

```python
try:
    result = files.upload_and_wait("file.jpg", timeout=60)
    
except TimeoutError:
    print("Operation timed out - job may still be running")
    
except Exception as e:
    if "failed" in str(e):
        print(f"Job failed during processing: {e}")
    elif "aborted" in str(e):
        print(f"Job was cancelled: {e}")  
    else:
        print(f"Unexpected error: {e}")
```

## Configuration Options

### Timeout Settings

```python
# Short timeout for quick operations
result = files.upload_and_wait("small-file.jpg", timeout=30)

# Long timeout for large files/complex processing
result = files.upload_and_wait("huge-file.mp4", timeout=1800)  # 30 minutes

# No timeout (wait indefinitely)
result = files.upload_and_wait("file.jpg", timeout=0)
```

### Polling Intervals

```python
# Fast polling for quick feedback (more API calls)
result = files.upload_and_wait("file.jpg", poll_interval=0.5)

# Slow polling for long operations (fewer API calls)  
result = files.upload_and_wait("file.jpg", poll_interval=10.0)

# Adaptive polling based on operation type
if file_size > 100_000_000:  # > 100MB
    poll_interval = 5.0
else:
    poll_interval = 1.0
```

## Integration with Existing Code

The async job tracking is designed to be backwards compatible:

```python
# Existing code still works unchanged
files = File(client)
response = files.post(form_data={"description": "test"})

# New code can add job tracking without breaking existing functionality  
response = files.post_and_wait(form_data={"description": "test"})
```

## Performance Considerations

- **Polling Frequency**: Lower poll intervals = more responsive but more API calls
- **Timeout Values**: Set reasonable timeouts based on expected operation duration
- **Async Usage**: Use async methods for better concurrency in async applications
- **Callback Functions**: Keep callback functions lightweight to avoid blocking status checks

## API Reference

### Job Class Methods

- `get_status(job_id)` → `JobInfo` - Get current job status
- `abort(job_id)` → `ResponseData` - Cancel a running job  
- `wait_for_completion(job_id, timeout, poll_interval, callback)` → `JobInfo`
- `async_wait_for_completion(job_id, timeout, poll_interval, callback)` → `JobInfo`

### ResourceJobMixin Methods

- `post_and_wait(timeout, poll_interval, **post_params)` → `ResponseData`
- `async_post_and_wait(timeout, poll_interval, **post_params)` → `ResponseData`

### File Class Async Methods

- `upload_and_wait(file_path, timeout, poll_interval, **form_data)` → `ResponseData`
- `async_upload_and_wait(file_path, timeout, poll_interval, **form_data)` → `ResponseData`

This async job tracking system provides a robust foundation for handling PIXXIO's long-running operations with proper error handling, progress monitoring, and both sync/async support.
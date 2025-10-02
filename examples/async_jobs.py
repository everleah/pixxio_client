"""
PIXXIO Async Job Tracking Examples

This file demonstrates how to use the new async job tracking capabilities
in the PIXXIO client library for long-running operations.
"""

import asyncio
from typing import Optional

from pixxio_client import Client, Authentication
from pixxio_client.files import File
from pixxio_client.jobs import Job
from pixxio_client.pixxio_types import JobInfo, JobStatus


def progress_callback(job_info: JobInfo) -> None:
    """Callback function to track job progress."""
    print(f"Job {job_info.id}: {job_info.status.value}")
    if job_info.progress is not None:
        print(f"  Progress: {job_info.progress}%")
    if job_info.message:
        print(f"  Message: {job_info.message}")


async def async_progress_callback(job_info: JobInfo) -> None:
    """Async callback function to track job progress."""
    print(f"[ASYNC] Job {job_info.id}: {job_info.status.value}")
    if job_info.progress is not None:
        print(f"  Progress: {job_info.progress}%")
    if job_info.message:
        print(f"  Message: {job_info.message}")
    
    # You could add async operations here like:
    # await send_notification_to_user(job_info)
    # await update_database(job_info)


def sync_job_tracking_example():
    """Example of synchronous job tracking."""
    
    # Create client
    client = Client.create_client("your-api-key", "your-host.com")
    
    # Upload file and wait for completion
    files = File(client)
    
    try:
        # Method 1: Upload with automatic job tracking
        print("Uploading file with automatic job tracking...")
        result = files.upload_and_wait(
            "path/to/large-file.jpg",
            timeout=600,  # 10 minutes
            poll_interval=3.0,  # Check every 3 seconds
            description="Large file upload with job tracking",
            category="test"
        )
        print("Upload completed successfully!")
        print(f"File ID: {getattr(result, 'id', 'N/A')}")
        
    except TimeoutError:
        print("Upload timed out")
    except Exception as e:
        print(f"Upload failed: {e}")


def manual_job_tracking_example():
    """Example of manual job tracking with callbacks."""
    
    client = Client.create_client("your-api-key", "your-host.com")
    
    # Start an operation that returns a job ID
    files = File(client)
    response = files.post(
        form_data={"description": "Test upload"},
        files={"file": open("path/to/file.jpg", "rb")}
    )
    
    # Check if we got a job ID
    job_id = getattr(response, 'jobID', None)
    if job_id:
        print(f"Started job {job_id}, tracking progress...")
        
        # Track job manually with progress callback
        jobs = Job(client)
        try:
            final_result = jobs.wait_for_completion(
                job_id=job_id,
                timeout=300,
                poll_interval=2.0,
                callback=progress_callback  # Called on each status update
            )
            print("Job completed successfully!")
            print(f"Final status: {final_result.status.value}")
            
        except Exception as e:
            print(f"Job failed: {e}")
    else:
        print("Operation completed immediately (no job tracking needed)")


async def async_job_tracking_example():
    """Example of async job tracking."""
    
    client = Client.create_client("your-api-key", "your-host.com") 
    files = File(client)
    
    try:
        print("Starting async upload with job tracking...")
        
        # Method 1: Async upload with automatic job tracking
        result = await files.async_upload_and_wait(
            "path/to/large-file.jpg", 
            timeout=600,
            poll_interval=2.0,
            description="Async upload with job tracking"
        )
        print("Async upload completed!")
        
        # Method 2: Manual async job tracking 
        response = files.post(
            form_data={"description": "Another test"},
            files={"file": open("path/to/another-file.jpg", "rb")}
        )
        
        job_id = getattr(response, 'jobID', None)
        if job_id:
            jobs = Job(client)
            final_result = await jobs.async_wait_for_completion(
                job_id=job_id,
                timeout=300,
                poll_interval=1.5, 
                callback=async_progress_callback
            )
            print(f"Async job {job_id} completed: {final_result.status.value}")
            
    except Exception as e:
        print(f"Async operation failed: {e}")


def job_status_monitoring_example():
    """Example of checking job status without waiting."""
    
    client = Client.create_client("your-api-key", "your-host.com")
    jobs = Job(client)
    
    # Get current status of a specific job
    job_id = 12345  # Replace with actual job ID
    
    try:
        job_info = jobs.get_status(job_id)
        
        print(f"Job {job_id} Status: {job_info.status.value}")
        print(f"Progress: {job_info.progress}%")
        print(f"Message: {job_info.message}")
        print(f"Created: {job_info.created_date}")
        
        if job_info.status == JobStatus.COMPLETED:
            print("Job is completed!")
            if job_info.result_data:
                print(f"Result: {job_info.result_data}")
                
        elif job_info.status == JobStatus.FAILED:
            print(f"Job failed: {job_info.message}")
            
        elif job_info.status in [JobStatus.PENDING, JobStatus.RUNNING]:
            print("Job is still processing...")
            
    except Exception as e:
        print(f"Could not get job status: {e}")


def job_abortion_example():
    """Example of aborting a running job."""
    
    client = Client.create_client("your-api-key", "your-host.com")
    jobs = Job(client)
    
    job_id = 12345  # Replace with actual job ID
    
    try:
        # Check current status
        job_info = jobs.get_status(job_id)
        
        if job_info.status in [JobStatus.PENDING, JobStatus.RUNNING]:
            print(f"Aborting job {job_id}...")
            result = jobs.abort(job_id)
            print("Job abortion requested")
            
            # Wait a bit and check if it was actually aborted
            import time
            time.sleep(2)
            
            updated_info = jobs.get_status(job_id)
            print(f"Job status after abortion: {updated_info.status.value}")
            
        else:
            print(f"Job {job_id} is not running (status: {job_info.status.value})")
            
    except Exception as e:
        print(f"Could not abort job: {e}")


if __name__ == "__main__":
    print("=== PIXXIO Async Job Tracking Examples ===\\n")
    
    # Run synchronous examples
    print("1. Sync Job Tracking Example")
    sync_job_tracking_example()
    print()
    
    print("2. Manual Job Tracking Example") 
    manual_job_tracking_example()
    print()
    
    print("3. Job Status Monitoring Example")
    job_status_monitoring_example()
    print()
    
    print("4. Job Abortion Example")
    job_abortion_example()
    print()
    
    # Run async example
    print("5. Async Job Tracking Example")
    asyncio.run(async_job_tracking_example())
    
    print("\\n=== Examples completed ===")
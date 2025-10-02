import time
import asyncio
from typing import Any, Optional, Union

from ._base import ReadOnlyResourceBase
from .exceptions import (
    get_response_exception, JobTimeoutException, 
    JobFailedException, JobAbortedException
)
from .pixxio_types import (
    PIXXIOId, ResponseData, JobStatus, JobInfo, 
    JobCallback, AsyncJobCallback
)


class Job(ReadOnlyResourceBase):
    """Job resource for managing asynchronous operations in PIXXIO."""
    
    NAME = "jobs"
    
    def abort(self, id: PIXXIOId, **params: Any) -> ResponseData:
        """Abort a running job by ID."""
        try:
            response = self.client.session.put(
                f"{self.client.location_base}/jobAbort/{id}",
                params=params
            )
        except Exception as ex:
            raise get_response_exception(ex)
        return self._parseResponse(response)
    
    def get_status(self, job_id: PIXXIOId) -> JobInfo:
        """Get current status of a job."""
        response = self.get(id=job_id)
        return self._parse_job_response(job_id, response)
    
    def _parse_job_response(self, job_id: PIXXIOId, response: ResponseData) -> JobInfo:
        """Parse API response into JobInfo object."""
        if hasattr(response, 'status'):
            status_str = getattr(response, 'status', 'pending') or 'pending'
            try:
                status = JobStatus(status_str.lower())
            except (ValueError, AttributeError):
                status = JobStatus.PENDING
        else:
            status = JobStatus.PENDING
            
        return JobInfo(
            id=job_id,
            status=status,
            progress=getattr(response, 'progress', None),
            message=getattr(response, 'message', None),
            created_date=getattr(response, 'createDate', None),
            completed_date=getattr(response, 'completedDate', None),
            result_data=getattr(response, 'result', None)
        )
    
    def wait_for_completion(
        self, 
        job_id: PIXXIOId, 
        timeout: int = 300, 
        poll_interval: float = 2.0,
        callback: Optional[JobCallback] = None
    ) -> JobInfo:
        """Wait for job completion with optional callback for progress updates.
        
        Args:
            job_id: The job ID to monitor
            timeout: Maximum time to wait in seconds (default: 300)
            poll_interval: Time between status checks in seconds (default: 2.0)
            callback: Optional callback function called on each status update
            
        Returns:
            Final JobInfo when job completes
            
        Raises:
            JobTimeoutException: If job doesn't complete within timeout
            JobFailedException: If job fails during processing
            JobAbortedException: If job was cancelled/aborted
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            job_info = self.get_status(job_id)
            
            if callback:
                callback(job_info)
                
            if job_info.status == JobStatus.COMPLETED:
                return job_info
            elif job_info.status == JobStatus.FAILED:
                raise JobFailedException(job_id, job_info.message)
            elif job_info.status == JobStatus.ABORTED:
                raise JobAbortedException(job_id)
                
            time.sleep(poll_interval)
            
        raise JobTimeoutException(job_id, timeout)
    
    async def async_wait_for_completion(
        self,
        job_id: PIXXIOId,
        timeout: int = 300,
        poll_interval: float = 2.0,
        callback: Optional[AsyncJobCallback] = None
    ) -> JobInfo:
        """Async version of wait_for_completion.
        
        Args:
            job_id: The job ID to monitor  
            timeout: Maximum time to wait in seconds (default: 300)
            poll_interval: Time between status checks in seconds (default: 2.0)
            callback: Optional async callback function called on each status update
            
        Returns:
            Final JobInfo when job completes
            
        Raises:
            JobTimeoutException: If job doesn't complete within timeout
            JobFailedException: If job fails during processing
            JobAbortedException: If job was cancelled/aborted
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            job_info = self.get_status(job_id)
            
            if callback:
                await callback(job_info)
                
            if job_info.status == JobStatus.COMPLETED:
                return job_info
            elif job_info.status == JobStatus.FAILED:
                raise JobFailedException(job_id, job_info.message)
            elif job_info.status == JobStatus.ABORTED:
                raise JobAbortedException(job_id)
                
            await asyncio.sleep(poll_interval)
            
        raise JobTimeoutException(job_id, timeout)
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
        callback: Optional[JobCallback] = None,
        response_fields: Optional[list[str]] = None
    ) -> ResponseData:
        """
        Wait for job completion using isFinished field in job object.
        When finished, fetch job data again with requested response fields.
        """
        start_time = time.time()
        job_obj = None
        if response_fields is None:
            response_fields = ["id", "jobType", "jobData", "isFinished", "success", "error"]
        while time.time() - start_time < timeout:
            job_response = self.get(job_id)
            job_obj = getattr(job_response, "job", job_response)
            is_finished = getattr(job_obj, "isFinished", False)
            if callback:
                callback(job_obj)
            if is_finished:
                # Fetch job data again with responseFields if provided, else use defaults
                params = {}
                for field in response_fields:
                    params.setdefault("responseFields", []).append(field)
                job_response = self.get(job_id, **params)
                full_job_obj = getattr(job_response, "job", job_obj)
                return full_job_obj
            time.sleep(poll_interval)
        raise JobTimeoutException(job_id, timeout)
    
    async def async_wait_for_completion(
        self,
        job_id: PIXXIOId,
        timeout: int = 300,
        poll_interval: float = 2.0,
        callback: Optional[AsyncJobCallback] = None
    ) -> ResponseData:
        """Async version: wait for job completion using isFinished field."""
        start_time = time.time()
        job_obj = None
        while time.time() - start_time < timeout:
            job_response = self.get(job_id)
            job_obj = getattr(job_response, "job", job_response)
            is_finished = getattr(job_obj, "isFinished", False)
            if callback:
                await callback(job_obj)
            if is_finished:
                return job_obj
            await asyncio.sleep(poll_interval)
        raise JobTimeoutException(job_id, timeout)
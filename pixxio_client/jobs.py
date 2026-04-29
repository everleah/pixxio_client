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
    """
    Resource for tracking and controlling asynchronous jobs in PIXXIO.

    Many PIXXIO API operations (e.g. file conversion, bulk updates) are
    handled asynchronously.  The API returns a ``jobID`` immediately and
    processes the work in the background.  Use this resource to poll the
    job status, wait for completion, or abort a running job.

    API endpoint: ``/api/v1/jobs``

    Available operations:
        - ``get()``                        – list all jobs
        - ``get(id)``                      – retrieve a specific job by ID
        - ``abort(id)``                    – abort a running job
        - ``get_status(job_id)``           – return current :class:`JobInfo`
        - ``wait_for_completion(job_id)``  – block until the job finishes
        - ``async_wait_for_completion(job_id)`` – async variant of the above

    Example::

        from pixxio_client import Client
        from pixxio_client.jobs import Job

        client = Client.create_client("api-key", "company.pixxio.com")
        jobs = Job(client)

        # Poll once
        info = jobs.get_status(job_id=42)
        print(info.status, info.progress)

        # Block until done (raises JobTimeoutException after 300 s)
        result = jobs.wait_for_completion(42)

        # Abort a running job
        jobs.abort(42)

    Response field filtering::

        jobs.set_response_fields(["id", "jobType", "isFinished", "success"])
        result = jobs.get()  # only returns the specified fields

    Note:
        :meth:`wait_for_completion` accepts a ``response_fields`` argument
        that is applied to the *final* fetch once the job has finished.
    """

    NAME = "jobs"

    def abort(self, id: PIXXIOId, **params: Any) -> ResponseData:
        """
        Abort a running job.

        Sends a PUT request to ``/api/v1/jobAbort/{id}`` to signal that the
        job should be stopped.  The job will transition to an aborted state;
        partially completed work may or may not be rolled back depending on
        the job type.

        Args:
            id: ID of the job to abort.
            **params: Additional query parameters forwarded to the API.

        Returns:
            ResponseData: API response confirming the abort request.

        Raises:
            PIXXIOException: If the API call fails.

        Example::

            jobs.abort(42)
        """
        try:
            response = self.client.session.put(
                f"{self.client.location_base}/jobAbort/{id}",
                params=params
            )
        except Exception as ex:
            raise get_response_exception(ex)
        return self._parseResponse(response)

    def get_status(self, job_id: PIXXIOId) -> JobInfo:
        """
        Return the current status of a job as a :class:`JobInfo` object.

        Fetches the job record from the API and converts it into a structured
        :class:`~pixxio_client.pixxio_types.JobInfo` object that exposes
        :attr:`status`, :attr:`progress`, :attr:`message`, and other fields
        in a consistent format.

        Args:
            job_id: ID of the job to inspect.

        Returns:
            JobInfo: Structured job status object.

        Example::

            info = jobs.get_status(42)
            print(info.status)    # e.g. JobStatus.PENDING
            print(info.progress)  # e.g. 0.45
        """
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
        Wait (blocking) until a job finishes, then return the final job object.

        Polls the job endpoint every ``poll_interval`` seconds.  When the job
        reports ``isFinished = True`` the job record is fetched once more with
        the requested ``response_fields`` and returned.

        Args:
            job_id: ID of the job to wait for.
            timeout: Maximum number of seconds to wait before raising
                :class:`~pixxio_client.exceptions.JobTimeoutException`.
                Defaults to ``300``.
            poll_interval: Number of seconds between polling requests.
                Defaults to ``2.0``.
            callback: Optional callable that receives the current job object
                after each poll.  Signature: ``callback(job_obj) -> None``.
            response_fields: List of field names to include in the final
                response.  Defaults to
                ``["id", "jobType", "jobData", "isFinished", "success", "error"]``.

        Returns:
            ResponseData: The final job object with the requested fields.

        Raises:
            JobTimeoutException: If the job does not finish within ``timeout``
                seconds.

        Example::

            def on_progress(job):
                print("Progress:", job.progress)

            result = jobs.wait_for_completion(
                job_id=42,
                timeout=120,
                poll_interval=5.0,
                callback=on_progress,
                response_fields=["id", "jobData", "success"],
            )
            print(result.success)
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
                callback(job_obj) # type: ignore
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
        """
        Asynchronously wait until a job finishes, then return the job object.

        Async counterpart of :meth:`wait_for_completion`.  Polls the job
        endpoint every ``poll_interval`` seconds using ``asyncio.sleep`` so
        the event loop is not blocked between polls.

        Args:
            job_id: ID of the job to wait for.
            timeout: Maximum number of seconds to wait before raising
                :class:`~pixxio_client.exceptions.JobTimeoutException`.
                Defaults to ``300``.
            poll_interval: Number of seconds between polling requests.
                Defaults to ``2.0``.
            callback: Optional async callable invoked after each poll.
                Signature: ``async callback(job_obj) -> None``.

        Returns:
            ResponseData: The final job object when ``isFinished`` is ``True``.

        Raises:
            JobTimeoutException: If the job does not finish within ``timeout``
                seconds.

        Example::

            import asyncio

            async def run():
                result = await jobs.async_wait_for_completion(42, timeout=60)
                print(result.success)

            asyncio.run(run())
        """
        start_time = time.time()
        job_obj = None
        while time.time() - start_time < timeout:
            job_response = self.get(job_id)
            job_obj = getattr(job_response, "job", job_response)
            is_finished = getattr(job_obj, "isFinished", False)
            if callback:
                await callback(job_obj) # type: ignore
            if is_finished:
                return job_obj
            await asyncio.sleep(poll_interval)
        raise JobTimeoutException(job_id, timeout)
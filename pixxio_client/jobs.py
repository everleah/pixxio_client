from typing import Any

from ._base import ReadOnlyResourceBase
from .exceptions import get_response_exception
from .pixxio_types import PIXXIOId, ResponseData


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
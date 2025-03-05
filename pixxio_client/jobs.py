from ._base import ReadOnlyResourceBase
from exceptions import get_response_exception

class Job(ReadOnlyResourceBase):
    NAME = "jobs"
    
    def abort(self, id, **params):
        try:
            response = self.client.session.put(
                f"{self.client.location_base}/jobAbort/{id}",
                params = params
            )
        except Exception as ex:
            raise get_response_exception(ex)
        return self._parseResponse(response)
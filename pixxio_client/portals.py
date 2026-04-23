
from ._base import ReadOnlyResourceBase

class Portal(ReadOnlyResourceBase):
    NAME = "portals"
    
class PortalPage(Portal):
    
    def get(self, id, **params):
        with self._without_response_fields():
            return self._get(
                endpoint_base=f"{self.endpoint_base}/{id}/pages",
                **params)

class PortalUser(Portal):
    
    def get(self, id, user_id=None, **params):
        with self._without_response_fields():
            if user_id is None:
                return self._get(
                    endpoint_base=f"{self.endpoint_base}/{id}/users/current",
                    **params)
            return self._get(
                endpoint_base=f"{self.endpoint_base}/{id}/users/{user_id}",
                **params)
        
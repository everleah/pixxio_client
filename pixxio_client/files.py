from ._base import ResourceBase

class File(ResourceBase):
    
    NAME = "files"
    
    def download(self, id=None, **params):
        if id is None:
            self._get(
                endpoint_base=f"{self.endpoint_base}/convert", 
                **params)
        return self._get(
            endpoint_base=f"{self.endpoint_base}/{id}/convert", 
            **params)
    
    def post(self):
        return # todo upload
    
    
    
    
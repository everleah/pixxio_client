from ._base import ResourceBase

class Keyword(ResourceBase):
    NAME = "keywords"
    
    def put(self, **params):
        raise NotImplementedError("not available in api")
    
    def post(self, **params):
        raise NotImplementedError("not available in api")
    
    def download(self, **params):
        return self._get(
            endpoint_base=f"{self.endpoint_base}/csv", 
            **params)
        
    def upload(self, **params):
        return # todo
    
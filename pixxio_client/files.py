from ._base import ResourceBase, ResourceUploadMixin

class File(ResourceBase, ResourceUploadMixin):
    
    NAME = "files"
    
    def download(self, id=None, **params):
        if id is None:
            return self._get(
                endpoint_base=f"{self.endpoint_base}/convert", 
                **params)
        return self._get(
            endpoint_base=f"{self.endpoint_base}/{id}/convert", 
            **params)

        
    
    
    
    
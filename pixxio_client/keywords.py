from ._base import ResourceBase, ResourceUploadMixin

class Keyword(ResourceBase, ResourceUploadMixin):
    NAME = "keywords"
    
    def put(self, **params):
        raise NotImplementedError("not available in api")
    
    def post(self, json_data = None, form_data=None, files=None, **params):
        return self._post(
            endpoint_base=f"{self.endpoint_base}/csv",
            json_data = json_data,
            form_data = form_data,
            files = files,
            **params)
    
    def download(self, **params):
        return self._get(
            endpoint_base=f"{self.endpoint_base}/csv", 
            **params)
    
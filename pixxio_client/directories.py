from ._base import ResourceBase

class Directory(ResourceBase):
    NAME = "directories"
    
    def get_tree(self, **params):
        return self._get(
            endpoint_base=f"{self.endpoint_base}/tree", 
            **params)
from ._base import ReadOnlyResourceBase

class CustomMetadata(ReadOnlyResourceBase):
    NAME = "metadata/custom"
    
class ImportantMetadata(ReadOnlyResourceBase):
    NAME = "metadata/important"
    
class InternalMetadata(ReadOnlyResourceBase):
    NAME = "metadata/internal"
    
class StandardMetadata(ReadOnlyResourceBase):
    NAME = "metadata/standard"
       
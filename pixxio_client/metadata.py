from ._base import ReadOnlyResourceBase

class CustomMetadata(ReadOnlyResourceBase):
    _paged: bool = False
    NAME = "metadata/custom"
    
class ImportantMetadata(ReadOnlyResourceBase):
    _paged: bool = False
    NAME = "metadata/important"
    
class InternalMetadata(ReadOnlyResourceBase):
    _paged: bool = False
    NAME = "metadata/internal"
    
class StandardMetadata(ReadOnlyResourceBase):
    _paged: bool = False
    NAME = "metadata/standard"
       
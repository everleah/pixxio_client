from ._base import ResourceBase, ReadOnlyResourceBase

class CustomMetadata(ResourceBase):
    _paged: bool = True
    NAME = "metadata/custom"

class ImportantMetadata(ReadOnlyResourceBase):
    _paged: bool = False
    NAME = "metadata/important"

class InternalMetadata(ReadOnlyResourceBase):
    _paged: bool = False
    NAME = "metadata/internal"

class StandardMetadata(ResourceBase):
    _paged: bool = False
    NAME = "metadata/standard"
       
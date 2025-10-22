from datetime import datetime, date
from typing import List, Optional, Literal
from types import SimpleNamespace
from ._base import ResourceBase, ReadOnlyResourceBase

class CustomMetadata(ResourceBase):
    _paged: bool = True
    _response_field_filter = [ "id", "createDate", "modifyDate", "name", "editType", "selectionOptions", "translationState"]
    NAME = "metadata/custom"

class ImportantMetadata(ReadOnlyResourceBase):
    _paged: bool = False
    _response_field_filter = [ "id", "createDate", "modifyDate", "metadata", "isSearchable", "isEditable"]
    NAME = "metadata/important"

class InternalMetadata(ReadOnlyResourceBase):
    _paged: bool = False
    _response_field_filter = []
    NAME = "metadata/internal"

class StandardMetadata(ResourceBase):
    _paged: bool = False
    _response_field_filter = []  # API does not support response fields restrictions here atm
    NAME = "metadata/standard"
       

class MetadataValueBuilder:
    """Build values to set via files post an put methods.
    works with the results of CustomMetadata and StandardMetadata get methods."""
    
    def __init__(self, metadata_fields_info: List[SimpleNamespace]):
        self.metadata_fields_info = metadata_fields_info
        self.metadata = []
        # create id to field mapping
        self.id_to_field = {field.id: field for field in self.metadata_fields_info}
        # create name to field mapping
        self.name_to_field = {field.name: field for field in self.metadata_fields_info}
        return

    def _transform_value(self, field_id, value):
        # Transform the value based on the field's metadata
        field = self.id_to_field.get(field_id, None)
        if not field:
            raise ValueError(f"Metadata field with id '{field_id}' not found.")
        # Apply any necessary transformations to the value
        # possible editTypes: date, map, focalpoint, orientation, multiselection, language, none, selection, number, text
        if field.editType == "date":
            if isinstance(value, date) or isinstance(value, datetime):
                value = value.isoformat()
        elif field.editType == "multiselection":
            if not isinstance(value, list):
                value = [value]
            # if the value is not int its a name an we must map it to id
            # allow mixup of ids and names
            transformed_values = []
            for v in value:
                if isinstance(v, int):
                    transformed_values.append(v)
                else:
                    # assume its a name
                    selection_options = self.get_selection_options(field_id) or []
                    name_index = self.get_selection_options_name_index(selection_options)
                    id = name_index.get(v, v)
                    if id:
                        transformed_values.append(id)
            value = transformed_values
        elif field.editType == "selection":
            if not isinstance(value, int):
                # assume its a name
                selection_options = self.get_selection_options(field_id) or []
                name_index = self.get_selection_options_name_index(selection_options)
                value = name_index.get(value, value)
        elif field.editType == "number":
            if not isinstance(value, (int, float)):
                try:
                    value = int(value)
                except ValueError:
                    try:
                        value = float(value)
                    except ValueError:
                        raise ValueError(f"Value for field id '{field_id}' must be a number.")
        elif field.editType == "boolean":
            if not isinstance(value, bool):
                if str(value).lower() in ["true", "1", "yes"]:
                    value = True
                elif str(value).lower() in ["false", "0", "no"]:
                    value = False
                else:
                    raise ValueError(f"Value for field id '{field_id}' must be a boolean.")
        elif field.editType == "language":
            # assume value is a language code string
            if not isinstance(value, str):
                raise ValueError(f"Value for field id '{field_id}' must be a language code string.")
        elif field.editType in ["text", "none", "map", "focalpoint", "orientation"]:
            # treat as string
            value = str(value)
        return value

    def append(self, action: Literal["add", "replace", "remove"], field_id: int, value=None):
        entry = {"action": action, "id": field_id}
        if action in ["replace", "add"]:
            entry["value"] = self._transform_value(field_id, value)
        self.metadata.append(entry)
        return self
    
    def append_by_name(self, action: Literal["add", "replace", "remove"], field_name: str, value=None):
        field = self.name_to_field.get(field_name, None)
        if not field:
            raise ValueError(f"Metadata field with name '{field_name}' not found.")
        field_id = getattr(field, "id", None)
        if field_id is None:
            raise ValueError(f"Metadata field id for name '{field_name}' not found.")
        self.append(action, field_id, value)
        return self

    def get_selection_options(self, id: int) -> Optional[List[dict]]:
            field = self.id_to_field.get(id, None)
            if not field:
                return None
            return getattr(field, "selectionOptions", None)
        
    def get_selection_options_by_name(self, name: str) -> Optional[List[dict]]:
        field = self.name_to_field.get(name, None)
        if not field:
            return None
        return getattr(field, "selectionOptions", None)
    
    @classmethod
    def get_selection_options_name_index(cls, selection_options: List[dict]) -> dict:
        """Convert a list of selection options to a name to id mapping dict."""
        index = {}
        for option in selection_options:
            name = option.get("name", None)
            id = option.get("id", None)
            if name and id is not None:
                index[name] = id
        return index

    def get_id(self, name: str) -> Optional[int]:
        return self.name_to_field.get(name, None) # type: ignore
        
    def add(self, name: str, value):
        return self.append_by_name("add", name, value)
    
    def replace(self, name: str, value):
        return self.append_by_name("replace", name, value)  
    
    def remove(self, name: str):
        return self.append_by_name("remove", name)
    
    def build(self) -> List[dict]:
        return self.metadata

class CustomMetadataBuilder(MetadataValueBuilder):
    """Builder for custom metadata values."""
    
    def __init__(self, client):
        custom_meta = CustomMetadata(client)
        custom_meta.set_response_fields(["id", "name", "editType", "selectionOptions"])
        metadata_fields_info = getattr(custom_meta.get(), "customMetadata", [])
        super().__init__(metadata_fields_info)
        
class StandardMetadataBuilder(MetadataValueBuilder):
    """Builder for standard metadata values."""
    
    def __init__(self, client):
        standard_meta = StandardMetadata(client)
        metadata_fields_info = getattr(standard_meta.get(), "standardMetadata", [])
        super().__init__(metadata_fields_info)
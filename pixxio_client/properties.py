from typing import Any, Optional

from ._base import ResourceBase
from .pixxio_types import PIXXIOId, ResponseData


class PropertyCreateBuilder:
    """Builder for PropertyPost form fields."""

    def __init__(self):
        self._fields = {}

    def address(self, value: str):
        self._fields["address"] = value
        return self

    def create_date(self, value: str):
        self._fields["createDate"] = value
        return self

    def name(self, value: str):
        self._fields["name"] = value
        return self

    def owner(self, value: str):
        self._fields["owner"] = value
        return self

    def set(self, key, value):
        self._fields[key] = value
        return self

    def build(self):
        return dict(self._fields)


class PropertyUpdateBuilder:
    """Builder for PropertyPut form fields."""

    def __init__(self):
        self._fields = {}

    def address(self, value: str):
        self._fields["address"] = value
        return self

    def name(self, value: str):
        self._fields["name"] = value
        return self

    def owner(self, value: str):
        self._fields["owner"] = value
        return self

    def truncate_address(self, value: bool = True):
        self._fields["truncateAddress"] = value
        return self

    def truncate_owner(self, value: bool = True):
        self._fields["truncateOwner"] = value
        return self

    def set(self, key, value):
        self._fields[key] = value
        return self

    def build(self):
        return dict(self._fields)


class PropertyDeleteBuilder:
    """Builder for PropertiesDelete query fields."""

    def __init__(self):
        self._fields = {}

    def id(self, value: PIXXIOId):
        self._fields["ids"] = [value]
        return self

    def ids(self, value):
        self._fields["ids"] = value
        return self

    def set(self, key, value):
        self._fields[key] = value
        return self

    def build(self):
        if "ids" not in self._fields:
            raise ValueError("'ids' is required for PropertiesDelete.")
        return dict(self._fields)


class Property(ResourceBase):
    """
    Resource for managing property records in PIXXIO.

    A property record holds information about a physical property (e.g. a
    building or location) depicted in an asset. Property records are linked
    to :class:`~pixxio_client.propertyreleases.PropertyRelease` documents
    confirming that the necessary permissions for depicting the property
    have been obtained.

    API endpoint: ``/api/v1/properties``

    Available operations (inherited):
        - ``get()``              – list all property records
        - ``get(id)``            – retrieve a specific property by ID
        - ``post(json_data)``    – create a new property record
        - ``put(id, json_data)`` – update an existing property record
        - ``delete(id=id)``      – delete a property record

    Example::

        from pixxio_client import Client
        from pixxio_client.properties import Property

        client = Client.create_client("api-key", "company.pixxio.com")
        props = Property(client)

        all_props = props.get()
        one_prop  = props.get(8)

    Response field filtering::

        props.set_response_fields(["id", "name", "address"])
        result = props.get()  # only returns the specified fields
    """

    NAME = "properties"

    def list(self, **params: Any) -> ResponseData:
        return self.get(**params)

    def create(self, **fields: Any) -> ResponseData:
        return self.post(form_data=fields)

    def update(self, id: PIXXIOId, **fields: Any) -> ResponseData:
        return self.put(id=id, form_data=fields)

    def delete(
        self,
        id: Optional[PIXXIOId] = None,
        ids=None,
        **params: Any,
    ) -> ResponseData:
        if id is not None and ids is not None:
            raise ValueError("Use either 'id' or 'ids', not both.")

        delete_params = dict(params)
        if ids is not None:
            delete_params["ids"] = ids
        elif id is not None:
            delete_params["ids"] = [id]
        elif "ids" not in delete_params:
            raise ValueError("'ids' is required for properties.delete().")

        return self._delete(endpoint_base=self.endpoint_base, **delete_params)

from typing import Any, Optional

from ._base import ResourceBase
from .pixxio_types import PIXXIOId, ResponseData


class PropertyReleaseCreateBuilder:
    """Builder for PropertyReleasePost form fields."""

    def __init__(self):
        self._fields = {}

    def color(self, value: str):
        self._fields["color"] = value
        return self

    def content(self, value: str):
        self._fields["content"] = value
        return self

    def create_date(self, value: str):
        self._fields["createDate"] = value
        return self

    def file(self, value):
        self._fields["file"] = value
        return self

    def file_name(self, value: str):
        self._fields["fileName"] = value
        return self

    def name(self, value: str):
        self._fields["name"] = value
        return self

    def property_id(self, value: int):
        self._fields["propertyID"] = value
        return self

    def release_create_date(self, value: str):
        self._fields["releaseCreateDate"] = value
        return self

    def show_file(self, value: bool):
        self._fields["showFile"] = value
        return self

    def show_warning_message(self, value: bool):
        self._fields["showWarningMessage"] = value
        return self

    def warning_message(self, value: str):
        self._fields["warningMessage"] = value
        return self

    def set(self, key, value):
        self._fields[key] = value
        return self

    def build(self):
        return dict(self._fields)


class PropertyReleaseUpdateBuilder:
    """Builder for PropertyReleasePut form fields."""

    def __init__(self):
        self._fields = {}

    def color(self, value: str):
        self._fields["color"] = value
        return self

    def delete_file(self, value: bool = True):
        self._fields["deleteFile"] = value
        return self

    def file(self, value):
        self._fields["file"] = value
        return self

    def file_name(self, value: str):
        self._fields["fileName"] = value
        return self

    def name(self, value: str):
        self._fields["name"] = value
        return self

    def release_create_date(self, value: str):
        self._fields["releaseCreateDate"] = value
        return self

    def show_file(self, value: bool):
        self._fields["showFile"] = value
        return self

    def show_warning_message(self, value: bool):
        self._fields["showWarningMessage"] = value
        return self

    def truncate_release_create_date(self, value: bool = True):
        self._fields["truncateReleaseCreateDate"] = value
        return self

    def truncate_warning_message(self, value: bool = True):
        self._fields["truncateWarningMessage"] = value
        return self

    def warning_message(self, value: str):
        self._fields["warningMessage"] = value
        return self

    def set(self, key, value):
        self._fields[key] = value
        return self

    def build(self):
        return dict(self._fields)


class PropertyReleaseDeleteBuilder:
    """Builder for PropertyReleasesDelete query fields."""

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
            raise ValueError("'ids' is required for PropertyReleasesDelete.")
        return dict(self._fields)


class PropertyRelease(ResourceBase):
    """
    Resource for managing property release documents in PIXXIO.

    A property release is a signed agreement granting permission to photograph
    or film a specific property (e.g. a privately owned building or artwork)
    and to publish the resulting images commercially. Releases are linked to
    the corresponding :class:`~pixxio_client.properties.Property` record and
    related assets.

    API endpoint: ``/api/v1/propertyReleases``

    Available operations (inherited):
        - ``get()``              – list all property release documents
        - ``get(id)``            – retrieve a specific release by ID
        - ``post(json_data)``    – register a new property release
        - ``put(id, json_data)`` – update an existing property release
        - ``delete(id=id)``      – delete a property release

    Example::

        from pixxio_client import Client
        from pixxio_client.propertyreleases import PropertyRelease

        client = Client.create_client("api-key", "company.pixxio.com")
        releases = PropertyRelease(client)

        all_releases = releases.get()
        one_release  = releases.get(2)

    Response field filtering::

        releases.set_response_fields(["id", "name", "createDate"])
        result = releases.get()  # only returns the specified fields
    """

    _paged = False
    NAME = "propertyReleases"

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
            raise ValueError("'ids' is required for propertyreleases.delete().")

        return self._delete(endpoint_base=self.endpoint_base, **delete_params)

from typing import Any, Optional

from ._base import ResourceBase
from .pixxio_types import PIXXIOId, ResponseData


class LicenseReleaseCreateBuilder:
    """Builder for LicenseReleasePost form fields."""

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

    def license_id(self, value: int):
        self._fields["licenseID"] = value
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

    def warning_message(self, value: str):
        self._fields["warningMessage"] = value
        return self

    def set(self, key, value):
        self._fields[key] = value
        return self

    def build(self):
        return dict(self._fields)


class LicenseReleaseDeleteBuilder:
    """Builder for LicenseReleasesDelete query fields."""

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
            raise ValueError("'ids' is required for LicenseReleasesDelete.")
        return dict(self._fields)


class LicenseRelease(ResourceBase):
    """
    Resource for managing license release documents in PIXXIO.

    License releases are signed agreements that grant specific usage rights
    for an asset. They are attached to files to document that the required
    permissions (e.g. for editorial or commercial use) have been obtained.

    API endpoint: ``/api/v1/licenseReleases``

    Available operations (inherited):
        - ``get()``              – list all license release documents
        - ``get(id)``            – retrieve a specific release by ID
        - ``post(json_data)``    – upload / register a new license release
        - ``put(id, json_data)`` – update an existing license release
        - ``delete(id=id)``      – delete a license release

    Example::

        from pixxio_client import Client
        from pixxio_client.licensereleases import LicenseRelease

        client = Client.create_client("api-key", "company.pixxio.com")
        releases = LicenseRelease(client)

        all_releases = releases.get()
        one_release  = releases.get(3)

    Response field filtering::

        releases.set_response_fields(["id", "name", "createDate"])
        result = releases.get()  # only returns the specified fields
    """

    _paged = False
    NAME = "licenseReleases"

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
            raise ValueError("'ids' is required for licensereleases.delete().")

        return self._delete(endpoint_base=self.endpoint_base, **delete_params)
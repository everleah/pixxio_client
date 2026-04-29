from typing import Any, Optional

from ._base import ResourceBase
from .pixxio_types import PIXXIOId, ResponseData


class LicenseCreateBuilder:
    """Builder for LicensePost form fields."""

    def __init__(self):
        self._fields = {}

    def provider(self, value: str):
        self._fields["provider"] = value
        return self

    def create_date(self, value: str):
        self._fields["createDate"] = value
        return self

    def set(self, key, value):
        self._fields[key] = value
        return self

    def build(self):
        return dict(self._fields)


class LicenseUpdateBuilder:
    """Builder for LicensePut form fields."""

    def __init__(self):
        self._fields = {}

    def provider(self, value: str):
        self._fields["provider"] = value
        return self

    def set(self, key, value):
        self._fields[key] = value
        return self

    def build(self):
        return dict(self._fields)


class LicenseDeleteBuilder:
    """Builder for LicensesDelete query fields."""

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
            raise ValueError("'ids' is required for LicensesDelete.")
        return dict(self._fields)


class License(ResourceBase):
    """
    Resource for managing licenses in PIXXIO.

    Licenses define the usage rights and restrictions associated with assets.
    Each license can specify permitted uses, territorial restrictions, and
    validity periods. Assets can be linked to one or more license records.

    API endpoint: ``/api/v1/licenses``

    Available operations (inherited):
        - ``get()``              – list all licenses
        - ``get(id)``            – retrieve a specific license by ID
        - ``post(json_data)``    – create a new license
        - ``put(id, json_data)`` – update an existing license
        - ``delete(id=id)``      – delete a license

    Example::

        from pixxio_client import Client
        from pixxio_client.licenses import License

        client = Client.create_client("api-key", "company.pixxio.com")
        licenses = License(client)

        all_licenses = licenses.get()
        one_license  = licenses.get(5)

    Response field filtering::

        licenses.set_response_fields(["id", "name"])
        result = licenses.get()  # only returns the specified fields
    """

    NAME = "licenses"

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
            raise ValueError("'ids' is required for licenses.delete().")

        return self._delete(endpoint_base=self.endpoint_base, **delete_params)
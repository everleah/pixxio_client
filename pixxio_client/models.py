from typing import Any, Optional

from ._base import ResourceBase
from .pixxio_types import PIXXIOId, ResponseData


class ModelCreateBuilder:
    """Builder for ModelPost form fields."""

    def __init__(self):
        self._fields = {}

    def birth_date(self, value: str):
        self._fields["birthDate"] = value
        return self

    def email(self, value: str):
        self._fields["email"] = value
        return self

    def first_name(self, value: str):
        self._fields["firstName"] = value
        return self

    def last_name(self, value: str):
        self._fields["lastName"] = value
        return self

    def set(self, key, value):
        self._fields[key] = value
        return self

    def build(self):
        return dict(self._fields)


class ModelUpdateBuilder:
    """Builder for ModelPut form fields."""

    def __init__(self):
        self._fields = {}

    def birth_date(self, value: str):
        self._fields["birthDate"] = value
        return self

    def email(self, value: str):
        self._fields["email"] = value
        return self

    def first_name(self, value: str):
        self._fields["firstName"] = value
        return self

    def last_name(self, value: str):
        self._fields["lastName"] = value
        return self

    def truncate_birth_date(self, value: bool = True):
        self._fields["truncateBirthDate"] = value
        return self

    def truncate_email(self, value: bool = True):
        self._fields["truncateEmail"] = value
        return self

    def set(self, key, value):
        self._fields[key] = value
        return self

    def build(self):
        return dict(self._fields)


class ModelDeleteBuilder:
    """Builder for ModelsDelete query fields."""

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
            raise ValueError("'ids' is required for ModelsDelete.")
        return dict(self._fields)


class Model(ResourceBase):
    """
    Resource for managing model records in PIXXIO.

    A model record holds information about a person depicted in an asset
    (e.g. name, date of birth). Model records are linked to
    :class:`~pixxio_client.modelreleases.ModelRelease` documents that confirm
    consent for using the person’s likeness.

    API endpoint: ``/api/v1/models``

    Available operations (inherited):
        - ``get()``              – list all model records
        - ``get(id)``            – retrieve a specific model by ID
        - ``post(json_data)``    – create a new model record
        - ``put(id, json_data)`` – update an existing model record
        - ``delete(id=id)``      – delete a model record

    Example::

        from pixxio_client import Client
        from pixxio_client.models import Model

        client = Client.create_client("api-key", "company.pixxio.com")
        models = Model(client)

        all_models = models.get()
        one_model  = models.get(12)

    Response field filtering::

        models.set_response_fields(["id", "name"])
        result = models.get()  # only returns the specified fields
    """

    NAME = "models"

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
            raise ValueError("'ids' is required for models.delete().")

        return self._delete(endpoint_base=self.endpoint_base, **delete_params)
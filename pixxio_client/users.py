from typing import Any

from ._base import ResourceBase
from .pixxio_types import PIXXIOId, ResponseData


class UserCreateBuilder:
    """Builder for UserPost form fields."""

    def __init__(self):
        self._fields = {}

    def email(self, value: str):
        self._fields["email"] = value
        return self

    def first_name(self, value: str):
        self._fields["firstName"] = value
        return self

    def is_active(self, value: bool):
        self._fields["isActive"] = value
        return self

    def language(self, value: str):
        self._fields["language"] = value
        return self

    def last_name(self, value: str):
        self._fields["lastName"] = value
        return self

    def password(self, value: str):
        self._fields["password"] = value
        return self

    def permission_group_ids(self, value: list):
        self._fields["permissionGroupIDs"] = value
        return self

    def user_name(self, value: str):
        self._fields["userName"] = value
        return self

    def set(self, key, value):
        self._fields[key] = value
        return self

    def build(self):
        return dict(self._fields)


class UserUpdateBuilder:
    """Builder for UserPut form fields."""

    def __init__(self):
        self._fields = {}

    def email(self, value: str):
        self._fields["email"] = value
        return self

    def first_name(self, value: str):
        self._fields["firstName"] = value
        return self

    def is_active(self, value: bool):
        self._fields["isActive"] = value
        return self

    def is_external(self, value: bool):
        self._fields["isExternal"] = value
        return self

    def language(self, value: str):
        self._fields["language"] = value
        return self

    def last_name(self, value: str):
        self._fields["lastName"] = value
        return self

    def password(self, value: str):
        self._fields["password"] = value
        return self

    def permission_group_ids_to_add(self, value: list):
        self._fields["permissionGroupIDsToAdd"] = value
        return self

    def permission_group_ids_to_remove(self, value: list):
        self._fields["permissionGroupIDsToRemove"] = value
        return self

    def recreate_refresh_token(self, value: bool = True):
        self._fields["recreateRefreshToken"] = value
        return self

    def truncate_first_name(self, value: bool = True):
        self._fields["truncateFirstName"] = value
        return self

    def truncate_last_name(self, value: bool = True):
        self._fields["truncateLastName"] = value
        return self

    def two_factor_auth_set_up(self, value: bool):
        self._fields["twoFactorAuthSetUp"] = value
        return self

    def user_name(self, value: str):
        self._fields["userName"] = value
        return self

    def set(self, key, value):
        self._fields[key] = value
        return self

    def build(self):
        return dict(self._fields)


class User(ResourceBase):
    """
    Resource for managing user accounts in PIXXIO.

    Users represent individual login accounts inside the PIXXIO system. User
    records contain profile information (name, e-mail, language, …) and link
    to permission groups that control what each user may do.

    API endpoint: ``/api/v1/users``

    Available operations (inherited):
        - ``get()``              – list all users
        - ``get(id)``            – retrieve a specific user by ID
        - ``post(json_data)``    – create a new user account
        - ``put(id, json_data)`` – update an existing user (e.g. change name or group)
        - ``delete(id=id)``      – delete a user account

    Example::

        from pixxio_client import Client
        from pixxio_client.users import User

        client = Client.create_client("api-key", "company.pixxio.com")
        users = User(client)

        # List all users
        all_users = users.get()

        # Retrieve a single user
        me = users.get(42)
        print(me.firstName, me.lastName, me.email)

        # Update a user’s display name
        users.put(42, json_data={"firstName": "Jane"})
    Response field filtering::

        users.set_response_fields(["id", "displayName", "email", "isActive"])
        result = users.get()  # only returns the specified fields    """

    NAME = "users"

    def list(self, **params: Any) -> ResponseData:
        return self.get(**params)

    def create(self, **fields: Any) -> ResponseData:
        return self.post(form_data=fields)

    def update(self, id: PIXXIOId, **fields: Any) -> ResponseData:
        return self.put(id=id, form_data=fields)

    def get_current(self, **params: Any) -> ResponseData:
        return self._get(endpoint_base=f"{self.endpoint_base}/current", **params)

    def delete(self, id: PIXXIOId, **params: Any) -> ResponseData:
        return self._delete(endpoint_base=f"{self.endpoint_base}/{id}", **params)


from ._base import ReadOnlyResourceBase


class PermissionGroup(ReadOnlyResourceBase):
    """
    Resource for reading permission groups in PIXXIO.

    Permission groups define sets of access rights that can be assigned to
    users. They control which actions (view, download, edit, delete …) a
    user may perform on assets and directories. Permission groups are
    managed in the PIXXIO backend and are read-only from the API.

    API endpoint: ``/api/v1/permissionGroups``

    Available operations (inherited):
        - ``get()``    – list all permission groups
        - ``get(id)``  – retrieve a specific permission group by ID

    Example::

        from pixxio_client import Client
        from pixxio_client.permissiongroups import PermissionGroup

        client = Client.create_client("api-key", "company.pixxio.com")
        groups = PermissionGroup(client)

        all_groups = groups.get()
        for g in all_groups.permissionGroups:
            print(g.id, g.name)

    Response field filtering::

        groups.set_response_fields(["id", "name", "isAdmin"])
        result = groups.get()  # only returns the specified fields
    """

    NAME = "permissionGroups"
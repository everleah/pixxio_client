from typing import Any

from ._base import ResourceBase
from .pixxio_types import PIXXIOId, ResponseData


class DirectoryGetBuilder:
    """
    Builder for directory list/query parameters (DirectoriesGet).
    """

    def __init__(self):
        self._params = {}

    def name(self, value: str):
        self._params["name"] = value
        return self

    def page(self, value: int):
        self._params["page"] = value
        return self

    def page_size(self, value: int):
        self._params["pageSize"] = value
        return self

    def response_fields(self, value):
        self._params["responseFields"] = value
        return self

    def show_subversions(self, value: bool):
        self._params["showSubVersions"] = value
        return self

    def sort_by(self, value: str):
        self._params["sortBy"] = value
        return self

    def sort_direction(self, value: str):
        self._params["sortDirection"] = value
        return self

    def set(self, key, value):
        self._params[key] = value
        return self

    def build(self):
        return dict(self._params)


class DirectoryCreateBuilder:
    """
    Builder for directory creation form fields (DirectoryPost).
    """

    def __init__(self):
        self._fields = {}

    def name(self, value: str):
        self._fields["name"] = value
        return self

    def parent_id(self, value: int):
        self._fields["parentID"] = value
        return self

    def set(self, key, value):
        self._fields[key] = value
        return self

    def build(self):
        return dict(self._fields)


class DirectoryUpdateBuilder:
    """
    Builder for directory update form fields (DirectoryPut).
    """

    def __init__(self):
        self._fields = {}

    def name(self, value: str):
        self._fields["name"] = value
        return self

    def parent_id(self, value: int):
        self._fields["parentID"] = value
        return self

    def set(self, key, value):
        self._fields[key] = value
        return self

    def build(self):
        return dict(self._fields)


class DirectoryTreeBuilder:
    """
    Builder for directory tree query parameters (DirectoriesTree).
    """

    def __init__(self):
        self._params = {}

    def child_id(self, value: int):
        self._params["childID"] = value
        return self

    def parent_id(self, value: int):
        self._params["parentID"] = value
        return self

    def response_fields(self, value):
        self._params["responseFields"] = value
        return self

    def show_children(self, value: bool):
        self._params["showChildren"] = value
        return self

    def show_parents(self, value: bool):
        self._params["showParents"] = value
        return self

    def show_subversions(self, value: bool):
        self._params["showSubVersions"] = value
        return self

    def sort_by(self, value: str):
        self._params["sortBy"] = value
        return self

    def sort_direction(self, value: str):
        self._params["sortDirection"] = value
        return self

    def set(self, key, value):
        self._params[key] = value
        return self

    def build(self):
        return dict(self._params)


class Directory(ResourceBase):
    """
    Resource for managing directories (folders) in PIXXIO.

    Directories represent the folder hierarchy used to organise assets inside
    PIXXIO. Standard CRUD operations allow creating, updating and deleting
    folders. The additional :meth:`get_tree` method returns the full nested
    directory hierarchy in a single request.

    API endpoint: ``/api/v1/directories``

    Available operations:
        - ``get()``              – list all directories
        - ``get(id)``            – retrieve a specific directory by ID
        - ``post(form_data=...)`` – create a new directory
        - ``put(id, form_data=...)`` – update a directory (e.g. rename)
        - ``delete(id=id)``      – delete a directory

    Example::

        from pixxio_client import Client
        from pixxio_client.directories import Directory

        client = Client.create_client("api-key", "company.pixxio.com")
        dirs = Directory(client)

        # List root directories
        all_dirs = dirs.get()

        # Get full tree structure
        tree = dirs.get_tree()

        # Create a sub-folder
        new_dir = dirs.create(name="Projects", parentID=1)

    Response field filtering::

        dirs.set_response_fields(["id", "name", "hasChildren"])
        result = dirs.get()  # only returns the specified fields

    Note:
        Response field filtering is suppressed automatically for
        :meth:`get_tree`, which does not support the parameter.
    """

    NAME = "directories"

    def list(self, **params: Any) -> ResponseData:
        """
        Convenience alias for list-style directory GET requests.
        """
        return self.get(**params)

    def create(self, **fields: Any) -> ResponseData:
        """
        Convenience helper for DirectoryPost using multipart form fields.
        """
        return self.post(form_data=fields)

    def update(self, id: PIXXIOId, **fields: Any) -> ResponseData:
        """
        Convenience helper for DirectoryPut using multipart form fields.
        """
        return self.put(id=id, form_data=fields)

    def delete(self, id: PIXXIOId, **params: Any) -> ResponseData:
        """
        Delete a directory by ID.

        OpenAPI defines delete on ``/directories/{directory_id}``, so this
        method calls the path-based endpoint directly.
        """
        return self._delete(endpoint_base=f"{self.endpoint_base}/{id}", **params)

    def get_tree(self, **params):
        """
        Retrieve the complete directory tree.

        Returns the entire folder hierarchy of the PIXXIO instance in a single
        call, including nesting relationships between directories.

        Note:
            This endpoint does not support the ``responseFields`` parameter.
            Any response fields configured on the resource instance are
            automatically suppressed for this call.

        Args:
            **params: Additional query parameters forwarded to the API
                (e.g. ``directoryId`` to start from a specific root).

        Returns:
            ResponseData: Nested directory structure.

        Example::

            dirs = Directory(client)
            tree = dirs.get_tree()
        """
        with self._without_response_fields():
            return self._get(
                endpoint_base=f"{self.endpoint_base}/tree",
                **params)
from ._base import ResourceBase


class Directory(ResourceBase):
    """
    Resource for managing directories (folders) in PIXXIO.

    Directories represent the folder hierarchy used to organise assets inside
    PIXXIO. Standard CRUD operations allow creating, updating and deleting
    folders. The additional :meth:`get_tree` method returns the full nested
    directory hierarchy in a single request.

    API endpoint: ``/api/v1/directories``

    Available operations (inherited):
        - ``get()``              – list all directories
        - ``get(id)``            – retrieve a specific directory by ID
        - ``post(json_data)``    – create a new directory
        - ``put(id, json_data)`` – update a directory (e.g. rename)
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
        new_dir = dirs.post(json_data={"name": "Projects", "parentId": 1})

    Response field filtering::

        dirs.set_response_fields(["id", "name", "hasChildren"])
        result = dirs.get()  # only returns the specified fields

    Note:
        Response field filtering is suppressed automatically for
        :meth:`get_tree`, which does not support the parameter.
    """

    NAME = "directories"

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
from ._base import ResourceBase


class Collection(ResourceBase):
    """
    Resource for managing file collections in PIXXIO.

    Collections are named groupings of assets that allow users to organise
    files independently of the folder/directory structure. A collection can
    contain any number of files and can be shared or reused across projects.

    API endpoint: ``/api/v1/collections``

    Available operations (inherited):
        - ``get()``              – list all accessible collections
        - ``get(id)``            – retrieve a specific collection by ID
        - ``post(json_data)``    – create a new collection
        - ``put(id, json_data)`` – update an existing collection
        - ``delete(id=id)``      – delete a collection

    Example::

        from pixxio_client import Client
        from pixxio_client.collections import Collection

        client = Client.create_client("api-key", "company.pixxio.com")
        collections = Collection(client)

        # List all collections
        all_cols = collections.get()

        # Create a new collection
        new_col = collections.post(json_data={"name": "My Collection"})

        # Update collection name
        collections.put(new_col.id, json_data={"name": "Renamed Collection"})

        # Delete collection
        collections.delete(id=new_col.id)

    Response field filtering::

        collections.set_response_fields(["id", "name", "filesQuantity"])
        result = collections.get()  # only returns the specified fields
    """

    NAME = "collections"
    
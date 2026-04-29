from ._base import ResourceBase


class VariantStack(ResourceBase):
    """
    Resource for managing variant stacks in PIXXIO.

    A variant stack groups multiple versions (variants) of the same asset
    under a single identifier. Typical variants include different resolutions,
    colour profiles, or language versions of the same image or document.
    Using stacks keeps the media library organised and ensures that all
    variants are discovered together.

    API endpoint: ``/api/v1/variantStacks``

    Available operations (inherited):
        - ``get()``              – list all variant stacks
        - ``get(id)``            – retrieve a specific variant stack by ID
        - ``post(json_data)``    – create a new variant stack
        - ``put(id, json_data)`` – update an existing variant stack
        - ``delete(id=id)``      – delete a variant stack

    Example::

        from pixxio_client import Client
        from pixxio_client.variantstacks import VariantStack

        client = Client.create_client("api-key", "company.pixxio.com")
        stacks = VariantStack(client)

        # List all variant stacks
        all_stacks = stacks.get()

        # Create a new variant stack linking files 100 and 101
        new_stack = stacks.post(json_data={"fileIds": [100, 101]})

        # Add another file to the stack
        stacks.put(new_stack.id, json_data={"fileIds": [100, 101, 102]})

    Response field filtering::

        stacks.set_response_fields(["id", "name"])
        result = stacks.get()  # only returns the specified fields
    """

    NAME = "variantStacks"
    
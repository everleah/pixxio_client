from ._base import ResourceBase


class Property(ResourceBase):
    """
    Resource for managing property records in PIXXIO.

    A property record holds information about a physical property (e.g. a
    building or location) depicted in an asset. Property records are linked
    to :class:`~pixxio_client.propertyreleases.PropertyRelease` documents
    confirming that the necessary permissions for depicting the property
    have been obtained.

    API endpoint: ``/api/v1/properties``

    Available operations (inherited):
        - ``get()``              – list all property records
        - ``get(id)``            – retrieve a specific property by ID
        - ``post(json_data)``    – create a new property record
        - ``put(id, json_data)`` – update an existing property record
        - ``delete(id=id)``      – delete a property record

    Example::

        from pixxio_client import Client
        from pixxio_client.properties import Property

        client = Client.create_client("api-key", "company.pixxio.com")
        props = Property(client)

        all_props = props.get()
        one_prop  = props.get(8)

    Response field filtering::

        props.set_response_fields(["id", "name", "address"])
        result = props.get()  # only returns the specified fields
    """

    NAME = "properties"
    
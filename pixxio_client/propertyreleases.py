from ._base import ResourceBase


class PropertyRelease(ResourceBase):
    """
    Resource for managing property release documents in PIXXIO.

    A property release is a signed agreement granting permission to photograph
    or film a specific property (e.g. a privately owned building or artwork)
    and to publish the resulting images commercially. Releases are linked to
    the corresponding :class:`~pixxio_client.properties.Property` record and
    related assets.

    API endpoint: ``/api/v1/propertyReleases``

    Available operations (inherited):
        - ``get()``              – list all property release documents
        - ``get(id)``            – retrieve a specific release by ID
        - ``post(json_data)``    – register a new property release
        - ``put(id, json_data)`` – update an existing property release
        - ``delete(id=id)``      – delete a property release

    Example::

        from pixxio_client import Client
        from pixxio_client.propertyreleases import PropertyRelease

        client = Client.create_client("api-key", "company.pixxio.com")
        releases = PropertyRelease(client)

        all_releases = releases.get()
        one_release  = releases.get(2)

    Response field filtering::

        releases.set_response_fields(["id", "name", "createDate"])
        result = releases.get()  # only returns the specified fields
    """

    NAME = "propertyReleases"
    
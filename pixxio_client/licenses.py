from ._base import ResourceBase


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
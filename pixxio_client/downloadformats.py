
from ._base import ReadOnlyResourceBase


class DownloadFormat(ReadOnlyResourceBase):
    """
    Resource for retrieving available download formats from PIXXIO.

    Download formats define the output options (file type, size, resolution,
    colour space, etc.) that a user can request when downloading an asset.
    These formats are configured in the PIXXIO backend and are read-only from
    the API perspective.

    API endpoint: ``/api/v1/downloadFormats``

    Available operations (inherited):
        - ``get()``    – list all available download formats
        - ``get(id)``  – retrieve a specific download format by ID

    Example::

        from pixxio_client import Client
        from pixxio_client.downloadformats import DownloadFormat

        client = Client.create_client("api-key", "company.pixxio.com")
        formats = DownloadFormat(client)

        all_formats = formats.get()
        for fmt in all_formats.downloadFormats:
            print(fmt.name, fmt.format)

    Response field filtering::

        formats.set_response_fields(["id", "name", "format"])
        result = formats.get()  # only returns the specified fields
    """

    NAME = "downloadFormats"
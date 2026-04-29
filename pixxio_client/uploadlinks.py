from ._base import ResourceBase


class UploadLink(ResourceBase):
    """
    Resource for managing upload links in PIXXIO.

    Upload links are pre-authenticated URLs that allow external parties to
    upload assets to a specific PIXXIO directory without requiring a full
    PIXXIO account. Each link can be restricted by expiry date, allowed file
    types, and maximum number of uploads.

    API endpoint: ``/api/v1/uploadLinks``

    Available operations (inherited):
        - ``get()``              – list all upload links
        - ``get(id)``            – retrieve a specific upload link by ID
        - ``post(json_data)``    – create a new upload link
        - ``put(id, json_data)`` – update an existing upload link
        - ``delete(id=id)``      – delete an upload link

    Example::

        from pixxio_client import Client
        from pixxio_client.uploadlinks import UploadLink

        client = Client.create_client("api-key", "company.pixxio.com")
        links = UploadLink(client)

        # Create an upload link for directory 10, valid for 14 days
        new_link = links.post(json_data={
            "directoryId": 10,
            "validDays": 14,
        })
        print(new_link.url)

        # List all existing upload links
        all_links = links.get()

        # Remove a link
        links.delete(id=new_link.id)

    Response field filtering::

        links.set_response_fields(["id", "url", "validUntil"])
        result = links.get()  # only returns the specified fields
    """

    NAME = "uploadLinks"
    
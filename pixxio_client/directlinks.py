from ._base import ResourceBase


class DirectLink(ResourceBase):
    """
    Resource for managing direct download links in PIXXIO.

    Direct links are pre-authenticated, shareable URLs that grant access to a
    specific file or asset without requiring the recipient to log in. They are
    useful for sharing individual assets with external parties.

    API endpoint: ``/api/v1/directLinks``

    Available operations (inherited):
        - ``get()``              – list all direct links
        - ``get(id)``            – retrieve a specific direct link by ID
        - ``post(json_data)``    – create a new direct link
        - ``put(id, json_data)`` – update an existing direct link
        - ``delete(id=id)``      – delete a direct link

    Example::

        from pixxio_client import Client
        from pixxio_client.directlinks import DirectLink

        client = Client.create_client("api-key", "company.pixxio.com")
        links = DirectLink(client)

        # Create a direct link for file 123
        new_link = links.post(json_data={"fileId": 123, "validDays": 7})
        print(new_link.url)

        # List all direct links
        all_links = links.get()

        # Remove a link
        links.delete(id=new_link.id)

    Response field filtering::

        links.set_response_fields(["id", "url", "validUntil"])
        result = links.get()  # only returns the specified fields
    """

    NAME = "directLinks"
    
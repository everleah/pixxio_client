from ._base import ResourceBase


class ExternalShare(ResourceBase):
    """
    Resource for managing external share links in PIXXIO.

    External shares allow assets or collections to be shared with people who
    do not have a PIXXIO account. A share can be password-protected, limited
    in time, and restricted to specific download formats.

    API endpoint: ``/api/v1/externalShares``

    Available operations (inherited):
        - ``get()``              – list all external shares
        - ``get(id)``            – retrieve a specific share by ID
        - ``post(json_data)``    – create a new external share
        - ``put(id, json_data)`` – update an existing external share
        - ``delete(id=id)``      – delete an external share

    Example::

        from pixxio_client import Client
        from pixxio_client.externalshares import ExternalShare

        client = Client.create_client("api-key", "company.pixxio.com")
        shares = ExternalShare(client)

        # Create a share for file 123, valid for 30 days
        new_share = shares.post(json_data={
            "fileIds": [123],
            "validDays": 30,
            "password": "secret"
        })
        print(new_share.shareUrl)

        # List all active shares
        all_shares = shares.get()

        # Remove a share
        shares.delete(id=new_share.id)

    Response field filtering::

        shares.set_response_fields(["id", "shareUrl", "validUntil"])
        result = shares.get()  # only returns the specified fields
    """

    NAME = "externalShares"
    
    
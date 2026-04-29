from ._base import ResourceBase


class LicenseRelease(ResourceBase):
    """
    Resource for managing license release documents in PIXXIO.

    License releases are signed agreements that grant specific usage rights
    for an asset. They are attached to files to document that the required
    permissions (e.g. for editorial or commercial use) have been obtained.

    API endpoint: ``/api/v1/licenseReleases``

    Available operations (inherited):
        - ``get()``              – list all license release documents
        - ``get(id)``            – retrieve a specific release by ID
        - ``post(json_data)``    – upload / register a new license release
        - ``put(id, json_data)`` – update an existing license release
        - ``delete(id=id)``      – delete a license release

    Example::

        from pixxio_client import Client
        from pixxio_client.licensereleases import LicenseRelease

        client = Client.create_client("api-key", "company.pixxio.com")
        releases = LicenseRelease(client)

        all_releases = releases.get()
        one_release  = releases.get(3)

    Response field filtering::

        releases.set_response_fields(["id", "name", "createDate"])
        result = releases.get()  # only returns the specified fields
    """

    NAME = "licenseReleases"
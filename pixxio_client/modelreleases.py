from ._base import ResourceBase


class ModelRelease(ResourceBase):
    """
    Resource for managing model release documents in PIXXIO.

    A model release is a signed consent document that permits the use of a
    person’s likeness in published media. Model releases are linked to both
    the :class:`~pixxio_client.models.Model` record and the relevant assets.

    API endpoint: ``/api/v1/modelReleases``

    Available operations (inherited):
        - ``get()``              – list all model release documents
        - ``get(id)``            – retrieve a specific release by ID
        - ``post(json_data)``    – register a new model release
        - ``put(id, json_data)`` – update an existing model release
        - ``delete(id=id)``      – delete a model release

    Example::

        from pixxio_client import Client
        from pixxio_client.modelreleases import ModelRelease

        client = Client.create_client("api-key", "company.pixxio.com")
        releases = ModelRelease(client)

        all_releases = releases.get()
        one_release  = releases.get(5)

    Response field filtering::

        releases.set_response_fields(["id", "name", "createDate"])
        result = releases.get()  # only returns the specified fields
    """

    NAME = "modelReleases"
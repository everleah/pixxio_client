from ._base import ResourceBase


class Model(ResourceBase):
    """
    Resource for managing model records in PIXXIO.

    A model record holds information about a person depicted in an asset
    (e.g. name, date of birth). Model records are linked to
    :class:`~pixxio_client.modelreleases.ModelRelease` documents that confirm
    consent for using the person’s likeness.

    API endpoint: ``/api/v1/models``

    Available operations (inherited):
        - ``get()``              – list all model records
        - ``get(id)``            – retrieve a specific model by ID
        - ``post(json_data)``    – create a new model record
        - ``put(id, json_data)`` – update an existing model record
        - ``delete(id=id)``      – delete a model record

    Example::

        from pixxio_client import Client
        from pixxio_client.models import Model

        client = Client.create_client("api-key", "company.pixxio.com")
        models = Model(client)

        all_models = models.get()
        one_model  = models.get(12)

    Response field filtering::

        models.set_response_fields(["id", "name"])
        result = models.get()  # only returns the specified fields
    """

    NAME = "models"
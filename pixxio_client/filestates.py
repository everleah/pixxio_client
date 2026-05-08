
from ._base import ReadOnlyResourceBase


class FileState(ReadOnlyResourceBase):
    """
    Resource for retrieving file workflow states from PIXXIO.

    File states represent the workflow status of an asset, such as
    ``draft``, ``review`` or ``approved``. The available states are defined
    in the PIXXIO backend configuration and are read-only from the API.

    API endpoint: ``/api/v1/fileStates``

    Available operations (inherited):
        - ``get()``    – list all configured file states
        - ``get(id)``  – retrieve a specific file state by ID

    Example::

        from pixxio_client import Client
        from pixxio_client.filestates import FileState

        client = Client.create_client("api-key", "company.pixxio.com")
        states = FileState(client)

        all_states = states.get()
        for state in all_states.fileStates:
            print(state.id, state.name)

    Response field filtering::

        states.set_response_fields(["id", "name"])
        result = states.get()  # only returns the specified fields
    """

    _paged = False
    NAME = "fileStates"
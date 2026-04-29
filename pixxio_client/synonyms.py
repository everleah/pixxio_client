from .keywords import Keyword


class Synonym(Keyword):
    """
    Resource for managing keyword synonyms in PIXXIO.

    Synonyms extend the :class:`~pixxio_client.keywords.Keyword` resource to
    cover synonym mappings. A synonym links an alternative term to a canonical
    keyword so that searches for either term return the same results.

    Synonym columns (the fields of each synonym record) can be retrieved via
    :meth:`get_columns`.

    API endpoint: ``/api/v1/synonyms``

    Available operations (inherited from Keyword / ResourceBase):
        - ``get()``              – list all synonyms
        - ``get(id)``            – retrieve a specific synonym by ID
        - ``post(json_data)``    – import synonyms via the CSV endpoint
        - ``put(id, ...)``       – **not available** (raises ``NotImplementedError``)
        - ``delete(id=id)``      – delete a synonym
        - ``download()``         – export synonyms as CSV
        - ``get_columns()``      – retrieve synonym column definitions

    Example::

        from pixxio_client import Client
        from pixxio_client.synonyms import Synonym

        client = Client.create_client("api-key", "company.pixxio.com")
        synonyms = Synonym(client)

        # List all synonyms
        all_synonyms = synonyms.get()

        # Get column schema
        cols = synonyms.get_columns()

    Response field filtering::

        synonyms.set_response_fields(["id", "name"])
        result = synonyms.get()  # only returns the specified fields

    Note:
        Response field filtering is suppressed automatically for
        :meth:`get_columns`, :meth:`post` (CSV import) and
        :meth:`download` (CSV export), as those endpoints do not
        support the parameter.
    """

    NAME = "synonyms"

    def get_columns(self, **params):
        """
        Retrieve the column definitions for synonym records.

        Sends a GET request to ``/api/v1/synonymColumns`` and returns the
        schema that describes the fields available on each synonym entry.

        Note:
            The ``responseFields`` parameter is not supported by this endpoint
            and is automatically suppressed.

        Args:
            **params: Additional query parameters forwarded to the API.

        Returns:
            ResponseData: Object describing the synonym column schema.

        Example::

            synonyms = Synonym(client)
            cols = synonyms.get_columns()
            for col in cols.synonymColumns:
                print(col.name, col.type)
        """
        with self._without_response_fields():
            return self._get(
                endpoint_base=f"{self.client.location_base}/synonymColumns",
                **params)
    
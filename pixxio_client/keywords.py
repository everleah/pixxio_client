from typing import Optional, Dict, Any

from ._base import ResourceBase, ResourceUploadMixin
from .pixxio_types import PIXXIOId, ResponseData, JSONDict, FileParams


class Keyword(ResourceBase, ResourceUploadMixin):
    """
    Resource for managing keywords in PIXXIO.

    Keywords are tags that describe the content of an asset and make it
    discoverable through search. Keywords are imported and exported in CSV
    format; the standard REST ``post`` endpoint routes to ``/keywords/csv``.
    Bulk upload is available through the :class:`ResourceUploadMixin`.

    API endpoint: ``/api/v1/keywords``

    Available operations:
        - ``get()``              – list all keywords
        - ``get(id)``            – retrieve a specific keyword by ID
        - ``post(json_data)``    – import keywords via CSV endpoint (``/keywords/csv``)
        - ``put(id, ...)``       – **not available** in the PIXXIO API (raises ``NotImplementedError``)
        - ``delete(id=id)``      – delete a keyword
        - ``download()``         – export all keywords as a CSV file
        - ``upload()``           – upload a keyword CSV file (from :class:`ResourceUploadMixin`)

    Example::

        from pixxio_client import Client
        from pixxio_client.keywords import Keyword

        client = Client.create_client("api-key", "company.pixxio.com")
        keywords = Keyword(client)

        # List all keywords
        all_keywords = keywords.get()

        # Import keywords from a CSV payload
        keywords.post(json_data={"csv": "keyword1\nkeyword2"})

        # Download keyword list as CSV
        csv_response = keywords.download()

    Response field filtering::

        keywords.set_response_fields(["id", "name"])
        result = keywords.get()  # only returns the specified fields

    Note:
        Response field filtering is suppressed automatically for
        :meth:`post` (CSV import) and :meth:`download` (CSV export),
        as those endpoints do not support the parameter.
    """

    NAME = "keywords"

    def put(self, id: PIXXIOId, **params: Any) -> None:
        """
        Not available for the keywords API.

        The PIXXIO API does not expose a PUT endpoint for keywords. Calling
        this method always raises :class:`NotImplementedError`.

        Raises:
            NotImplementedError: Always.
        """
        raise NotImplementedError("not available in api")

    def post(
        self,
        json_data: Optional[JSONDict] = None,
        form_data: Optional[Dict[str, Any]] = None,
        files: Optional[FileParams] = None,
        **params: Any
    ) -> ResponseData:
        """
        Import keywords via the CSV endpoint.

        Routes the POST request to ``/api/v1/keywords/csv`` instead of the
        standard ``/api/v1/keywords`` endpoint, as required by the PIXXIO API.

        Args:
            json_data: Optional JSON body (e.g. ``{"csv": "kw1\nkw2"}``)
            form_data: Optional form-encoded fields.
            files: Optional file payload (``{"file": file_handle}``).
            **params: Additional query parameters forwarded to the API.

        Returns:
            ResponseData: API response object.

        Example::

            keywords.post(json_data={"csv": "nature\nlandscape\nsunset"})
        """
        return self._post(
            endpoint_base=f"{self.endpoint_base}/csv",
            json_data=json_data,
            form_data=form_data,
            files=files,
            **params)

    def download(self, **params: Any) -> ResponseData:
        """
        Download all keywords as a CSV file.

        Sends a GET request to ``/api/v1/keywords/csv`` and returns the raw
        CSV content.

        Note:
            The ``responseFields`` parameter is not supported by this endpoint
            and is automatically suppressed.

        Args:
            **params: Additional query parameters forwarded to the API.

        Returns:
            ResponseData: Object whose body contains the CSV data.

        Example::

            csv_data = keywords.download()
        """
        with self._without_response_fields():
            return self._get(
                endpoint_base=f"{self.endpoint_base}/csv",
                **params)
    
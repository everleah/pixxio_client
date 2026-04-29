from typing import Any, Optional

from ._base import ResourceBase
from .pixxio_types import PIXXIOId, ResponseData


class DirectLinkGetBuilder:
    """
    Builder for direct link list/query parameters (DirectLinksGet).
    """

    def __init__(self):
        self._params = {}

    def page(self, value: int):
        self._params["page"] = value
        return self

    def page_size(self, value: int):
        self._params["pageSize"] = value
        return self

    def response_fields(self, value):
        self._params["responseFields"] = value
        return self

    def file_response_fields(self, value):
        self._params["fileResponseFields"] = value
        return self

    def download_format_response_fields(self, value):
        self._params["downloadFormatResponseFields"] = value
        return self

    def file_ids(self, value):
        self._params["fileIDs"] = value
        return self

    def file_name(self, value: str):
        self._params["fileName"] = value
        return self

    def is_custom(self, value: bool):
        self._params["isCustom"] = value
        return self

    def sort_by(self, value: str):
        self._params["sortBy"] = value
        return self

    def sort_direction(self, value: str):
        self._params["sortDirection"] = value
        return self

    def set(self, key, value):
        self._params[key] = value
        return self

    def build(self):
        return dict(self._params)


class DirectLinkCreateBuilder:
    """
    Builder for direct link creation form fields (DirectLinkPost).
    """

    def __init__(self):
        self._fields = {}

    def add_watermark(self, value: bool):
        self._fields["addWatermark"] = value
        return self

    def allow_upscaling(self, value: bool):
        self._fields["allowUpscaling"] = value
        return self

    def apply_metadata(self, value: bool):
        self._fields["applyMetadata"] = value
        return self

    def colorspace(self, value: str):
        self._fields["colorspace"] = value
        return self

    def crop(self, value):
        self._fields["crop"] = value
        return self

    def density(self, value: int):
        self._fields["density"] = value
        return self

    def download_format_id(self, value: int):
        self._fields["downloadFormatID"] = value
        return self

    def download_proof(self, value: str):
        self._fields["downloadProof"] = value
        return self

    def download_type(self, value: str):
        self._fields["downloadType"] = value
        return self

    def file_extension(self, value: str):
        self._fields["fileExtension"] = value
        return self

    def file_id(self, value: int):
        self._fields["fileID"] = value
        return self

    def file_name(self, value: str):
        self._fields["fileName"] = value
        return self

    def height(self, value: int):
        self._fields["height"] = value
        return self

    def layers(self, value):
        self._fields["layers"] = value
        return self

    def max_size(self, value: int):
        self._fields["maxSize"] = value
        return self

    def min_size(self, value: int):
        self._fields["minSize"] = value
        return self

    def quality(self, value: int):
        self._fields["quality"] = value
        return self

    def rotation(self, value: int):
        self._fields["rotation"] = value
        return self

    def strip_metadata(self, value: bool):
        self._fields["stripMetadata"] = value
        return self

    def unit(self, value: str):
        self._fields["unit"] = value
        return self

    def width(self, value: int):
        self._fields["width"] = value
        return self

    def set(self, key, value):
        self._fields[key] = value
        return self

    def build(self):
        return dict(self._fields)


class DirectLinkUpdateBuilder:
    """
    Builder for direct link update form fields (DirectLinkPut).
    """

    def __init__(self):
        self._fields = {}

    def file_name(self, value: str):
        self._fields["fileName"] = value
        return self

    def set(self, key, value):
        self._fields[key] = value
        return self

    def build(self):
        return dict(self._fields)


class DirectLinkDeleteBuilder:
    """
    Builder for direct link delete query fields (DirectLinksDelete).
    """

    def __init__(self):
        self._fields = {}

    def id(self, value: PIXXIOId):
        self._fields["ids"] = [value]
        return self

    def ids(self, value):
        self._fields["ids"] = value
        return self

    def set(self, key, value):
        self._fields[key] = value
        return self

    def build(self):
        if "ids" not in self._fields:
            raise ValueError("'ids' is required for DirectLinksDelete.")
        return dict(self._fields)


class DirectLink(ResourceBase):
    """
    Resource for managing direct download links in PIXXIO.

    Direct links are pre-authenticated, shareable URLs that grant access to a
    specific file or asset without requiring the recipient to log in. They are
    useful for sharing individual assets with external parties.

    API endpoint: ``/api/v1/directLinks``

    Available operations:
        - ``get()``              – list all direct links
        - ``get(id)``            – retrieve a specific direct link by ID
        - ``post(form_data=...)`` – create a new direct link
        - ``put(id, form_data=...)`` – update an existing direct link
        - ``delete(id=...)``      – delete one direct link (compatibility helper)
        - ``delete(ids=[...])``   – delete one or more direct links (API contract)

    Example::

        from pixxio_client import Client
        from pixxio_client.directlinks import DirectLink

        client = Client.create_client("api-key", "company.pixxio.com")
        links = DirectLink(client)

        # Create a direct link for file 123
        new_link = links.create(fileID=123, fileName="my-file.jpg")
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

    def list(self, **params: Any) -> ResponseData:
        """
        Convenience alias for list-style direct link GET requests.
        """
        return self.get(**params)

    def create(self, **fields: Any) -> ResponseData:
        """
        Convenience helper for DirectLinkPost using multipart form fields.
        """
        return self.post(form_data=fields)

    def update(self, id: PIXXIOId, **fields: Any) -> ResponseData:
        """
        Convenience helper for DirectLinkPut using multipart form fields.
        """
        return self.put(id=id, form_data=fields)

    def delete(
        self,
        id: Optional[PIXXIOId] = None,
        ids=None,
        **params: Any,
    ) -> ResponseData:
        """
        Delete one or more direct links.

        OpenAPI contract for DirectLinksDelete requires query parameter ``ids``.
        This wrapper keeps compatibility with ``delete(id=...)`` and maps it
        to ``ids=[id]``.
        """
        if id is not None and ids is not None:
            raise ValueError("Use either 'id' or 'ids', not both.")

        delete_params = dict(params)
        if ids is not None:
            delete_params["ids"] = ids
        elif id is not None:
            delete_params["ids"] = [id]
        elif "ids" not in delete_params:
            raise ValueError("'ids' is required for directlinks.delete().")

        return self._delete(endpoint_base=self.endpoint_base, **delete_params)
    
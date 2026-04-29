from typing import Any, Optional

from ._base import ResourceBase
from .pixxio_types import PIXXIOId, ResponseData


class ExternalShareCreateBuilder:
    """Builder for ExternalSharePost form fields."""

    def __init__(self):
        self._fields = {}

    def allow_comments(self, value: bool):
        self._fields["allowComments"] = value
        return self

    def allow_downloads(self, value: bool):
        self._fields["allowDownloads"] = value
        return self

    def allow_upvotes(self, value: bool):
        self._fields["allowUpvotes"] = value
        return self

    def collection_id(self, value: int):
        self._fields["collectionID"] = value
        return self

    def description(self, value: str):
        self._fields["description"] = value
        return self

    def download_format_ids(self, value: list):
        self._fields["downloadFormatIDs"] = value
        return self

    def emails(self, value: list):
        self._fields["emails"] = value
        return self

    def export_proof(self, value: bool):
        self._fields["exportProof"] = value
        return self

    def file_details(self, value: list):
        self._fields["fileDetails"] = value
        return self

    def file_ids(self, value: list):
        self._fields["fileIDs"] = value
        return self

    def force_download_proof(self, value: bool):
        self._fields["forceDownloadProof"] = value
        return self

    def force_watermark(self, value: bool):
        self._fields["forceWatermark"] = value
        return self

    def has_download_format_free(self, value: bool):
        self._fields["hasDownloadFormatFree"] = value
        return self

    def has_download_format_original(self, value: bool):
        self._fields["hasDownloadFormatOriginal"] = value
        return self

    def has_download_format_preview(self, value: bool):
        self._fields["hasDownloadFormatPreview"] = value
        return self

    def media_views(self, value: list):
        self._fields["mediaViews"] = value
        return self

    def name(self, value: str):
        self._fields["name"] = value
        return self

    def notification_text(self, value: str):
        self._fields["notificationText"] = value
        return self

    def password(self, value: str):
        self._fields["password"] = value
        return self

    def terms_of_use(self, value: str):
        self._fields["termsOfUse"] = value
        return self

    def validity_period(self, value: int):
        self._fields["validityPeriod"] = value
        return self

    def set(self, key, value):
        self._fields[key] = value
        return self

    def build(self):
        return dict(self._fields)


class ExternalShareUpdateBuilder:
    """Builder for ExternalSharePut form fields."""

    def __init__(self):
        self._fields = {}

    def allow_comments(self, value: bool):
        self._fields["allowComments"] = value
        return self

    def allow_downloads(self, value: bool):
        self._fields["allowDownloads"] = value
        return self

    def allow_upvotes(self, value: bool):
        self._fields["allowUpvotes"] = value
        return self

    def description(self, value: str):
        self._fields["description"] = value
        return self

    def download_format_ids_to_add(self, value: list):
        self._fields["downloadFormatIDsToAdd"] = value
        return self

    def download_format_ids_to_remove(self, value: list):
        self._fields["downloadFormatIDsToRemove"] = value
        return self

    def emails_to_add(self, value: list):
        self._fields["emailsToAdd"] = value
        return self

    def file_details_to_add(self, value: list):
        self._fields["fileDetailsToAdd"] = value
        return self

    def file_details_to_remove(self, value: list):
        self._fields["fileDetailsToRemove"] = value
        return self

    def file_ids_to_add(self, value: list):
        self._fields["fileIDsToAdd"] = value
        return self

    def file_ids_to_remove(self, value: list):
        self._fields["fileIDsToRemove"] = value
        return self

    def force_download_proof(self, value: bool):
        self._fields["forceDownloadProof"] = value
        return self

    def force_watermark(self, value: bool):
        self._fields["forceWatermark"] = value
        return self

    def has_download_format_free(self, value: bool):
        self._fields["hasDownloadFormatFree"] = value
        return self

    def has_download_format_original(self, value: bool):
        self._fields["hasDownloadFormatOriginal"] = value
        return self

    def has_download_format_preview(self, value: bool):
        self._fields["hasDownloadFormatPreview"] = value
        return self

    def is_disabled(self, value: bool):
        self._fields["isDisabled"] = value
        return self

    def media_views_to_add(self, value: list):
        self._fields["mediaViewsToAdd"] = value
        return self

    def media_views_to_remove(self, value: list):
        self._fields["mediaViewsToRemove"] = value
        return self

    def name(self, value: str):
        self._fields["name"] = value
        return self

    def notification_text(self, value: str):
        self._fields["notificationText"] = value
        return self

    def password(self, value: str):
        self._fields["password"] = value
        return self

    def terms_of_use(self, value: str):
        self._fields["termsOfUse"] = value
        return self

    def truncate_description(self, value: bool = True):
        self._fields["truncateDescription"] = value
        return self

    def truncate_notification_text(self, value: bool = True):
        self._fields["truncateNotificationText"] = value
        return self

    def truncate_password(self, value: bool = True):
        self._fields["truncatePassword"] = value
        return self

    def truncate_terms_of_use(self, value: bool = True):
        self._fields["truncateTermsOfUse"] = value
        return self

    def validity_period(self, value: int):
        self._fields["validityPeriod"] = value
        return self

    def set(self, key, value):
        self._fields[key] = value
        return self

    def build(self):
        return dict(self._fields)


class ExternalShareDeleteBuilder:
    """Builder for ExternalSharesDelete query fields."""

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
            raise ValueError("'ids' is required for ExternalSharesDelete.")
        return dict(self._fields)


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

    def list(self, **params: Any) -> ResponseData:
        return self.get(**params)

    def create(self, **fields: Any) -> ResponseData:
        return self.post(form_data=fields)

    def update(self, id: PIXXIOId, **fields: Any) -> ResponseData:
        return self.put(id=id, form_data=fields)

    def delete(
        self,
        id: Optional[PIXXIOId] = None,
        ids=None,
        **params: Any,
    ) -> ResponseData:
        if id is not None and ids is not None:
            raise ValueError("Use either 'id' or 'ids', not both.")

        delete_params = dict(params)
        if ids is not None:
            delete_params["ids"] = ids
        elif id is not None:
            delete_params["ids"] = [id]
        elif "ids" not in delete_params:
            raise ValueError("'ids' is required for externalshares.delete().")

        return self._delete(endpoint_base=self.endpoint_base, **delete_params)

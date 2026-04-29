from typing import Any, Optional

from ._base import ResourceBase
from .pixxio_types import PIXXIOId, ResponseData


class UploadLinkCreateBuilder:
    """Builder for UploadLinkPost form fields."""

    def __init__(self):
        self._fields = {}

    def description(self, value: str):
        self._fields["description"] = value
        return self

    def directory_id(self, value: int):
        self._fields["directoryID"] = value
        return self

    def emails(self, value: list):
        self._fields["emails"] = value
        return self

    def file_state_id(self, value: int):
        self._fields["fileStateID"] = value
        return self

    def keywords(self, value: list):
        self._fields["keywords"] = value
        return self

    def license_release_ids(self, value: list):
        self._fields["licenseReleaseIDs"] = value
        return self

    def model_release_ids(self, value: list):
        self._fields["modelReleaseIDs"] = value
        return self

    def name(self, value: str):
        self._fields["name"] = value
        return self

    def notification_text(self, value: str):
        self._fields["notificationText"] = value
        return self

    def property_release_ids(self, value: list):
        self._fields["propertyReleaseIDs"] = value
        return self

    def show_all_license_releases(self, value: bool):
        self._fields["showAllLicenseReleases"] = value
        return self

    def show_all_model_releases(self, value: bool):
        self._fields["showAllModelReleases"] = value
        return self

    def show_all_property_releases(self, value: bool):
        self._fields["showAllPropertyReleases"] = value
        return self

    def upload_condition(self, value: str):
        self._fields["uploadCondition"] = value
        return self

    def validity_period(self, value: int):
        self._fields["validityPeriod"] = value
        return self

    def set(self, key, value):
        self._fields[key] = value
        return self

    def build(self):
        return dict(self._fields)


class UploadLinkUpdateBuilder:
    """Builder for UploadLinkPut form fields."""

    def __init__(self):
        self._fields = {}

    def description(self, value: str):
        self._fields["description"] = value
        return self

    def directory_id(self, value: int):
        self._fields["directoryID"] = value
        return self

    def emails_to_add(self, value: list):
        self._fields["emailsToAdd"] = value
        return self

    def file_state_id(self, value: int):
        self._fields["fileStateID"] = value
        return self

    def files_to_add(self, value: list):
        self._fields["filesToAdd"] = value
        return self

    def is_disabled(self, value: bool):
        self._fields["isDisabled"] = value
        return self

    def keywords_to_add(self, value: list):
        self._fields["keywordsToAdd"] = value
        return self

    def keywords_to_remove(self, value: list):
        self._fields["keywordsToRemove"] = value
        return self

    def license_release_ids_to_add(self, value: list):
        self._fields["licenseReleaseIDsToAdd"] = value
        return self

    def license_release_ids_to_remove(self, value: list):
        self._fields["licenseReleaseIDsToRemove"] = value
        return self

    def model_release_ids_to_add(self, value: list):
        self._fields["modelReleaseIDsToAdd"] = value
        return self

    def model_release_ids_to_remove(self, value: list):
        self._fields["modelReleaseIDsToRemove"] = value
        return self

    def name(self, value: str):
        self._fields["name"] = value
        return self

    def notification_text(self, value: str):
        self._fields["notificationText"] = value
        return self

    def property_release_ids_to_add(self, value: list):
        self._fields["propertyReleaseIDsToAdd"] = value
        return self

    def property_release_ids_to_remove(self, value: list):
        self._fields["propertyReleaseIDsToRemove"] = value
        return self

    def show_all_license_releases(self, value: bool):
        self._fields["showAllLicenseReleases"] = value
        return self

    def show_all_model_releases(self, value: bool):
        self._fields["showAllModelReleases"] = value
        return self

    def show_all_property_releases(self, value: bool):
        self._fields["showAllPropertyReleases"] = value
        return self

    def truncate_description(self, value: bool = True):
        self._fields["truncateDescription"] = value
        return self

    def truncate_file_state_id(self, value: bool = True):
        self._fields["truncateFileStateID"] = value
        return self

    def truncate_notification_text(self, value: bool = True):
        self._fields["truncateNotificationText"] = value
        return self

    def truncate_upload_condition(self, value: bool = True):
        self._fields["truncateUploadCondition"] = value
        return self

    def upload_condition(self, value: str):
        self._fields["uploadCondition"] = value
        return self

    def validity_period(self, value: int):
        self._fields["validityPeriod"] = value
        return self

    def set(self, key, value):
        self._fields[key] = value
        return self

    def build(self):
        return dict(self._fields)


class UploadLinkDeleteBuilder:
    """Builder for UploadLinksDelete query fields."""

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
            raise ValueError("'ids' is required for UploadLinksDelete.")
        return dict(self._fields)


class UploadLink(ResourceBase):
    """
    Resource for managing upload links in PIXXIO.

    Upload links are pre-authenticated URLs that allow external parties to
    upload assets to a specific PIXXIO directory without requiring a full
    PIXXIO account. Each link can be restricted by expiry date, allowed file
    types, and maximum number of uploads.

    API endpoint: ``/api/v1/uploadLinks``

    Available operations (inherited):
        - ``get()``              – list all upload links
        - ``get(id)``            – retrieve a specific upload link by ID
        - ``post(json_data)``    – create a new upload link
        - ``put(id, json_data)`` – update an existing upload link
        - ``delete(id=id)``      – delete an upload link

    Example::

        from pixxio_client import Client
        from pixxio_client.uploadlinks import UploadLink

        client = Client.create_client("api-key", "company.pixxio.com")
        links = UploadLink(client)

        # Create an upload link for directory 10, valid for 14 days
        new_link = links.post(json_data={
            "directoryId": 10,
            "validDays": 14,
        })
        print(new_link.url)

        # List all existing upload links
        all_links = links.get()

        # Remove a link
        links.delete(id=new_link.id)

    Response field filtering::

        links.set_response_fields(["id", "url", "validUntil"])
        result = links.get()  # only returns the specified fields
    """

    NAME = "uploadLinks"

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
            raise ValueError("'ids' is required for uploadlinks.delete().")

        return self._delete(endpoint_base=self.endpoint_base, **delete_params)

from typing import Any, Optional

from ._base import ResourceBase
from .pixxio_types import PIXXIOId, ResponseData


class CollectionDeleteBuilder:
    """
    Builder for PIXXIO collection delete (CollectionsDelete) query fields.

    API contract requires ``ids``. This builder supports both ``id`` and
    ``ids`` helpers and normalizes to ``ids`` in build().
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
            raise ValueError("'ids' is required for CollectionsDelete.")
        return dict(self._fields)


class CollectionGetBuilder:
    """
    Builder for collection list/query parameters (CollectionsGet).
    """

    def __init__(self):
        self._params = {}

    def page(self, value: int):
        self._params["page"] = value
        return self

    def page_size(self, value: int):
        self._params["pageSize"] = value
        return self

    def collection_ids(self, value):
        self._params["collectionIDs"] = value
        return self

    def is_dynamic(self, value: bool):
        self._params["isDynamic"] = value
        return self

    def portal_id(self, value: int):
        self._params["portalID"] = value
        return self

    def search_term(self, value: str):
        self._params["searchTerm"] = value
        return self

    def with_file_id(self, value: int):
        self._params["withFileID"] = value
        return self

    def without_file_id(self, value: int):
        self._params["withoutFileID"] = value
        return self

    def show_subversions(self, value: bool):
        self._params["showSubVersions"] = value
        return self

    def response_fields(self, value):
        self._params["responseFields"] = value
        return self

    def sort_by(self, value: str):
        self._params["sortBy"] = value
        return self

    def sort_direction(self, value: str):
        self._params["sortDirection"] = value
        return self

    def user_ids(self, value):
        self._params["userIDs"] = value
        return self

    def has_indd_file(self, value: bool):
        self._params["hasInddFile"] = value
        return self

    def language(self, value: str):
        self._params["language"] = value
        return self

    def deactivate_translation_fallback(self, value: bool):
        self._params["deactivateTranslationFallback"] = value
        return self

    def user_response_fields(self, value):
        self._params["userResponseFields"] = value
        return self

    def shared_users_response_fields(self, value):
        self._params["sharedUsersResponseFields"] = value
        return self

    def shared_permission_groups_response_fields(self, value):
        self._params["sharedPermissionGroupsResponseFields"] = value
        return self

    def asset_navigator_response_fields(self, value):
        self._params["assetNavigatorResponseFields"] = value
        return self

    def preview_files_limit(self, value: int):
        self._params["previewFilesLimit"] = value
        return self

    def preview_files_filter(self, value):
        self._params["previewFilesFilter"] = value
        return self

    def preview_files_preview_file_options(self, value):
        self._params["previewFilesPreviewFileOptions"] = value
        return self

    def preview_files_response_fields(self, value):
        self._params["previewFilesResponseFields"] = value
        return self

    def set(self, key, value):
        self._params[key] = value
        return self

    def build(self):
        return dict(self._params)


class CollectionCreateBuilder:
    """
    Builder for collection creation form fields (CollectionPost).
    """

    def __init__(self):
        self._fields = {}

    def asset_navigator_id(self, value: int):
        self._fields["assetNavigatorID"] = value
        return self

    def asynchronous(self, value: bool):
        self._fields["async"] = value
        return self

    def create_date(self, value: str):
        self._fields["createDate"] = value
        return self

    def description(self, value: str):
        self._fields["description"] = value
        return self

    def file_ids(self, value):
        self._fields["fileIDs"] = value
        return self

    def filter_id(self, value: int):
        self._fields["filterID"] = value
        return self

    def internal_share_globally(self, value: bool):
        self._fields["internalShareGlobally"] = value
        return self

    def internal_share_message(self, value: str):
        self._fields["internalShareMessage"] = value
        return self

    def is_dynamic(self, value: bool):
        self._fields["isDynamic"] = value
        return self

    def name(self, value: str):
        self._fields["name"] = value
        return self

    def shared_permission_group_ids(self, value):
        self._fields["sharedPermissionGroupIDs"] = value
        return self

    def shared_user_ids(self, value):
        self._fields["sharedUserIDs"] = value
        return self

    def subscribe_collection(self, value: bool):
        self._fields["subscribeCollection"] = value
        return self

    def truncate_description(self, value: bool):
        self._fields["truncateDescription"] = value
        return self

    def set(self, key, value):
        self._fields[key] = value
        return self

    def build(self):
        return dict(self._fields)


class CollectionUpdateBuilder:
    """
    Builder for collection update form fields (CollectionPut).
    """

    def __init__(self):
        self._fields = {}

    def add_internal_shared_permission_group_ids(self, value):
        self._fields["addInternalSharedPermissionGroupIDs"] = value
        return self

    def add_internal_shared_user_ids(self, value):
        self._fields["addInternalSharedUserIDs"] = value
        return self

    def asset_navigator_id(self, value: int):
        self._fields["assetNavigatorID"] = value
        return self

    def description(self, value: str):
        self._fields["description"] = value
        return self

    def file_ids_to_add(self, value):
        self._fields["fileIDsToAdd"] = value
        return self

    def file_ids_to_remove(self, value):
        self._fields["fileIDsToRemove"] = value
        return self

    def internal_share_globally(self, value: bool):
        self._fields["internalShareGlobally"] = value
        return self

    def internal_share_message(self, value: str):
        self._fields["internalShareMessage"] = value
        return self

    def name(self, value: str):
        self._fields["name"] = value
        return self

    def preview_file_ids(self, value):
        self._fields["previewFileIDs"] = value
        return self

    def remove_internal_shared_permission_group_ids(self, value):
        self._fields["removeInternalSharedPermissionGroupIDs"] = value
        return self

    def remove_internal_shared_user_ids(self, value):
        self._fields["removeInternalSharedUserIDs"] = value
        return self

    def truncate_asset_navigator_id(self, value: bool):
        self._fields["truncateAssetNavigatorID"] = value
        return self

    def truncate_description(self, value: bool):
        self._fields["truncateDescription"] = value
        return self

    def user_id(self, value: int):
        self._fields["userID"] = value
        return self

    def set(self, key, value):
        self._fields[key] = value
        return self

    def build(self):
        return dict(self._fields)


class Collection(ResourceBase):
    """
    Resource for managing file collections in PIXXIO.

    Collections are named groupings of assets that allow users to organise
    files independently of the folder/directory structure. A collection can
    contain any number of files and can be shared or reused across projects.

    API endpoint: ``/api/v1/collections``

    Available operations:
        - ``get()``              – list all accessible collections
        - ``get(id)``            – retrieve a specific collection by ID
        - ``post(json_data)``    – create a new collection
        - ``put(id, json_data)`` – update an existing collection
        - ``delete(id=...)``     – delete one collection (compatibility helper)
        - ``delete(ids=[...])``  – delete one or more collections (API contract)

    Example::

        from pixxio_client import Client
        from pixxio_client.collections import Collection

        client = Client.create_client("api-key", "company.pixxio.com")
        collections = Collection(client)

        # List all collections
        all_cols = collections.get()

        # Create a new collection
        new_col = collections.post(json_data={"name": "My Collection"})

        # Update collection name
        collections.put(new_col.id, json_data={"name": "Renamed Collection"})

        # Delete collection
        collections.delete(id=new_col.id)

    Response field filtering::

        collections.set_response_fields(["id", "name", "filesQuantity"])
        result = collections.get()  # only returns the specified fields
    """

    NAME = "collections"

    def list(self, **params: Any) -> ResponseData:
        """
        Convenience alias for list-style collection GET requests.
        """
        return self.get(**params)

    def create(self, **fields: Any) -> ResponseData:
        """
        Convenience helper for CollectionPost using multipart form fields.
        """
        return self.post(form_data=fields)

    def update(self, id: PIXXIOId, **fields: Any) -> ResponseData:
        """
        Convenience helper for CollectionPut using multipart form fields.
        """
        return self.put(id=id, form_data=fields)

    def delete(
        self,
        id: Optional[PIXXIOId] = None,
        ids=None,
        **params: Any,
    ) -> ResponseData:
        """
        Delete one or more collections.

        OpenAPI contract for CollectionsDelete requires query parameter ``ids``.
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
            raise ValueError("'ids' is required for collections.delete().")

        return self._delete(endpoint_base=self.endpoint_base, **delete_params)
    
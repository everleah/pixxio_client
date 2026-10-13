from pixxio_client import Client, Authentication
from pixxio_client.files import File
from pixxio_client.jobs import Job
from pixxio_client.metadata import StandardMetadata, CustomMetadata  # CustomMetadata: GET only, no update
import tempfile
import requests
import os

try:  # direct execution: python tests/<script>.py
    from credentials import require_api_key, test_host
except ImportError:  # module execution: python -m tests.<module>
    from tests.credentials import require_api_key, test_host

api_key = require_api_key()
host = test_host()
file_url = "https://www.w3.org/People/mimasa/test/imgformat/img/w3c_home.jpg"

# Example metadata values
standard_metadata_values = {
    # Replace with actual standard metadata IDs and values
    # e.g. "title": "Test Asset Title"
}

# NOTE: Custom metadata update is NOT supported by the PIXXIO API (GET only)
custom_metadata_values = {
    # Example: "customField1": "Custom Value" (read-only)
}


auth = Authentication(api_key)
client = Client(auth, host)
files = File(client)

# Download remote file to temp location
with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
    response = requests.get(file_url)
    response.raise_for_status()
    tmp_file.write(response.content)
    tmp_file_path = tmp_file.name



# Use builder classes to prepare test metadata
from pixxio_client.metadata import StandardMetadataBuilder, CustomMetadataBuilder

standard_builder = StandardMetadataBuilder(client)
for item in standard_builder.metadata_fields_info:
    field_name = getattr(item, "name", None)
    field_type = getattr(item, "editType", None)
    selection_options = getattr(item, "selectionOptions", None)
    if field_name:
        if field_type == "text":
            standard_builder.add(field_name, f"Test value for {field_name}")
        elif field_type == "number":
            standard_builder.add(field_name, 42)
        elif field_type == "boolean":
            standard_builder.add(field_name, True)
        elif field_type == "date":
            standard_builder.add(field_name, "2025-10-21")
        elif field_type == "selection" and selection_options:
            # Pick the first available option name or id
            opt = selection_options[0] if isinstance(selection_options, list) and selection_options else None
            if isinstance(opt, dict) and "id" in opt:
                standard_builder.add(field_name, opt["id"])
            elif isinstance(opt, int):
                standard_builder.add(field_name, opt)
            elif isinstance(opt, str):
                standard_builder.add(field_name, opt)
        elif field_type == "multiselection" and selection_options:
            # Pick the first available option as a list
            opt = selection_options[0] if isinstance(selection_options, list) and selection_options else None
            if isinstance(opt, dict) and "id" in opt:
                standard_builder.add(field_name, [opt["id"]])
            elif isinstance(opt, int):
                standard_builder.add(field_name, [opt])
            elif isinstance(opt, str):
                standard_builder.add(field_name, [opt])
        else:
            standard_builder.add(field_name, f"Test value for {field_name} [{field_type}]")
test_standard_metadata = standard_builder.build()

custom_builder = CustomMetadataBuilder(client)
for item in custom_builder.metadata_fields_info:
    field_name = getattr(item, "name", None)
    field_type = getattr(item, "type", None)
    edit_type = getattr(item, "editType", None)
    selection_options = getattr(item, "selectionOptions", None) or getattr(item, "selectionTerms", None)
    if field_name:
        if edit_type == "multiselection" and selection_options:
            opt = selection_options[0] if isinstance(selection_options, list) and selection_options else None
            if isinstance(opt, dict) and "id" in opt:
                custom_builder.add(field_name, [opt["id"]])
            elif isinstance(opt, int):
                custom_builder.add(field_name, [opt])
            elif isinstance(opt, str):
                custom_builder.add(field_name, [opt])
        elif edit_type == "selection" and selection_options:
            opt = selection_options[0] if isinstance(selection_options, list) and selection_options else None
            if isinstance(opt, dict) and "id" in opt:
                custom_builder.add(field_name, opt["id"])
            elif isinstance(opt, int):
                custom_builder.add(field_name, opt)
            elif isinstance(opt, str):
                custom_builder.add(field_name, opt)
        elif field_type == "text":
            custom_builder.add(field_name, f"Custom test value for {field_name}")
        elif field_type == "number":
            custom_builder.add(field_name, 99)
        elif field_type == "boolean":
            custom_builder.add(field_name, False)
        elif field_type == "date":
            custom_builder.add(field_name, "2025-10-21")
        else:
            custom_builder.add(field_name, f"Custom test value for {field_name}")
test_custom_metadata = custom_builder.build()


# Upload asset from local temp file and set metadata in one step using high-level client method


from pixxio_client.files import FileUploadBuilder
import pprint


# Use the builder to construct the upload form fields
metadata_standard_payload = test_standard_metadata
metadata_custom_payload = test_custom_metadata
form_data = (
    FileUploadBuilder()
        #.metadata_standard(metadata_standard_payload)
        .metadata_custom(metadata_custom_payload)
        .build()
)
print("Uploading with metadataStandard:")
pprint.pprint(metadata_standard_payload)
print("Uploading with metadataCustom:")
pprint.pprint(metadata_custom_payload)
result = files.upload_and_wait(tmp_file_path, **form_data)
print("Upload result:")
pprint.pprint(result)

import types
# Try to extract asset ID from result, handling duplicateInfo if present
asset_id = None
duplicate_info = None
if isinstance(result, dict):
    asset_id = result.get("asset_id") or result.get("id") or result.get("fileId")
    duplicate_info = result.get("duplicateInfo")
    if duplicate_info and isinstance(duplicate_info, dict):
        asset_id = duplicate_info.get("existingFileID", asset_id)
elif isinstance(result, types.SimpleNamespace):
    asset_id = getattr(result, "asset_id", None) or getattr(result, "id", None) or getattr(result, "fileId", None)
    duplicate_info = getattr(result, "duplicateInfo", None)
    if duplicate_info:
        # duplicateInfo may be a dict or SimpleNamespace
        if isinstance(duplicate_info, dict):
            asset_id = duplicate_info.get("existingFileID", asset_id)
        else:
            asset_id = getattr(duplicate_info, "existingFileID", asset_id)

if asset_id:
    print(f"Fetching metadata for uploaded asset ID: {asset_id} using fileGet...")
    # Use fileGet endpoint with responseFields for all metadata
    response_fields = [
        "id", "fileName", "metadataFields", "metadata", "importantMetadata", "unimportantMetadata"
    ]
    # Use correct query parameter name: responseFields (case-sensitive)
    file_get_params = [("responseFields", field) for field in response_fields]
    file_get_url = f"{client.location_base}/files/{asset_id}"
    file_get_headers = {"Authorization": f"Bearer {api_key}"}
    import requests
    file_get_response = requests.get(file_get_url, params=file_get_params, headers=file_get_headers)
    print(f"fileGet status: {file_get_response.status_code}")
    try:
        file_get_json = file_get_response.json()
    except Exception as e:
        print(f"Failed to parse fileGet response: {e}")
        file_get_json = None
    print("Fetched file metadata (fileGet with all metadata fields):")
    pprint.pprint(file_get_json)
else:
    print("Could not extract asset ID from upload result; skipping metadata fetch.")

# Clean up temp file
os.unlink(tmp_file_path)

# try to update metadata using File.update 
from pixxio_client.files import FileUpdateBuilder

form_data = (
    FileUpdateBuilder()
        .description("Updated description via File.update")
        .metadata_standard(metadata_standard_payload)
        .metadata_custom(metadata_custom_payload)
        .build()
)   

if asset_id:
    # Ensure asset_id is an integer for the update call
    try:
        asset_id_int = int(asset_id)
    except Exception:
        asset_id_int = asset_id
    import json

    # Try updating with both
    print("\n--- Attempting update with both metadataStandard and metadataCustom ---")
    try:
        update_result_both = files.update(ids=[asset_id_int], **form_data)
        print("Update result:")
        pprint.pprint(update_result_both)
    except Exception as e:
        print("Exception:", e)

    # Now test each custom metadata field individually to find the problematic one
    print("\n--- Testing each custom metadata field individually for IDArray error ---")
    for meta_item in metadata_custom_payload:
        single_form_data = (
            FileUpdateBuilder()
                .description("Test single custom metadata field")
                .metadata_custom([meta_item])
                .build()
        )
        try:
            result = files.update(ids=[asset_id_int], **single_form_data)
            print(f"CustomMetadata ID {meta_item['id']} update result: success")
        except Exception as e:
            print(f"CustomMetadata ID {meta_item['id']} update result: Exception: {e}")
            print("Item causing error:")
            pprint.pprint(meta_item)

# PIXXIO Python Client - Metadata Builder Usage

## Metadata Builder Classes

The PIXXIO Python client provides builder classes to simplify the construction of metadata payloads for both standard and custom metadata fields. These builders ensure that values are correctly formatted according to the field type and API requirements.

### StandardMetadataBuilder
- Dynamically loads all available standard metadata fields from the API.
- Provides methods to add, replace, or remove metadata values by field name.
- Handles type conversion and value mapping for selection/multiselection fields.

### CustomMetadataBuilder
- Dynamically loads all available custom metadata fields from the API.
- Provides methods to add, replace, or remove metadata values by field name.
- Handles type conversion and value mapping for selection/multiselection fields.

## Example Usage

```python
from pixxio_client import Client
from pixxio_client.metadata import StandardMetadataBuilder, CustomMetadataBuilder

client = Client(api_key, host)

# Build standard metadata
standard_builder = StandardMetadataBuilder(client)
standard_builder.add("Title", "Test Asset Title")
standard_builder.add("DateCreated", "2025-10-21")
# For selection/multiselection fields, use the option name or id
standard_builder.add("Category", [12345])
standard_metadata_payload = standard_builder.build()

# Build custom metadata
custom_builder = CustomMetadataBuilder(client)
custom_builder.add("Produktbereich", [98765])  # multiselection field
custom_builder.add("Artikelnummer", "123-ABC")
custom_metadata_payload = custom_builder.build()

# Use in file upload or update
from pixxio_client.files import FileUploadBuilder
form_data = (
    FileUploadBuilder()
        .metadata_standard(standard_metadata_payload)
        .metadata_custom(custom_metadata_payload)
        .build()
)
```

## Benefits
- Ensures correct value formatting for all metadata field types
- Reduces boilerplate and manual mapping
- Automatically fetches field definitions from the API
- Supports all field types, including text, date, selection, and multiselection

## See Also
- [API Reference](API_REFERENCE.md)
- [Developer Guide](DEVELOPER_GUIDE.md)
- [tests/test_upload_with_metadata.py](../tests/test_upload_with_metadata.py) for a full example

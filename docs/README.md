# Metadata Builder Classes

The PIXXIO Python client provides builder classes to simplify the construction of metadata payloads for both standard and custom metadata fields. These builders ensure correct formatting and type handling for all field types, including text, date, selection, and multiselection.

## Usage

- Use `StandardMetadataBuilder` to build payloads for standard metadata fields.
- Use `CustomMetadataBuilder` to build payloads for custom metadata fields.
- These builders automatically fetch field definitions from the API and handle value conversion for selection/multiselection fields.

## Example

```python
from pixxio_client.metadata import StandardMetadataBuilder, CustomMetadataBuilder

standard_builder = StandardMetadataBuilder(client)
standard_builder.add("Title", "Test Asset Title")
standard_metadata_payload = standard_builder.build()

custom_builder = CustomMetadataBuilder(client)
custom_builder.add("Produktbereich", [98765])
custom_metadata_payload = custom_builder.build()
```

See [../tests/test_upload_with_metadata.py](../tests/test_upload_with_metadata.py) for a full example.

## Benefits
- Ensures correct value formatting for all metadata field types
- Reduces boilerplate and manual mapping
- Automatically fetches field definitions from the API
- Supports all field types, including text, date, selection, and multiselection

## References
- [API Reference](API_REFERENCE.md)
- [Developer Guide](DEVELOPER_GUIDE.md)

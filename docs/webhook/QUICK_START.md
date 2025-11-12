# PIXXIO Webhook Parser - Quick Start (5 Minutes)

**Updated:** November 12, 2025  
**For:** Getting started with webhook event handling

## Install & Import

```python
# The parser is part of pixxio_client
from pixxio_client.webhook_parser import WebhookParser, WebhookEvent
```

## Basic Usage (30 seconds)

```python
parser = WebhookParser()

# Parse webhook JSON
events = parser.parse_webhook(webhook_json)

# Process events
for event in events:
    print(f"Event: {event.event_key}")
    print(f"User: {event.user.email}")
    print(f"Data: {event.data.raw}")
```

## Handle Metadata Changes (1 minute)

```python
for event in events:
    # Text field changed
    if event.event_key == 'fileModifiedMetadataFieldText':
        field_name = event.data.name
        new_value = event.data.new_text
        print(f"Updated {field_name} to: {new_value}")
```

## Safe Data Access (1 minute)

```python
# Method 1: hasattr() check
if hasattr(event.data, 'new_text'):
    print(event.data.new_text)

# Method 2: getattr() with default
new_value = getattr(event.data, 'new_text', 'N/A')

# Method 3: Raw dict
data = event.data.raw  # Complete original data
```

## Real-World Example (2 minutes)

```python
from flask import Flask, request
from pixxio_client.webhook_parser import WebhookParser

app = Flask(__name__)
parser = WebhookParser()

@app.route('/webhook/pixxio', methods=['POST'])
def handle_webhook():
    """Receive and process PIXXIO webhooks."""
    webhook_data = request.get_json()
    events = parser.parse_webhook(webhook_data)
    
    for event in events:
        print(f"✓ {event.event_key} by {event.user.email}")
        
        # Handle specific event types
        if 'Metadata' in event.event_key and hasattr(event.data, 'new_text'):
            update_system(
                field=event.data.name,
                value=event.data.new_text
            )
    
    return {'status': 'ok'}, 200
```

## Key Points

✅ **One Parser, All Event Types**
- Single `WebhookParser` handles 200+ event types
- No need to check event class
- Future events work automatically

✅ **Flexible Data Access**
```python
# All these work
event.data.newText           # camelCase (API style)
event.data.new_text          # snake_case (Python style)
event.data.raw['newText']    # dict access
getattr(event.data, 'new_text', None)  # safe default
```

✅ **Use `hasattr()` for Optional Fields**
```python
if hasattr(event.data, 'new_text'):
    # Field exists, safe to access
    print(event.data.new_text)
```

## Common Event Types

| Event Key | Field | What It Is |
|---|---|---|
| `fileModifiedMetadataFieldText` | `name`, `new_text`, `old_text` | Text field changed |
| `fileModifiedMetadataFieldMultiSelectionsAdded` | `name`, `multi_selections_added` | Selections added |
| `fileModifiedFileStateID` | `new_file_state_id` | File state changed |
| `fileModifiedLanguageCodesAdded` | `language_codes_added` | Languages added |

## Event Structure

```python
event.id                    # Unique event ID
event.event_key            # Type: 'fileModifiedMetadataFieldText', etc.
event.action               # 'CREATED', 'UPDATED', 'DELETED'
event.resource             # 'File', 'Collection', etc.
event.user.email           # Who made the change
event.timestamp            # When it happened
event.data.raw             # Complete event data
```

## Troubleshooting

**AttributeError on `event.data.field_name`?**
- Use `hasattr()` first: `if hasattr(event.data, 'field')`
- Or use `getattr()`: `value = getattr(event.data, 'field', None)`
- Field might not exist for this event type

**Type checking warnings (Pylance)?**
- Use `getattr()` or `hasattr()` (works with type checkers)
- Or add `# type: ignore[attr-defined]` comment for direct access

**Unknown event type?**
- Still works! Use `event.data.raw` to access any data
- Works with future PIXXIO events automatically

## Next Steps

- 📖 **Full Guide:** See `PARSER_IMPLEMENTATION.md`
- 💡 **More Examples:** See `USAGE_EXAMPLES.md`
- 🧪 **View Tests:** `tests/test_webhook_parser_generalized.py`

## One More Example

```python
def process_webhook(request_data):
    """Complete webhook handler."""
    parser = WebhookParser()
    events = parser.parse_webhook(request_data)
    
    for event in events:
        # Extract info
        event_type = event.event_key
        user_email = event.user.email
        timestamp = event.timestamp
        data = event.data.raw
        
        # Log it
        print(f"{timestamp} | {event_type} | {user_email}")
        
        # Handle known events
        if event_type == 'fileModifiedMetadataFieldText':
            field_name = event.data.name
            new_value = event.data.new_text
            print(f"  → {field_name} = {new_value}")
        
        # Handle unknown events (future-proof!)
        elif event_type not in KNOWN_TYPES:
            print(f"  → Unknown event data: {data}")
    
    return 'OK'
```

That's it! You're ready to process PIXXIO webhooks. 🚀

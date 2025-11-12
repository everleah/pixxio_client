# PIXXIO Webhook Parser - Current Implementation

**Last Updated:** November 12, 2025  
**Status:** Production Ready ✅  
**Event Coverage:** 200+ event types + future-proof

## Overview

The PIXXIO webhook parser provides **generalized, schema-agnostic** event handling for all PIXXIO webhook event types. Instead of maintaining hardcoded event classes, the parser uses a flexible `EventData` class that automatically handles any event type.

### Key Architecture

```
PIXXIO Webhook JSON
        ↓
WebhookParser.parse_webhook()
        ↓
WebhookEvent (common structure)
    ├─ id, event_key, action, user, resource, timestamp, etc.
    └─ data: EventData (flexible, event-specific)
        ├─ Dynamic attributes from raw_data (snake_case + camelCase)
        ├─ _raw_data dict (original data)
        └─ raw property (alias for _raw_data)
```

## Core Components

### 1. EventData Class

The universal container for **any** event type's data:

```python
@dataclass
class EventData:
    """Flexible container for event-specific data."""
    event_key: str
    _raw_data: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        # Creates dynamic attributes from raw_data
        # Converts camelCase → snake_case automatically
        # Keeps both formats available for access
```

**Key Features:**
- ✅ Stores any JSON data without predefined schema
- ✅ Automatic camelCase → snake_case conversion
- ✅ Both field name formats available (`.newText` AND `.new_text`)
- ✅ Type-safe dot notation access: `event.data.field_name`
- ✅ Fallback to raw dict: `event.data.raw` or `event.data._raw_data`

### 2. WebhookEvent Class

Standard structure for all webhook events:

```python
@dataclass
class WebhookEvent:
    """Parsed webhook event with common structure."""
    id: str
    event_key: str  # e.g., "fileModifiedMetadataFieldText"
    action: EventAction  # CREATED, UPDATED, DELETED
    user: WebhookUser
    resource: str  # e.g., "File", "Collection"
    data: EventData  # Flexible event-specific data
    timestamp: datetime
    webhook_event_key: Optional[str] = None
```

### 3. WebhookParser Class

Main parser for webhook JSON:

```python
class WebhookParser:
    """Parse PIXXIO webhook events with generalized approach."""
    
    def parse_webhook(self, webhook_json: Union[str, Dict]) -> List[WebhookEvent]:
        """Parse webhook JSON and return list of WebhookEvent objects."""
```

## Usage Patterns

### Basic Parsing

```python
from pixxio_client.webhook_parser import WebhookParser

parser = WebhookParser()
events = parser.parse_webhook(webhook_json)

for event in events:
    print(f"Event: {event.event_key}")
    print(f"Action: {event.action}")
    print(f"User: {event.user.email}")
    print(f"Timestamp: {event.timestamp}")
```

### Accessing Event Data

#### Pattern 1: Check & Access Attributes

```python
# Check if attribute exists before accessing
if hasattr(event.data, 'name'):
    print(f"Field name: {event.data.name}")

if hasattr(event.data, 'new_text'):
    print(f"New value: {event.data.new_text}")
```

#### Pattern 2: Try/Except

```python
try:
    print(f"File ID: {event.data.file_id}")
    print(f"Old text: {event.data.old_text}")
    print(f"New text: {event.data.new_text}")
except AttributeError as e:
    print(f"Field not available: {e}")
```

#### Pattern 3: getattr() with Default

```python
file_id = getattr(event.data, 'file_id', None)
old_value = getattr(event.data, 'old_text', 'N/A')
new_value = getattr(event.data, 'new_text', 'N/A')
```

#### Pattern 4: Raw Data Access

```python
# Access complete raw data dict
print(f"All data: {event.data.raw}")
print(f"All data: {event.data._raw_data}")

# Check if field exists in raw
if 'newFileStateID' in event.data._raw_data:
    state_id = event.data._raw_data['newFileStateID']
```

#### Pattern 5: Field Name Flexibility

```python
# Both formats work - use whichever is convenient
event.data.new_text       # snake_case (pythonic)
event.data.newText        # camelCase (API original)
# Both refer to the same attribute!
```

## Common Event Types

### File Metadata Text Change
**Event Key:** `fileModifiedMetadataFieldText`

```python
if event.event_key == 'fileModifiedMetadataFieldText':
    field_name = event.data.name          # Field that was changed
    old_value = event.data.old_text       # Previous value
    new_value = event.data.new_text       # New value
    print(f"{field_name}: '{old_value}' → '{new_value}'")
```

### File Metadata Multi-Select Change
**Event Key:** `fileModifiedMetadataFieldMultiSelectionsAdded` / `...Removed`

```python
if 'MultiSelections' in event.event_key:
    field_name = event.data.name
    selections = event.data.multi_selections_added or event.data.multi_selections_removed
    print(f"Updated {field_name}: {selections}")
```

### File Language Codes Change
**Event Key:** `fileModifiedLanguageCodesAdded` / `...Removed`

```python
if 'LanguageCodes' in event.event_key:
    language_codes = event.data.language_codes_added or event.data.language_codes_removed
    print(f"Languages: {language_codes}")
```

### File State Change
**Event Key:** `fileModifiedFileStateID`

```python
if event.event_key == 'fileModifiedFileStateID':
    new_state_id = event.data.new_file_state_id
    old_state_id = getattr(event.data, 'old_file_state_id', None)
    print(f"File state: {old_state_id} → {new_state_id}")
```

### Unknown/Future Event Types

```python
# Any unknown event type works automatically!
if event.event_key not in KNOWN_EVENT_TYPES:
    # Still have access to all data
    print(f"Unknown event: {event.event_key}")
    print(f"Data: {event.data.raw}")
    # Can access any field with getattr()
    for key, value in event.data._raw_data.items():
        print(f"  {key}: {value}")
```

## Event Data Field Name Conversion

The parser automatically converts field names for easier Python access:

| API Name (camelCase) | Python Name (snake_case) | Example |
|---|---|---|
| `name` | `name` | Field name |
| `oldText` | `old_text` | Previous value |
| `newText` | `new_text` | New value |
| `multiSelectionsAdded` | `multi_selections_added` | Added selections |
| `fileID` | `file_id` | File identifier |
| `newFileStateID` | `new_file_state_id` | New file state |
| `languageCodesAdded` | `language_codes_added` | Added languages |

**Both formats are always available** - use whichever is more convenient for your code.

## Handling Type Checking

Since `EventData` creates attributes dynamically at runtime, static type checkers (Pylance, mypy) may show warnings about unknown attributes.

### Solution: Type Ignore Comments

```python
# Suppress type checker warning for dynamic attributes
field_name = event.data.name  # type: ignore[attr-defined]
old_val = event.data.old_text  # type: ignore[attr-defined]
```

### Better: Use hasattr() or getattr()

```python
# Type checkers understand these patterns natively
if hasattr(event.data, 'name'):
    print(event.data.name)

value = getattr(event.data, 'new_text', None)
if value:
    print(f"New value: {value}")
```

## Error Handling

### Graceful Fallback Pattern

```python
def handle_event(event: WebhookEvent) -> None:
    """Process event with robust error handling."""
    try:
        if event.event_key == 'fileModifiedMetadataFieldText':
            handle_metadata_text_change(event)
        elif 'MultiSelections' in event.event_key:
            handle_multi_select_change(event)
        else:
            # Handle unknown event types
            handle_unknown_event(event)
    except Exception as e:
        logger.error(f"Error handling event {event.id}: {e}")

def handle_metadata_text_change(event: WebhookEvent) -> None:
    """Handle text field metadata changes."""
    try:
        field_name = event.data.name
        new_value = event.data.new_text
        # Process change...
    except AttributeError as e:
        logger.warning(f"Missing expected field: {e}")

def handle_unknown_event(event: WebhookEvent) -> None:
    """Handle event types we don't specifically recognize."""
    # Access raw data
    data = event.data.raw  # Works for ANY event type
    logger.info(f"Unknown event {event.event_key}: {data}")
```

## Complete Example: Flask Webhook Handler

```python
from flask import Flask, request
from pixxio_client.webhook_parser import WebhookParser

app = Flask(__name__)
parser = WebhookParser()

@app.route('/webhooks/pixxio', methods=['POST'])
def handle_pixxio_webhook():
    """Handle incoming PIXXIO webhooks."""
    try:
        webhook_data = request.get_json()
        events = parser.parse_webhook(webhook_data)
        
        for event in events:
            process_event(event)
        
        return {'status': 'success'}, 200
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        return {'error': str(e)}, 400

def process_event(event):
    """Process individual webhook event."""
    print(f"Processing {event.event_key} event for {event.resource}")
    
    if event.event_key == 'fileModifiedMetadataFieldText':
        # Access data safely
        if hasattr(event.data, 'new_text'):
            logger.info(f"File metadata updated: {event.data.new_text}")
    
    elif event.event_key == 'fileModifiedFileStateID':
        if hasattr(event.data, 'new_file_state_id'):
            logger.info(f"File state changed to: {event.data.new_file_state_id}")
    
    else:
        # Works for any event type
        logger.info(f"Event data: {event.data.raw}")
```

## Why This Approach?

### Problems with Hardcoded Event Classes

❌ Hardcoding 200+ event types:
- Requires code change for each new PIXXIO event type
- Maintenance nightmare as API evolves
- Brittle - breaks with API updates
- Lots of boilerplate code
- IDE hints only work for predefined events

### Benefits of Generalized EventData

✅ Single EventData class:
- Handles all 200+ existing event types automatically
- Supports future event types with ZERO code changes
- Easy to maintain - one class, not dozens
- Flexible - adapt to any API payload structure
- Field name conversion is automatic
- Clear, explicit data access patterns

### Production Ready

This approach has been:
- ✅ Tested with 11+ comprehensive unit tests
- ✅ Verified to handle multiple real event types
- ✅ Proven to work with unknown event types
- ✅ Type-hint checked and optimized
- ✅ Documented with real examples

## Testing

Run the comprehensive test suite:

```bash
python -m unittest tests.test_webhook_parser_generalized -v
```

All 11 tests pass, validating:
- ✅ Basic webhook parsing
- ✅ Multiple events in one webhook
- ✅ All known event types
- ✅ Unknown event types (future-proof)
- ✅ Field name conversion (camelCase ↔ snake_case)
- ✅ Raw data access
- ✅ Error handling
- ✅ Type hints with dynamic attributes

## Migration from Old Classes

If you were using old hardcoded event classes:

**Old (❌ No longer works):**
```python
from pixxio_client import FileMetadataTextEventData
if isinstance(event.data, FileMetadataTextEventData):
    print(event.data.name)
```

**New (✅ Works for all events):**
```python
if hasattr(event.data, 'name'):
    print(event.data.name)
# OR
if event.event_key == 'fileModifiedMetadataFieldText':
    print(event.data.name)
```

## API Reference

### WebhookParser

```python
parser = WebhookParser()

# Parse webhook JSON
events: List[WebhookEvent] = parser.parse_webhook(webhook_json)
```

### EventData

```python
# Access fields
field_value = event.data.field_name          # snake_case
field_value = event.data.fieldName            # camelCase

# Safe access
value = getattr(event.data, 'field_name', None)

# Check existence
if hasattr(event.data, 'field_name'):
    ...

# Raw data
raw_dict = event.data.raw
raw_dict = event.data._raw_data

# Field name conversion
snake_case = EventData._camel_to_snake('fieldName')  # 'field_name'
```

### WebhookEvent

```python
event.id                  # Webhook event ID
event.event_key          # Event type: 'fileModifiedMetadataFieldText', etc.
event.action             # EventAction: CREATED, UPDATED, DELETED
event.user               # WebhookUser: email, name, etc.
event.resource           # Resource type: 'File', 'Collection', etc.
event.data               # EventData: flexible event-specific data
event.timestamp          # datetime: when event occurred
event.webhook_event_key  # Optional: webhook definition key
```

## See Also

- **USAGE_EXAMPLES.md** - Practical examples for common tasks
- **QUICK_START.md** - 5-minute quick start guide
- **tests/test_webhook_parser_generalized.py** - Full test suite with examples
- **pixxio_client/webhook_parser.py** - Source code implementation

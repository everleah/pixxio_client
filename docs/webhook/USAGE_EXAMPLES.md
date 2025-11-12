# PIXXIO Webhook Parser - Usage Examples

**Updated:** November 12, 2025  
**Focus:** Practical patterns for common webhook scenarios

## Quick Examples

### Example 1: Simple Event Logging

Log all webhook events with their data:

```python
from pixxio_client.webhook_parser import WebhookParser
import json

parser = WebhookParser()

def log_webhook_events(webhook_json):
    """Log all events from a webhook."""
    events = parser.parse_webhook(webhook_json)
    
    for event in events:
        print(f"Event ID: {event.id}")
        print(f"Type: {event.event_key}")
        print(f"Action: {event.action}")
        print(f"Resource: {event.resource}")
        print(f"User: {event.user.email}")
        print(f"Timestamp: {event.timestamp}")
        print(f"Data: {event.data.raw}")
        print("-" * 50)
```

### Example 2: Handle Metadata Changes

Process file metadata field changes:

```python
def handle_metadata_change(event):
    """Handle metadata field changes."""
    if event.event_key == 'fileModifiedMetadataFieldText':
        # These fields are always present for this event type
        field_name = event.data.name
        old_value = event.data.old_text
        new_value = event.data.new_text
        
        print(f"Field '{field_name}' changed:")
        print(f"  Old: {old_value}")
        print(f"  New: {new_value}")
        print(f"  By: {event.user.email}")
        print(f"  At: {event.timestamp}")
        
        # Update your system
        update_file_metadata(
            field_name=field_name,
            new_value=new_value,
            old_value=old_value,
            updated_by=event.user.email
        )
```

### Example 3: Filter Events by Type

Process only specific event types:

```python
def process_file_events(webhook_json):
    """Process only file-related events."""
    parser = WebhookParser()
    events = parser.parse_webhook(webhook_json)
    
    file_events = [e for e in events if e.resource == 'File']
    metadata_events = [e for e in events if 'Metadata' in e.event_key]
    
    print(f"Total events: {len(events)}")
    print(f"File events: {len(file_events)}")
    print(f"Metadata changes: {len(metadata_events)}")
    
    for event in metadata_events:
        print(f"  - {event.event_key}: {event.data.name}")
```

### Example 4: Safe Data Access

Safely access optional event fields:

```python
def safe_data_access(event):
    """Access event data with safe defaults."""
    
    # Pattern 1: hasattr() check
    if hasattr(event.data, 'file_id'):
        file_id = event.data.file_id
    
    # Pattern 2: getattr() with default
    file_id = getattr(event.data, 'file_id', None)
    old_name = getattr(event.data, 'old_text', 'N/A')
    new_name = getattr(event.data, 'new_text', 'N/A')
    
    # Pattern 3: Direct access with try/except
    try:
        print(f"File: {event.data.file_id}")
    except AttributeError:
        print("File ID not available for this event")
    
    # Pattern 4: Check in raw data
    if 'newFileStateID' in event.data._raw_data:
        state_id = event.data._raw_data['newFileStateID']
```

### Example 5: Handle Multiple Event Types

Handle different event types in a router:

```python
def route_webhook_event(event):
    """Route event to appropriate handler based on type."""
    
    handlers = {
        'fileModifiedMetadataFieldText': handle_text_metadata,
        'fileModifiedMetadataFieldMultiSelectionsAdded': handle_multi_select,
        'fileModifiedFileStateID': handle_file_state,
        'fileModifiedLanguageCodesAdded': handle_language_codes,
    }
    
    # Try specific handler
    handler = handlers.get(event.event_key)
    if handler:
        handler(event)
    else:
        # Fallback for unknown events
        handle_unknown_event(event)

def handle_text_metadata(event):
    """Handle text field metadata changes."""
    print(f"Text field changed: {event.data.name}")
    print(f"  From: {event.data.old_text}")
    print(f"  To: {event.data.new_text}")

def handle_multi_select(event):
    """Handle multi-select metadata changes."""
    selections = event.data.multi_selections_added or event.data.multi_selections_removed
    print(f"Multi-select updated: {event.data.name}")
    print(f"  Values: {selections}")

def handle_file_state(event):
    """Handle file state changes."""
    new_state = event.data.new_file_state_id
    old_state = getattr(event.data, 'old_file_state_id', 'unknown')
    print(f"File state: {old_state} → {new_state}")

def handle_language_codes(event):
    """Handle language code changes."""
    codes = event.data.language_codes_added or event.data.language_codes_removed
    print(f"Languages: {codes}")

def handle_unknown_event(event):
    """Handle event types we don't recognize."""
    print(f"Unknown event: {event.event_key}")
    print(f"Data: {event.data.raw}")
```

### Example 6: Batch Processing with Error Handling

Process webhook events with robust error handling:

```python
from logging import getLogger

logger = getLogger(__name__)

def process_webhook_batch(webhook_json):
    """Process all events with error handling."""
    parser = WebhookParser()
    
    try:
        events = parser.parse_webhook(webhook_json)
    except Exception as e:
        logger.error(f"Failed to parse webhook: {e}")
        return False
    
    processed = 0
    failed = 0
    
    for event in events:
        try:
            process_single_event(event)
            processed += 1
        except Exception as e:
            logger.error(f"Error processing event {event.id}: {e}")
            failed += 1
    
    logger.info(f"Webhook processing: {processed} success, {failed} failed")
    return failed == 0

def process_single_event(event):
    """Process a single event with detailed error info."""
    try:
        # Validate required fields
        if not event.id or not event.event_key:
            raise ValueError("Missing required event fields")
        
        # Route to handler
        if 'Metadata' in event.event_key:
            if hasattr(event.data, 'new_text'):
                update_metadata_cache(event)
        
        elif event.event_key == 'fileModifiedFileStateID':
            if hasattr(event.data, 'new_file_state_id'):
                update_file_state(event)
        
        else:
            logger.debug(f"Unhandled event type: {event.event_key}")
    
    except AttributeError as e:
        logger.warning(f"Missing event data field: {e}")
    except Exception as e:
        logger.error(f"Event processing error: {e}", exc_info=True)
        raise
```

### Example 7: Work with Raw JSON Data

Access original raw data when needed:

```python
def inspect_event_raw_data(event):
    """Inspect original JSON structure."""
    
    # Get complete raw data dict
    raw_dict = event.data.raw  # or event.data._raw_data
    
    print(f"Event: {event.event_key}")
    print(f"Raw data keys: {list(raw_dict.keys())}")
    print(f"Full raw data: {json.dumps(raw_dict, indent=2)}")
    
    # Check for specific keys
    if 'newText' in raw_dict:
        print(f"New text (camelCase): {raw_dict['newText']}")
    
    if 'new_text' in raw_dict:
        print(f"New text (snake_case): {raw_dict['new_text']}")
    
    # Iterate all fields
    for key, value in raw_dict.items():
        print(f"  {key}: {value} (type: {type(value).__name__})")
```

### Example 8: Field Name Flexibility

Use both camelCase and snake_case:

```python
def field_name_examples(event):
    """Show both naming conventions work."""
    
    # These all work the same way!
    # Original API camelCase names
    name1 = event.data.newText
    name2 = event.data.newFileStateID
    name3 = event.data.multiSelectionsAdded
    
    # Pythonic snake_case names
    name1_py = event.data.new_text
    name2_py = event.data.new_file_state_id
    name3_py = event.data.multi_selections_added
    
    # They're identical
    assert name1 == name1_py
    assert name2 == name2_py
    assert name3 == name3_py
    
    # Choose whichever fits your code style
    # For new code, prefer snake_case (more Pythonic)
```

### Example 9: Database Integration

Store webhook events in database:

```python
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class WebhookEventRecord(Base):
    """Store parsed webhook events in database."""
    __tablename__ = 'webhook_events'
    
    id = Column(String, primary_key=True)
    event_key = Column(String, index=True)
    resource = Column(String)
    action = Column(String)
    user_email = Column(String)
    data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

def save_webhook_to_db(webhook_json, db_session):
    """Parse and save webhook events to database."""
    parser = WebhookParser()
    events = parser.parse_webhook(webhook_json)
    
    for event in events:
        record = WebhookEventRecord(
            id=event.id,
            event_key=event.event_key,
            resource=event.resource,
            action=str(event.action),
            user_email=event.user.email,
            data=event.data.raw,
            created_at=event.timestamp
        )
        db_session.add(record)
    
    db_session.commit()
```

### Example 10: Async Webhook Handler (FastAPI)

Handle webhooks asynchronously:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pixxio_client.webhook_parser import WebhookParser
import asyncio

app = FastAPI()
parser = WebhookParser()

class WebhookPayload(BaseModel):
    """Webhook request body."""
    pass

@app.post("/webhooks/pixxio")
async def handle_pixxio_webhook(payload: dict):
    """Handle PIXXIO webhook asynchronously."""
    try:
        events = parser.parse_webhook(payload)
        
        # Process events in background
        tasks = [process_event_async(e) for e in events]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check for errors
        errors = [r for r in results if isinstance(r, Exception)]
        if errors:
            raise HTTPException(status_code=400, detail=f"{len(errors)} events failed")
        
        return {"status": "received", "count": len(events)}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

async def process_event_async(event):
    """Process single event asynchronously."""
    # Simulate async processing
    await asyncio.sleep(0.1)
    
    if event.event_key == 'fileModifiedMetadataFieldText':
        # Async operations here
        await update_file_async(event)
    
    return event.id

async def update_file_async(event):
    """Async file update."""
    # Your async code here
    pass
```

## Best Practices

### ✅ Do:

```python
# Use getattr() or hasattr() for optional fields
value = getattr(event.data, 'field_name', None)

# Check field existence
if hasattr(event.data, 'field_name'):
    process(event.data.field_name)

# Use event_key for type-specific logic
if event.event_key == 'fileModifiedMetadataFieldText':
    handle_text_change(event)

# Access raw data for debugging
raw = event.data.raw
logger.debug(f"Raw data: {raw}")

# Use snake_case for new code (more Pythonic)
new_text = event.data.new_text
```

### ❌ Don't:

```python
# Don't directly access without checking
value = event.data.field_name  # May not exist!

# Don't assume all events have same fields
state_id = event.data.new_file_state_id  # Some events don't have this

# Don't use old hardcoded classes (they don't exist)
from pixxio_client import FileMetadataTextEventData  # ❌ Error!

# Don't ignore attribute errors
try:
    value = event.data.field_name
except:  # ❌ Too broad
    pass

# Don't parse raw JSON yourself
json.loads(webhook_string)  # Use parser instead!
```

## Common Patterns

### Pattern 1: Event Filtering

```python
# Filter by event type
def get_metadata_events(webhook_json):
    parser = WebhookParser()
    events = parser.parse_webhook(webhook_json)
    return [e for e in events if 'Metadata' in e.event_key]

# Filter by resource
def get_file_events(webhook_json):
    events = parser.parse_webhook(webhook_json)
    return [e for e in events if e.resource == 'File']

# Filter by user
def get_user_events(webhook_json, user_email):
    events = parser.parse_webhook(webhook_json)
    return [e for e in events if e.user.email == user_email]
```

### Pattern 2: Data Extraction

```python
# Extract specific fields from all events
def extract_event_summary(webhook_json):
    parser = WebhookParser()
    events = parser.parse_webhook(webhook_json)
    
    return [
        {
            'event_key': e.event_key,
            'timestamp': e.timestamp,
            'user': e.user.email,
            'data': e.data.raw
        }
        for e in events
    ]
```

### Pattern 3: Change Tracking

```python
# Track what changed
def track_changes(webhook_json):
    parser = WebhookParser()
    events = parser.parse_webhook(webhook_json)
    
    changes = []
    for event in events:
        change = {
            'timestamp': event.timestamp,
            'user': event.user.email,
            'type': event.event_key,
            'old_value': getattr(event.data, 'old_text', None),
            'new_value': getattr(event.data, 'new_text', None),
        }
        changes.append(change)
    
    return changes
```

## See Also

- **PARSER_IMPLEMENTATION.md** - Complete implementation guide
- **QUICK_START.md** - Get started in 5 minutes
- **tests/test_webhook_parser_generalized.py** - Full test suite

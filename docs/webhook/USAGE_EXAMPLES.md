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

### Example 11: Handle Multiple Events in One Webhook (Real Payloads)

Process multiple events from a single webhook payload - a common pattern in PIXXIO:

```python
def handle_batch_webhook_events(webhook_payload):
    """Handle multiple events in one webhook (real PIXXIO pattern)."""
    parser = WebhookParser()
    events = parser.parse_webhook(webhook_payload)
    
    print(f"Processing {len(events)} events from single webhook...\n")
    
    # Group events by type
    by_type = {}
    for event in events:
        if event.event_key not in by_type:
            by_type[event.event_key] = []
        by_type[event.event_key].append(event)
    
    # Show summary
    print(f"Event summary:")
    for event_type, events_of_type in by_type.items():
        print(f"  {event_type}: {len(events_of_type)} event(s)")
    
    # Process each event
    for event in events:
        if event.is_metadata_event():
            # Handle all metadata changes
            field_name = getattr(event.data, 'name', 'unknown')
            new_value = getattr(event.data, 'new_text', None)
            old_value = getattr(event.data, 'old_text', None)
            print(f"\n✓ Metadata change: {field_name}")
            print(f"  Old: {old_value}")
            print(f"  New: {new_value}")
            print(f"  By: {event.user_descriptive_name}")
        
        elif event.is_file_property_event():
            # Handle file property changes
            print(f"\n✓ File property change: {event.event_key}")
            
            # Handle different property types
            if 'FileName' in event.event_key:
                old_name = getattr(event.data, 'old_file_name', None)
                new_name = getattr(event.data, 'new_file_name', None)
                print(f"  Renamed: {old_name} → {new_name}")
            
            elif 'CreateDate' in event.event_key:
                old_date = getattr(event.data, 'old_create_date', None)
                new_date = getattr(event.data, 'new_create_date', None)
                print(f"  Create date: {old_date} → {new_date}")
            
            else:
                # Generic property display
                for key, value in event.data._raw_data.items():
                    if key.startswith('new'):
                        print(f"  {key}: {value}")

# Example with real PIXXIO webhook payload (multiple events)
real_webhook_payload = {
    "events": [
        # Event 1: Metadata text field change
        {
            "id": 1858295187,
            "eventKey": "fileModifiedMetadataFieldText",
            "action": "updated",
            "name": "updateFile",
            "createDate": "2025-11-13 12:52:14",
            "modifyDate": "2025-11-13 12:52:14",
            "applicationKey": "app1",
            "applicationName": "pixx.io",
            "userType": "user",
            "userID": 1000000002,
            "userName": "demo_editor",
            "userDescriptiveName": "Demo Editor",
            "resourceType": "file",
            "resourceID": 1376045043,
            "resourceName": "-",
            "resourceOwnerUserType": "",
            "resourceOwnerUserID": 0,
            "resourceOwnerUserName": "",
            "data": {
                "eventKey": "fileModifiedMetadataFieldText",
                "name": "Kurzbeschreibung",
                "newText": "VIel X",
                "oldText": None
            }
        },
        # Event 2: File name change
        {
            "id": 1191684159,
            "eventKey": "fileModifiedFileName",
            "action": "updated",
            "name": "updateFile",
            "createDate": "2025-11-13 12:52:14",
            "modifyDate": "2025-11-13 12:52:14",
            "applicationKey": "app1",
            "applicationName": "pixx.io",
            "userType": "user",
            "userID": 1000000002,
            "userName": "demo_editor",
            "userDescriptiveName": "Demo Editor",
            "resourceType": "file",
            "resourceID": 1376045043,
            "resourceName": "tmprg44afs5.txt",
            "resourceOwnerUserType": "user",
            "resourceOwnerUserID": 1000000001,
            "resourceOwnerUserName": "demo_admin",
            "data": {
                "eventKey": "fileModifiedFileName",
                "newFileName": "tmprg44afs5_testdatei.txt",
                "oldFileName": "tmprg44afs5.txt"
            }
        }
    ]
}

handle_batch_webhook_events(real_webhook_payload)
# Output:
# Processing 2 events from single webhook...
# 
# Event summary:
#   fileModifiedMetadataFieldText: 1 event(s)
#   fileModifiedFileName: 1 event(s)
#
# ✓ Metadata change: Kurzbeschreibung
#   Old: None
#   New: VIel X
#   By: Demo Editor
#
# ✓ File property change: fileModifiedFileName
#   Renamed: tmprg44afs5.txt → tmprg44afs5_testdatei.txt
```

### Example 12: Handle Metadata Truncate & Language Code Events

Process metadata field truncate (clear) and language code modification events:

```python
def handle_metadata_truncate_and_languages(event):
    """Handle metadata field truncate and language code events."""
    import json
    
    if event.event_key == 'fileModifiedMetadataFieldTruncate':
        # Field was completely cleared
        field_name = event.data.name
        old_data_json = event.data.old_data  # JSON string format
        previous_values = json.loads(old_data_json)
        
        print(f"🗑️  Field cleared: {field_name}")
        print(f"   Previous data: {previous_values}")
        print(f"   By: {event.user.email}")
    
    elif event.event_key == 'fileModifiedLanguageCodesAdded':
        # Language codes were added to file
        codes = event.data.language_codes_added
        print(f"🌐 Languages added: {', '.join(codes)}")
        print(f"   By: {event.user.email}")
    
    elif event.event_key == 'fileModifiedLanguageCodesRemoved':
        # Language codes were removed from file
        codes = event.data.language_codes_removed
        print(f"❌ Languages removed: {', '.join(codes)}")
        print(f"   By: {event.user.email}")

# Example with real payloads showing all three event types
def process_batch_with_truncate_and_languages():
    """Process webhooks with truncate and language code events."""
    parser = WebhookParser()
    
    # Payload 432: Two truncate events
    truncate_payload = {
        "events": [
            {
                "id": 2106034205,
                "eventKey": "fileModifiedMetadataFieldTruncate",
                "action": "updated",
                "name": "updateFile",
                "createDate": "2025-11-13 13:24:52",
                "modifyDate": "2025-11-13 13:24:52",
                "userDescriptiveName": "Demo Editor",
                "resourceID": 1376045043,
                "data": {
                    "eventKey": "fileModifiedMetadataFieldTruncate",
                    "name": "Produktbereich",
                    "oldData": "[\"Kabel\"]"
                }
            },
            {
                "id": 1435646945,
                "eventKey": "fileModifiedMetadataFieldTruncate",
                "action": "updated",
                "name": "updateFile",
                "createDate": "2025-11-13 13:24:52",
                "modifyDate": "2025-11-13 13:24:52",
                "userDescriptiveName": "Demo Editor",
                "resourceID": 1376045043,
                "data": {
                    "eventKey": "fileModifiedMetadataFieldTruncate",
                    "name": "Kanal",
                    "oldData": "[\"STEP\"]"
                }
            }
        ]
    }
    
    # Payload 437: Language codes added
    lang_added_payload = {
        "events": [
            {
                "id": 759112203,
                "eventKey": "fileModifiedLanguageCodesAdded",
                "action": "updated",
                "name": "updateFile",
                "createDate": "2025-11-13 13:24:52",
                "modifyDate": "2025-11-13 13:24:52",
                "userDescriptiveName": "Demo Editor",
                "resourceID": 1376045043,
                "data": {
                    "eventKey": "fileModifiedLanguageCodesAdded",
                    "languageCodesAdded": ["ar-dz", "sq"]
                }
            }
        ]
    }
    
    # Payload 435: Language codes removed
    lang_removed_payload = {
        "events": [
            {
                "id": 1592957052,
                "eventKey": "fileModifiedLanguageCodesRemoved",
                "action": "updated",
                "name": "updateFile",
                "createDate": "2025-11-13 13:24:52",
                "modifyDate": "2025-11-13 13:24:52",
                "userDescriptiveName": "Demo Editor",
                "resourceID": 1376045043,
                "data": {
                    "eventKey": "fileModifiedLanguageCodesRemoved",
                    "languageCodesRemoved": ["af"]
                }
            }
        ]
    }
    
    print("Processing Truncate Events:")
    print("=" * 50)
    for event in parser.parse_webhook(truncate_payload):
        handle_metadata_truncate_and_languages(event)
    
    print("\nProcessing Language Added Event:")
    print("=" * 50)
    for event in parser.parse_webhook(lang_added_payload):
        handle_metadata_truncate_and_languages(event)
    
    print("\nProcessing Language Removed Event:")
    print("=" * 50)
    for event in parser.parse_webhook(lang_removed_payload):
        handle_metadata_truncate_and_languages(event)

# Output:
# Processing Truncate Events:
# ==================================================
# 🗑️  Field cleared: Produktbereich
#    Previous data: ['Kabel']
#    By: Demo Editor
# 🗑️  Field cleared: Kanal
#    Previous data: ['STEP']
#    By: Demo Editor
#
# Processing Language Added Event:
# ==================================================
# 🌐 Languages added: ar-dz, sq
#    By: Demo Editor
#
# Processing Language Removed Event:
# ==================================================
# ❌ Languages removed: af
#    By: Demo Editor
```

### Example 13: Handle Keyword Events (Added/Deleted)

Process file keyword modification events:

```python
def handle_keyword_events(event):
    """Handle keyword added/deleted events."""
    if event.is_keywords_event():
        if event.event_key == 'fileModifiedKeywordsAdded':
            keywords = event.data.keywords_added
            print(f"✨ Keywords added to '{event.resource_name}':")
            print(f"   Keywords: {', '.join(keywords)}")
            print(f"   By: {event.user_descriptive_name}")
            print(f"   At: {event.timestamp}")
        
        elif event.event_key == 'fileModifiedKeywordsDeleted':
            keywords = event.data.keywords_deleted
            print(f"🗑️  Keywords removed from '{event.resource_name}':")
            print(f"   Keywords: {', '.join(keywords)}")
            print(f"   By: {event.user_descriptive_name}")
            print(f"   At: {event.timestamp}")

def process_keyword_events():
    """Process webhooks containing keyword modification events."""
    parser = WebhookParser()
    
    # Payload 551: Keywords added
    keywords_added_payload = {
        "events": [
            {
                "id": 1678336404,
                "eventKey": "fileModifiedKeywordsAdded",
                "action": "updated",
                "name": "updateFile",
                "createDate": "2025-11-13 13:40:51",
                "modifyDate": "2025-11-13 13:40:51",
                "userDescriptiveName": "Demo Editor",
                "resourceID": 1376045043,
                "resourceName": "tmprg44afs5_testdatei.txt",
                "data": {
                    "eventKey": "fileModifiedKeywordsAdded",
                    "keywordsAdded": ["demo"]
                }
            }
        ]
    }
    
    # Payload 719: Keywords deleted
    keywords_deleted_payload = {
        "events": [
            {
                "id": 459041673,
                "eventKey": "fileModifiedKeywordsDeleted",
                "action": "updated",
                "name": "updateFile",
                "createDate": "2025-11-13 13:42:13",
                "modifyDate": "2025-11-13 13:42:13",
                "userDescriptiveName": "Demo Editor",
                "resourceID": 1376045043,
                "resourceName": "tmprg44afs5_testdatei.txt",
                "data": {
                    "eventKey": "fileModifiedKeywordsDeleted",
                    "keywordsDeleted": ["example"]
                }
            }
        ]
    }
    
    print("Processing Keyword Added Event:")
    print("=" * 50)
    for event in parser.parse_webhook(keywords_added_payload):
        handle_keyword_events(event)
    
    print("\nProcessing Keyword Deleted Event:")
    print("=" * 50)
    for event in parser.parse_webhook(keywords_deleted_payload):
        handle_keyword_events(event)

# Output:
# Processing Keyword Added Event:
# ==================================================
# ✨ Keywords added to 'tmprg44afs5_testdatei.txt':
#    Keywords: demo
#    By: Demo Editor
#    At: 2025-11-13 13:40:51
#
# Processing Keyword Deleted Event:
# ==================================================
# 🗑️  Keywords removed from 'tmprg44afs5_testdatei.txt':
#    Keywords: example
#    By: Demo Editor
#    At: 2025-11-13 13:42:13
```

## See Also

- **PARSER_IMPLEMENTATION.md** - Complete implementation guide
- **QUICK_START.md** - Get started in 5 minutes
- **tests/test_webhook_parser_generalized.py** - Full test suite

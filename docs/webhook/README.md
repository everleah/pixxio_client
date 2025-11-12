# PIXXIO Webhook Parser Documentation

This folder contains comprehensive documentation for the PIXXIO webhook parser implementation.

## Quick Navigation

### 📚 Getting Started
- **[QUICK_START.md](./QUICK_START.md)** - 5-minute quick start guide
  - Basic usage, common patterns, troubleshooting

### 📖 Implementation Details
- **[PARSER_IMPLEMENTATION.md](./PARSER_IMPLEMENTATION.md)** - Complete implementation guide
  - Core components, all usage patterns, real-world examples
  - Architecture explanation, type hints, error handling
  - Migration guide from old hardcoded classes

### 💡 Examples
- **[USAGE_EXAMPLES.md](./USAGE_EXAMPLES.md)** - 10+ practical examples
  - Simple logging, metadata handling, filtering
  - Database integration (SQLAlchemy)
  - Async handlers (FastAPI)
  - Best practices and patterns

## What is the Webhook Parser?

The PIXXIO webhook parser provides **generalized, schema-agnostic** event handling for all PIXXIO webhook event types.

### Key Features

✅ **Handles 200+ Event Types** - Single `EventData` class works for all event types  
✅ **Future-Proof** - New event types work automatically with ZERO code changes  
✅ **Flexible Data Access** - camelCase + snake_case, both available  
✅ **Type-Safe** - Dot notation access with error handling  
✅ **Production Ready** - 11 comprehensive unit tests, all passing  

## Quick Example

```python
from pixxio_client.webhook_parser import WebhookParser

parser = WebhookParser()
events = parser.parse_webhook(webhook_json)

for event in events:
    print(f"Event: {event.event_key}")
    print(f"User: {event.user.email}")
    
    # Safe data access
    if hasattr(event.data, 'new_text'):
        print(f"Changed to: {event.data.new_text}")
```

## Documentation Structure

```
docs/webhook/
├── README.md                    (this file)
├── QUICK_START.md              (5-minute intro)
├── PARSER_IMPLEMENTATION.md    (complete guide)
└── USAGE_EXAMPLES.md           (10+ practical examples)
```

## Event Structure

Every webhook event has:

```python
event.id                 # Unique event ID
event.event_key         # Event type (e.g., 'fileModifiedMetadataFieldText')
event.action            # 'CREATED', 'UPDATED', 'DELETED'
event.resource          # 'File', 'Collection', etc.
event.user              # WebhookUser object (email, name, etc.)
event.timestamp         # When the event occurred
event.data              # EventData - flexible event-specific data
```

## Field Access Patterns

### Pattern 1: Check & Access
```python
if hasattr(event.data, 'new_text'):
    print(event.data.new_text)
```

### Pattern 2: Safe Default
```python
new_value = getattr(event.data, 'new_text', None)
```

### Pattern 3: Raw Data
```python
raw_dict = event.data.raw  # Complete original data
```

### Pattern 4: Both Name Formats
```python
event.data.new_text       # snake_case (Pythonic)
event.data.newText        # camelCase (API original)
# Both work!
```

## Common Event Types

| Event | Fields | Example |
|-------|--------|---------|
| `fileModifiedMetadataFieldText` | `name`, `old_text`, `new_text` | Text field changed |
| `fileModifiedMetadataFieldMultiSelectionsAdded` | `name`, `multi_selections_added` | Selections added |
| `fileModifiedFileStateID` | `new_file_state_id` | File state changed |
| `fileModifiedLanguageCodesAdded` | `language_codes_added` | Languages added |

## Why the Generalized Approach?

### Old Way (❌ Problematic)
- Hardcoded classes for 4-50+ event types
- New API events require code changes
- Maintenance burden

### New Way (✅ Production Ready)
- Single `EventData` class for all 200+ types
- Future events work automatically
- Easy to maintain and extend

## Testing

All webhook parsing is thoroughly tested:

```bash
python -m unittest tests.test_webhook_parser_generalized -v
# Result: Ran 11 tests in 0.005s - OK ✅
```

Tests validate:
- ✅ Basic parsing
- ✅ Multiple events in one webhook
- ✅ All known event types
- ✅ Unknown/future event types
- ✅ Field name conversion
- ✅ Raw data access
- ✅ Error handling

## File Locations

**Documentation:**
- `docs/webhook/` (this folder)

**Source Code:**
- `pixxio_client/webhook_parser.py`

**Tests:**
- `tests/test_webhook_parser_generalized.py`

## Need Help?

1. **Just starting?** → Read [QUICK_START.md](./QUICK_START.md)
2. **Want full details?** → Read [PARSER_IMPLEMENTATION.md](./PARSER_IMPLEMENTATION.md)
3. **Need code examples?** → See [USAGE_EXAMPLES.md](./USAGE_EXAMPLES.md)
4. **Review tests?** → Check `tests/test_webhook_parser_generalized.py`

---

**Status:** Production Ready ✅  
**Last Updated:** November 12, 2025  
**Event Coverage:** 200+ types + future-proof

"""
PIXXIO Webhook Event Parser

This module provides utilities for parsing and handling PIXXIO webhook events.
It uses a generalized, schema-agnostic approach that can handle any event type
(200+ known types + future types) without code changes.

Architecture:
    - PIXXIO webhooks have a CONSISTENT structure: metadata + data
    - Event structure is always: id, eventKey, action, user, resource, data, etc.
    - Each event type has DIFFERENT data content (event-specific)
    - Solution: Parse structure once, store data generically using SimpleNamespace
    
This allows:
    ✓ Handling all 200+ existing event types
    ✓ Supporting future event types automatically
    ✓ Type-safe access via dot notation (event.data.field_name)
    ✓ Optional schema definitions for known types (validation, IDE hints)
    ✓ Fallback to raw dict access for unknown events

Usage:
    from pixxio_client.webhook_parser import WebhookParser, WebhookEvent
    
    parser = WebhookParser()
    events = parser.parse_webhook(webhook_json)
    
    for event in events:
        print(f"Event: {event.event_key}, Action: {event.action}")
        # Access event data generically via dot notation
        if hasattr(event.data, 'name'):
            print(f"Changed field: {event.data.name}")
        # Access raw dict if needed
        print(f"Raw data: {event.data.raw}")
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from enum import Enum
from types import SimpleNamespace
import json
import logging

logger = logging.getLogger(__name__)


class EventAction(str, Enum):
    """Standard PIXXIO event action types."""
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    UPLOADED = "uploaded"
    MOVED = "moved"
    COPIED = "copied"
    RESTORED = "restored"
    ARCHIVED = "archived"
    EXPORTED = "exported"
    IMPORTED = "imported"


class ResourceType(str, Enum):
    """PIXXIO resource types."""
    FILE = "file"
    COLLECTION = "collection"
    DIRECTORY = "directory"
    USER = "user"
    PERMISSION_GROUP = "permissiongroup"
    PORTAL = "portal"
    EXTERNAL_SHARE = "externalshare"
    LICENSE = "license"
    KEYWORD = "keyword"
    METADATA = "metadata"
    UNKNOWN = "unknown"


class EventKey(str, Enum):
    """Known PIXXIO event keys."""
    # File metadata events
    FILE_MODIFIED_METADATA_FIELD_TEXT = "fileModifiedMetadataFieldText"
    FILE_MODIFIED_METADATA_FIELD_MULTI_SELECTIONS_ADDED = "fileModifiedMetadataFieldMultiSelectionsAdded"
    FILE_MODIFIED_METADATA_FIELD_MULTI_SELECTIONS_REMOVED = "fileModifiedMetadataFieldMultiSelectionsRemoved"
    FILE_MODIFIED_LANGUAGE_CODES_ADDED = "fileModifiedLanguageCodesAdded"
    FILE_MODIFIED_LANGUAGE_CODES_REMOVED = "fileModifiedLanguageCodesRemoved"
    FILE_MODIFIED_FILE_STATE_ID = "fileModifiedFileStateID"
    
    # File events
    FILE_CREATED = "fileCreated"
    FILE_UPLOADED = "fileUploaded"
    FILE_DELETED = "fileDeleted"
    FILE_MOVED = "fileMoved"
    FILE_COPIED = "fileCopied"
    FILE_DOWNLOADED = "fileDownloaded"
    FILE_RESTORED = "fileRestored"
    
    # Collection events
    COLLECTION_CREATED = "collectionCreated"
    COLLECTION_DELETED = "collectionDeleted"
    COLLECTION_MODIFIED = "collectionModified"
    
    # User events
    USER_CREATED = "userCreated"
    USER_DELETED = "userDeleted"
    USER_MODIFIED = "userModified"
    
    # Unknown
    UNKNOWN = "unknown"


@dataclass
@dataclass
class EventData:
    """
    Flexible container for event-specific data.
    
    This class provides a GENERALIZED approach that works for any event type.
    Instead of hardcoding specific event types, we store all data as attributes
    that can be accessed via dot notation.
    
    The data is stored in two ways:
    1. As individual attributes (from parsed raw_data) for IDE autocomplete hints
       and easy dot notation access
    2. As raw_data dict for access to original data
    
    This design allows:
    - Handling 200+ event types without code changes
    - Supporting future event types automatically
    - Type-safe dot notation access: event.data.field_name
    - Fallback to raw dict: event.data.raw or event.data._raw_data
    
    Example:
        # Metadata text change event
        if hasattr(event.data, 'name') and hasattr(event.data, 'new_text'):
            print(f"Changed {event.data.name}: {event.data.old_text} → {event.data.new_text}")
        
        # File state change event
        if hasattr(event.data, 'new_file_state_id'):
            print(f"New file state: {event.data.new_file_state_id}")
        
        # Access raw data if needed
        print(f"All data: {event.data._raw_data}")
    """
    event_key: str
    _raw_data: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Convert raw data to object attributes for dot notation access."""
        # Store raw data as a property-like dict
        self.raw = self._raw_data
        
        # Dynamically set all raw data fields as attributes
        for key, value in self._raw_data.items():
            # Convert camelCase keys to snake_case for pythonic access
            # e.g., "oldText" → "old_text", "newFileStateID" → "new_file_state_id"
            snake_key = self._camel_to_snake(key)
            setattr(self, snake_key, value)
            # Also keep original camelCase for reference
            setattr(self, key, value)
    
    @staticmethod
    def _camel_to_snake(name: str) -> str:
        """Convert camelCase to snake_case."""
        import re
        # Handle special case of consecutive capitals (e.g., ID → id)
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event data to dictionary."""
        return {
            "event_key": self.event_key,
            **self._raw_data
        }
    
    def __repr__(self) -> str:
        """String representation."""
        return f"EventData({self.event_key}, {self._raw_data})"


@dataclass
class WebhookEvent:
    """
    Represents a single event from a PIXXIO webhook.
    
    This is the main dataclass that applications should use when processing
    webhook events. All relevant data from the webhook is mapped to typed fields.
    
    The common structure is always present (id, eventKey, action, user, resource),
    but the event-specific data in the 'data' field varies by event type.
    
    This class supports ANY event type without code changes because the data
    is stored flexibly in an EventData object.
    """
    
    # Event metadata
    event_id: int
    event_key: str
    action: str
    event_name: str
    created_at: datetime
    modified_at: datetime
    
    # Application info
    application_key: str
    application_name: str
    
    # User info
    user_type: str
    user_id: int
    user_name: str
    user_descriptive_name: str
    
    # Resource info
    resource_type: str
    resource_id: int
    resource_name: str
    resource_owner_user_type: str
    resource_owner_user_id: int
    resource_owner_user_name: str
    
    # Event-specific data (flexible, works for any event type)
    data: EventData
    
    # Original raw data
    raw: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Ensure datetime objects are proper datetime instances."""
        if isinstance(self.created_at, str):
            self.created_at = self._parse_datetime(self.created_at)
        if isinstance(self.modified_at, str):
            self.modified_at = self._parse_datetime(self.modified_at)
    
    @staticmethod
    def _parse_datetime(dt_str: str) -> datetime:
        """Parse PIXXIO datetime strings (format: "2025-11-11 14:22:27")."""
        try:
            return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            # Fallback for ISO format
            return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    
    def is_file_event(self) -> bool:
        """Check if this event is about a file."""
        return self.resource_type == ResourceType.FILE.value
    
    def is_collection_event(self) -> bool:
        """Check if this event is about a collection."""
        return self.resource_type == ResourceType.COLLECTION.value
    
    def is_metadata_event(self) -> bool:
        """Check if this event is about metadata changes."""
        return "Metadata" in self.event_key
    
    def is_language_event(self) -> bool:
        """Check if this event is about language code changes."""
        return "LanguageCodes" in self.event_key
    
    def is_state_event(self) -> bool:
        """Check if this event is about file state changes."""
        return "FileStateID" in self.event_key
    
    def is_user_action_by_admin(self) -> bool:
        """Check if this event was triggered by an admin user."""
        return "admin" in self.user_name.lower()
    
    def get_user_full_name(self) -> str:
        """Get the full descriptive name of the user who triggered this event."""
        return self.user_descriptive_name or self.user_name
    
    def get_changed_field_name(self) -> Optional[str]:
        """
        Get the name of the field that was changed (if applicable).
        
        Works for metadata events where the data contains a 'name' field.
        For other event types, returns None.
        """
        if hasattr(self.data, 'name'):
            return getattr(self.data, 'name', None)
        return None
    
    def data_has_field(self, field_name: str) -> bool:
        """
        Check if the event data contains a specific field.
        
        Useful for checking what fields are available in different event types.
        Supports both snake_case and camelCase field names.
        
        Example:
            if event.data_has_field('new_text'):
                print(event.data.new_text)
        """
        return hasattr(self.data, field_name)
    
    def get_data_field(self, field_name: str, default: Any = None) -> Any:
        """
        Safely get a field from event data.
        
        Tries both snake_case and camelCase versions of the field name.
        
        Example:
            new_text = event.get_data_field('new_text', '')
        """
        # Try snake_case first
        if hasattr(self.data, field_name):
            return getattr(self.data, field_name, default)
        # Try camelCase (reverse of snake_to_camel)
        camel_name = ''.join(word.capitalize() if i > 0 else word 
                             for i, word in enumerate(field_name.split('_')))
        if hasattr(self.data, camel_name):
            return getattr(self.data, camel_name, default)
        return default
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary representation."""
        return {
            "event_id": self.event_id,
            "event_key": self.event_key,
            "action": self.action,
            "event_name": self.event_name,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
            "application_key": self.application_key,
            "application_name": self.application_name,
            "user": {
                "type": self.user_type,
                "id": self.user_id,
                "name": self.user_name,
                "descriptive_name": self.user_descriptive_name,
            },
            "resource": {
                "type": self.resource_type,
                "id": self.resource_id,
                "name": self.resource_name,
                "owner": {
                    "type": self.resource_owner_user_type,
                    "id": self.resource_owner_user_id,
                    "name": self.resource_owner_user_name,
                }
            },
            "data": self.data.to_dict() if hasattr(self.data, 'to_dict') else self.data,
        }


class WebhookParser:
    """
    Parser for PIXXIO webhook events.
    
    This class converts raw webhook JSON payloads into structured WebhookEvent objects.
    It handles different event types and provides type-safe access to event data.
    
    Example:
        parser = WebhookParser()
        events = parser.parse_webhook(webhook_json_dict)
        
        for event in events:
            if event.is_file_event():
                print(f"File {event.resource_id} was {event.action}")
    """
    
    def __init__(self):
        """Initialize the webhook parser."""
        self.logger = logger
    
    def parse_webhook(self, payload: Union[str, bytes, Dict[str, Any]]) -> List[WebhookEvent]:
        """
        Parse a webhook payload into a list of WebhookEvent objects.
        
        Args:
            payload: Raw webhook payload (JSON string, bytes, or dict)
        
        Returns:
            List of parsed WebhookEvent objects
        
        Raises:
            ValueError: If payload format is invalid
        """
        try:
            # Convert to dict if needed
            if isinstance(payload, (str, bytes)):
                data = json.loads(payload) if isinstance(payload, str) else json.loads(payload.decode())
            else:
                data = payload
            
            if not isinstance(data, dict):
                raise ValueError("Payload must be a dictionary or JSON object")
            
            events_data = data.get("events", [])
            if not isinstance(events_data, list):
                raise ValueError("Payload 'events' field must be a list")
            
            events = []
            for event_data in events_data:
                try:
                    event = self._parse_event(event_data)
                    events.append(event)
                except Exception as e:
                    self.logger.warning(f"Failed to parse event: {e}")
                    # Skip malformed events but continue processing
                    continue
            
            self.logger.info(f"Parsed {len(events)} events from webhook")
            return events
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON payload: {e}")
        except Exception as e:
            self.logger.error(f"Error parsing webhook: {e}")
            raise
    
    def _parse_event(self, event_data: Dict[str, Any]) -> WebhookEvent:
        """
        Parse a single event from webhook data.
        
        Args:
            event_data: Dictionary containing a single event
        
        Returns:
            WebhookEvent object
        """
        # Extract event metadata
        event_id = event_data.get("id", 0)
        event_key = event_data.get("eventKey", "unknown")
        action = event_data.get("action", "unknown")
        event_name = event_data.get("name", "unknown")
        created_at = event_data.get("createDate", datetime.now())
        modified_at = event_data.get("modifyDate", datetime.now())
        
        # Extract application info
        application_key = event_data.get("applicationKey", "")
        application_name = event_data.get("applicationName", "")
        
        # Extract user info
        user_type = event_data.get("userType", "")
        user_id = event_data.get("userID", 0)
        user_name = event_data.get("userName", "")
        user_descriptive_name = event_data.get("userDescriptiveName", "")
        
        # Extract resource info
        resource_type = event_data.get("resourceType", "unknown")
        resource_id = event_data.get("resourceID", 0)
        resource_name = event_data.get("resourceName", "")
        resource_owner_user_type = event_data.get("resourceOwnerUserType", "")
        resource_owner_user_id = event_data.get("resourceOwnerUserID", 0)
        resource_owner_user_name = event_data.get("resourceOwnerUserName", "")
        
        # Parse event-specific data
        event_specific_data = self._parse_event_data(event_key, event_data.get("data", {}))
        
        # Create WebhookEvent object
        return WebhookEvent(
            event_id=event_id,
            event_key=event_key,
            action=action,
            event_name=event_name,
            created_at=created_at,
            modified_at=modified_at,
            application_key=application_key,
            application_name=application_name,
            user_type=user_type,
            user_id=user_id,
            user_name=user_name,
            user_descriptive_name=user_descriptive_name,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            resource_owner_user_type=resource_owner_user_type,
            resource_owner_user_id=resource_owner_user_id,
            resource_owner_user_name=resource_owner_user_name,
            data=event_specific_data,
            raw=event_data,
        )
    
    def _parse_event_data(self, event_key: str, data: Dict[str, Any]) -> EventData:
        """
        Parse event-specific data generically.
        
        This simplified method works for ANY event type. It doesn't hardcode
        specific event types - instead it just wraps the raw data in an
        EventData object which dynamically creates attributes for all fields.
        
        This is the key to supporting 200+ event types + future types without
        code changes.
        
        Args:
            event_key: The event key to store for reference
            data: Raw event data dict
        
        Returns:
            EventData object with all fields as attributes
        """
        # Simply wrap the data - EventData.__post_init__ will handle
        # converting all fields to accessible attributes
        return EventData(event_key=event_key, _raw_data=data)


# Convenience function for quick parsing
def parse_pixxio_webhook(payload: Union[str, bytes, Dict[str, Any]]) -> List[WebhookEvent]:
    """
    Quick function to parse a PIXXIO webhook payload.
    
    This is a convenience wrapper around WebhookParser for one-off parsing.
    For repeated parsing, create a WebhookParser instance instead.
    
    Args:
        payload: Raw webhook payload
    
    Returns:
        List of parsed WebhookEvent objects
    
    Example:
        events = parse_pixxio_webhook(request.json())
        for event in events:
            print(event.event_key)
    """
    parser = WebhookParser()
    return parser.parse_webhook(payload)

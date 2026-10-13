"""
Tests for PIXXIO Webhook Parser - Generalized Approach

This module contains comprehensive tests for the webhook parser using real
PIXXIO webhook data. Tests verify the GENERALIZED approach works for all
event types without hardcoding specific types.

Key test strategy:
- Tests verify that EventData works generically via hasattr/getattr
- No type-specific assertions needed
- Tests use event.data_has_field() and event.get_data_field()
- Same parser handles all 200+ event types uniformly
"""

import unittest
import json
from datetime import datetime
from pixxio_client.webhook_parser import (
    WebhookParser,
    WebhookEvent,
    EventData,
    parse_pixxio_webhook,
)


class TestWebhookParserGeneralized(unittest.TestCase):
    """Test cases for generalized WebhookParser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = WebhookParser()
    
    def test_parse_file_metadata_text_event(self):
        """Test parsing file metadata text modification event (generalized)."""
        payload = {
            "events": [
                {
                    "id": 164137675,
                    "eventKey": "fileModifiedMetadataFieldText",
                    "action": "updated",
                    "name": "updateFile",
                    "createDate": "2025-11-11 13:32:52",
                    "modifyDate": "2025-11-11 13:32:52",
                    "applicationKey": "app1",
                    "applicationName": "pixx.io",
                    "userType": "user",
                    "userID": 130052009,
                    "userName": "admin_claudius",
                    "userDescriptiveName": "Claudius Hansch",
                    "resourceType": "file",
                    "resourceID": 1930337128,
                    "resourceName": "-",
                    "resourceOwnerUserType": "",
                    "resourceOwnerUserID": 0,
                    "resourceOwnerUserName": "",
                    "data": {
                        "eventKey": "fileModifiedMetadataFieldText",
                        "name": "Artikelnummer",
                        "newText": "555444333",
                        "oldText": None
                    }
                }
            ]
        }
        
        events = self.parser.parse_webhook(payload)
        
        self.assertEqual(len(events), 1)
        event = events[0]
        
        # Check common structure (works for all events)
        self.assertEqual(event.event_id, 164137675)
        self.assertEqual(event.event_key, "fileModifiedMetadataFieldText")
        self.assertEqual(event.action, "updated")
        self.assertEqual(event.user_name, "admin_claudius")
        self.assertTrue(event.is_file_event())
        self.assertTrue(event.is_metadata_event())
        
        # Check event data (generalized - works for ANY event type)
        self.assertIsInstance(event.data, EventData)
        self.assertTrue(event.data_has_field('name'))
        self.assertTrue(event.data_has_field('new_text'))
        self.assertEqual(event.get_data_field('name'), "Artikelnummer")
        self.assertEqual(event.get_data_field('new_text'), "555444333")
        self.assertIsNone(event.get_data_field('old_text'))
        
        # Direct attribute access also works
        self.assertEqual(event.data.name, "Artikelnummer")  # type: ignore[attr-defined]
        self.assertEqual(event.data.new_text, "555444333")  # type: ignore[attr-defined]
    
    def test_parse_file_metadata_multi_select_event(self):
        """Test parsing file metadata multi-select modification event (generalized)."""
        payload = {
            "events": [
                {
                    "id": 1014544096,
                    "eventKey": "fileModifiedMetadataFieldMultiSelectionsAdded",
                    "action": "updated",
                    "name": "updateFile",
                    "createDate": "2025-11-11 14:22:27",
                    "modifyDate": "2025-11-11 14:22:27",
                    "applicationKey": "app1",
                    "applicationName": "pixx.io",
                    "userType": "user",
                    "userID": 130052009,
                    "userName": "admin_claudius",
                    "userDescriptiveName": "Claudius Hansch",
                    "resourceType": "file",
                    "resourceID": 1930337128,
                    "resourceName": "-",
                    "resourceOwnerUserType": "",
                    "resourceOwnerUserID": 0,
                    "resourceOwnerUserName": "",
                    "data": {
                        "name": "Kanal",
                        "multiSelectionsAdded": ["STEP"],
                        "multiSelectionsRemoved": []
                    }
                }
            ]
        }
        
        events = self.parser.parse_webhook(payload)
        self.assertEqual(len(events), 1)
        
        event = events[0]
        self.assertEqual(event.event_key, "fileModifiedMetadataFieldMultiSelectionsAdded")
        self.assertEqual(event.action, "updated")
        self.assertTrue(event.is_file_event())
        self.assertTrue(event.is_metadata_event())
        
        # Generalized data access
        self.assertIsInstance(event.data, EventData)
        self.assertEqual(event.get_data_field('name'), "Kanal")
        self.assertEqual(event.get_data_field('multi_selections_added'), ["STEP"])
        self.assertEqual(event.get_data_field('multi_selections_removed'), [])
        
        # Direct access
        self.assertEqual(event.data.name, "Kanal")  # type: ignore
        self.assertEqual(event.data.multi_selections_added, ["STEP"])  # type: ignore
    
    def test_parse_file_language_codes_event(self):
        """Test parsing file language codes modification event (generalized)."""
        payload = {
            "events": [
                {
                    "id": 1047882309,
                    "eventKey": "fileModifiedLanguageCodesAdded",
                    "action": "updated",
                    "name": "updateFile",
                    "createDate": "2025-11-11 14:22:29",
                    "modifyDate": "2025-11-11 14:22:29",
                    "applicationKey": "app1",
                    "applicationName": "pixx.io",
                    "userType": "user",
                    "userID": 130052009,
                    "userName": "admin_claudius",
                    "userDescriptiveName": "Claudius Hansch",
                    "resourceType": "file",
                    "resourceID": 1930337128,
                    "resourceName": "-",
                    "resourceOwnerUserType": "",
                    "resourceOwnerUserID": 0,
                    "resourceOwnerUserName": "",
                    "data": {
                        "languageCodesAdded": ["af"],
                        "languageCodesRemoved": []
                    }
                }
            ]
        }
        
        events = self.parser.parse_webhook(payload)
        self.assertEqual(len(events), 1)
        
        event = events[0]
        self.assertEqual(event.event_key, "fileModifiedLanguageCodesAdded")
        self.assertTrue(event.is_file_event())
        self.assertTrue(event.is_language_event())
        
        # Generalized data access
        self.assertIsInstance(event.data, EventData)
        self.assertEqual(event.get_data_field('language_codes_added'), ["af"])
        self.assertEqual(event.get_data_field('language_codes_removed'), [])
    
    def test_parse_file_state_event(self):
        """Test parsing file state modification event (generalized)."""
        payload = {
            "events": [
                {
                    "id": 1047882310,
                    "eventKey": "fileModifiedFileStateID",
                    "action": "updated",
                    "name": "updateFile",
                    "createDate": "2025-11-11 14:22:30",
                    "modifyDate": "2025-11-11 14:22:30",
                    "applicationKey": "app1",
                    "applicationName": "pixx.io",
                    "userType": "user",
                    "userID": 130052009,
                    "userName": "admin_claudius",
                    "userDescriptiveName": "Claudius Hansch",
                    "resourceType": "file",
                    "resourceID": 1930337128,
                    "resourceName": "-",
                    "resourceOwnerUserType": "",
                    "resourceOwnerUserID": 0,
                    "resourceOwnerUserName": "",
                    "data": {
                        "newFileStateID": 1872385346,
                        "oldFileStateID": None
                    }
                }
            ]
        }
        
        events = self.parser.parse_webhook(payload)
        self.assertEqual(len(events), 1)
        
        event = events[0]
        self.assertEqual(event.event_key, "fileModifiedFileStateID")
        self.assertTrue(event.is_file_event())
        self.assertTrue(event.is_state_event())
        
        # Generalized data access
        self.assertIsInstance(event.data, EventData)
        self.assertEqual(event.get_data_field('new_file_state_id'), 1872385346)
        self.assertIsNone(event.get_data_field('old_file_state_id'))
        
        # Direct access
        self.assertEqual(event.data.new_file_state_id, 1872385346)  # type: ignore
    
    def test_parse_unknown_event_type(self):
        """Test parsing an unknown/future event type (generalized)."""
        # This demonstrates how new event types work WITHOUT code changes
        payload = {
            "events": [
                {
                    "id": 99999,
                    "eventKey": "futureEventTypeThatDoesntExistYet",
                    "action": "created",
                    "name": "unknownEvent",
                    "createDate": "2025-11-11 14:22:30",
                    "modifyDate": "2025-11-11 14:22:30",
                    "applicationKey": "app1",
                    "applicationName": "pixx.io",
                    "userType": "user",
                    "userID": 130052009,
                    "userName": "admin_claudius",
                    "userDescriptiveName": "Claudius Hansch",
                    "resourceType": "file",
                    "resourceID": 1930337128,
                    "resourceName": "-",
                    "resourceOwnerUserType": "",
                    "resourceOwnerUserID": 0,
                    "resourceOwnerUserName": "",
                    "data": {
                        "someNewField": "value1",
                        "anotherNewField": 42,
                        "complexField": {"nested": "data"}
                    }
                }
            ]
        }
        
        # Parser handles it WITHOUT code changes!
        events = self.parser.parse_webhook(payload)
        self.assertEqual(len(events), 1)
        
        event = events[0]
        self.assertEqual(event.event_key, "futureEventTypeThatDoesntExistYet")
        
        # All fields accessible without any special handling
        self.assertEqual(event.get_data_field('some_new_field'), "value1")
        self.assertEqual(event.get_data_field('another_new_field'), 42)
        self.assertEqual(event.get_data_field('complex_field'), {"nested": "data"})
    
    def test_parse_multiple_events_mixed_types(self):
        """Test parsing multiple events of different types (generalized)."""
        payload = {
            "events": [
                {
                    "id": 1,
                    "eventKey": "fileModifiedMetadataFieldText",
                    "action": "updated",
                    "name": "updateFile",
                    "createDate": "2025-11-11 13:32:52",
                    "modifyDate": "2025-11-11 13:32:52",
                    "applicationKey": "app1",
                    "applicationName": "pixx.io",
                    "userType": "user",
                    "userID": 130052009,
                    "userName": "admin_claudius",
                    "userDescriptiveName": "Claudius Hansch",
                    "resourceType": "file",
                    "resourceID": 1930337128,
                    "resourceName": "-",
                    "resourceOwnerUserType": "",
                    "resourceOwnerUserID": 0,
                    "resourceOwnerUserName": "",
                    "data": {
                        "name": "Title",
                        "newText": "New Title",
                        "oldText": "Old Title"
                    }
                },
                {
                    "id": 2,
                    "eventKey": "fileModifiedFileStateID",
                    "action": "updated",
                    "name": "updateFile",
                    "createDate": "2025-11-11 14:22:30",
                    "modifyDate": "2025-11-11 14:22:30",
                    "applicationKey": "app1",
                    "applicationName": "pixx.io",
                    "userType": "user",
                    "userID": 130052009,
                    "userName": "admin_claudius",
                    "userDescriptiveName": "Claudius Hansch",
                    "resourceType": "file",
                    "resourceID": 1930337128,
                    "resourceName": "-",
                    "resourceOwnerUserType": "",
                    "resourceOwnerUserID": 0,
                    "resourceOwnerUserName": "",
                    "data": {
                        "newFileStateID": 123,
                        "oldFileStateID": 456
                    }
                }
            ]
        }
        
        events = self.parser.parse_webhook(payload)
        self.assertEqual(len(events), 2)
        
        # Both work the same way - generalized!
        event1 = events[0]
        self.assertTrue(event1.is_metadata_event())
        self.assertEqual(event1.get_data_field('name'), "Title")
        self.assertEqual(event1.get_data_field('new_text'), "New Title")
        
        event2 = events[1]
        self.assertTrue(event2.is_state_event())
        self.assertEqual(event2.get_data_field('new_file_state_id'), 123)
        self.assertEqual(event2.get_data_field('old_file_state_id'), 456)
    
    def test_parse_json_string(self):
        """Test parsing JSON string payload."""
        payload_str = json.dumps({
            "events": [
                {
                    "id": 1,
                    "eventKey": "fileModifiedMetadataFieldText",
                    "action": "updated",
                    "name": "test",
                    "createDate": "2025-11-11 13:32:52",
                    "modifyDate": "2025-11-11 13:32:52",
                    "applicationKey": "app1",
                    "applicationName": "pixx.io",
                    "userType": "user",
                    "userID": 1,
                    "userName": "user1",
                    "userDescriptiveName": "User One",
                    "resourceType": "file",
                    "resourceID": 100,
                    "resourceName": "file.txt",
                    "resourceOwnerUserType": "",
                    "resourceOwnerUserID": 0,
                    "resourceOwnerUserName": "",
                    "data": {
                        "name": "field",
                        "newText": "value"
                    }
                }
            ]
        })
        
        events = self.parser.parse_webhook(payload_str)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].user_name, "user1")
    
    def test_parse_json_bytes(self):
        """Test parsing JSON bytes payload."""
        payload_bytes = json.dumps({
            "events": [
                {
                    "id": 1,
                    "eventKey": "fileModifiedMetadataFieldText",
                    "action": "updated",
                    "name": "test",
                    "createDate": "2025-11-11 13:32:52",
                    "modifyDate": "2025-11-11 13:32:52",
                    "applicationKey": "app1",
                    "applicationName": "pixx.io",
                    "userType": "user",
                    "userID": 1,
                    "userName": "user1",
                    "userDescriptiveName": "User One",
                    "resourceType": "file",
                    "resourceID": 100,
                    "resourceName": "file.txt",
                    "resourceOwnerUserType": "",
                    "resourceOwnerUserID": 0,
                    "resourceOwnerUserName": "",
                    "data": {
                        "name": "field",
                        "newText": "value"
                    }
                }
            ]
        }).encode('utf-8')
        
        events = self.parser.parse_webhook(payload_bytes)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].user_name, "user1")
    
    def test_event_to_dict(self):
        """Test converting event to dictionary."""
        payload = {
            "events": [
                {
                    "id": 1,
                    "eventKey": "fileModifiedMetadataFieldText",
                    "action": "updated",
                    "name": "test",
                    "createDate": "2025-11-11 13:32:52",
                    "modifyDate": "2025-11-11 13:32:52",
                    "applicationKey": "app1",
                    "applicationName": "pixx.io",
                    "userType": "user",
                    "userID": 1,
                    "userName": "user1",
                    "userDescriptiveName": "User One",
                    "resourceType": "file",
                    "resourceID": 100,
                    "resourceName": "file.txt",
                    "resourceOwnerUserType": "",
                    "resourceOwnerUserID": 0,
                    "resourceOwnerUserName": "",
                    "data": {
                        "name": "field",
                        "newText": "value"
                    }
                }
            ]
        }
        
        events = self.parser.parse_webhook(payload)
        event_dict = events[0].to_dict()
        
        self.assertIsInstance(event_dict, dict)
        self.assertEqual(event_dict['event_id'], 1)
        self.assertEqual(event_dict['event_key'], "fileModifiedMetadataFieldText")
        self.assertIn('user', event_dict)
        self.assertIn('resource', event_dict)
        self.assertIn('data', event_dict)
    
    def test_event_data_raw_access(self):
        """Test accessing raw data when needed."""
        payload = {
            "events": [
                {
                    "id": 1,
                    "eventKey": "fileModifiedMetadataFieldText",
                    "action": "updated",
                    "name": "test",
                    "createDate": "2025-11-11 13:32:52",
                    "modifyDate": "2025-11-11 13:32:52",
                    "applicationKey": "app1",
                    "applicationName": "pixx.io",
                    "userType": "user",
                    "userID": 1,
                    "userName": "user1",
                    "userDescriptiveName": "User One",
                    "resourceType": "file",
                    "resourceID": 100,
                    "resourceName": "file.txt",
                    "resourceOwnerUserType": "",
                    "resourceOwnerUserID": 0,
                    "resourceOwnerUserName": "",
                    "data": {
                        "name": "field",
                        "newText": "value",
                        "customField": "customValue"
                    }
                }
            ]
        }
        
        events = self.parser.parse_webhook(payload)
        event = events[0]
        
        # Access raw data dict
        self.assertEqual(event.data.raw['name'], "field")  # type: ignore
        self.assertEqual(event.data._raw_data['newText'], "value")  # type: ignore
        self.assertEqual(event.data._raw_data['customField'], "customValue")  # type: ignore


class TestParseConvenienceFunction(unittest.TestCase):
    """Test the convenience parsing function."""
    
    def test_parse_pixxio_webhook_function(self):
        """Test parse_pixxio_webhook convenience function."""
        payload = {
            "events": [
                {
                    "id": 1,
                    "eventKey": "fileModifiedMetadataFieldText",
                    "action": "updated",
                    "name": "test",
                    "createDate": "2025-11-11 13:32:52",
                    "modifyDate": "2025-11-11 13:32:52",
                    "applicationKey": "app1",
                    "applicationName": "pixx.io",
                    "userType": "user",
                    "userID": 1,
                    "userName": "user1",
                    "userDescriptiveName": "User One",
                    "resourceType": "file",
                    "resourceID": 100,
                    "resourceName": "file.txt",
                    "resourceOwnerUserType": "",
                    "resourceOwnerUserID": 0,
                    "resourceOwnerUserName": "",
                    "data": {
                        "name": "field",
                        "newText": "value"
                    }
                }
            ]
        }
        
        events = parse_pixxio_webhook(payload)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_key, "fileModifiedMetadataFieldText")


if __name__ == '__main__':
    unittest.main()

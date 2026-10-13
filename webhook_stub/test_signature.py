#!/usr/bin/env python3
"""
Test script for PIXXIO webhook signature verification.
"""
import json
import os
import hmac
import hashlib
import requests
from datetime import datetime

# Configuration
WEBHOOK_URL = "http://localhost:5000/webhook"
WEBHOOK_SECRET = os.environ["PIXXIO_WEBHOOK_SECRET"]

# Sample webhook payload
payload = {
    "events": [
        {
            "id": "evt_12345",
            "eventKey": "fileModifiedMetadataFieldText",
            "action": "Updated",
            "name": "File Metadata Updated",
            "createDate": datetime.now().isoformat(),
            "userID": "user_123",
            "userName": "Test User",
            "resourceType": "file",
            "resourceID": "file_456",
            "data": {
                "fieldName": "testField",
                "oldValue": "old",
                "newValue": "new"
            }
        }
    ]
}

# Convert payload to JSON string (important: use exact formatting)
body = json.dumps(payload)
body_bytes = body.encode('utf-8')

# Calculate signature
signature = hmac.new(
    WEBHOOK_SECRET.encode(),
    body_bytes,
    hashlib.sha256
).hexdigest()

print("=" * 60)
print("PIXXIO Webhook Signature Test")
print("=" * 60)
print(f"\n📦 Payload:\n{json.dumps(payload, indent=2)}")
print(f"\n🔐 Secret: {WEBHOOK_SECRET}")
print(f"\n✍️  Signature: {signature}")
print(f"\n🌐 Sending to: {WEBHOOK_URL}")

# Send webhook with valid signature
print("\n" + "=" * 60)
print("Test 1: Valid Signature")
print("=" * 60)

headers_valid = {
    "x-hub-signature-256": signature,
    "Content-Type": "application/json"
}

response = requests.post(
    WEBHOOK_URL,
    data=body_bytes,
    headers=headers_valid
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

if response.status_code == 200:
    print("✅ Valid signature accepted!")
else:
    print(f"❌ Unexpected status: {response.status_code}")

# Send webhook with invalid signature
print("\n" + "=" * 60)
print("Test 2: Invalid Signature")
print("=" * 60)

headers_invalid = {
    "x-hub-signature-256": "invalid_signature_12345",
    "Content-Type": "application/json"
}

response = requests.post(
    WEBHOOK_URL,
    data=body_bytes,
    headers=headers_invalid
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

if response.status_code == 401:
    print("✅ Invalid signature rejected!")
else:
    print(f"❌ Expected 401, got: {response.status_code}")

# Send webhook without signature
print("\n" + "=" * 60)
print("Test 3: Missing Signature Header")
print("=" * 60)

headers_none = {
    "Content-Type": "application/json"
}

response = requests.post(
    WEBHOOK_URL,
    data=body_bytes,
    headers=headers_none
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

if response.status_code == 401:
    print("✅ Missing signature rejected!")
else:
    print(f"❌ Expected 401, got: {response.status_code}")

print("\n" + "=" * 60)
print("All tests completed!")
print("=" * 60)

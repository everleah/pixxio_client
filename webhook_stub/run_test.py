#!/usr/bin/env python3
"""Test webhook signature verification in Docker container."""
import subprocess
import json

test_code = """
import json
import hmac
import hashlib
import requests
import os

payload = json.dumps({
    "events": [
        {
            "id": "evt_12345",
            "eventKey": "fileModifiedMetadataFieldText",
            "action": "Updated",
            "resourceType": "file"
        }
    ]
})

secret = os.environ["PIXXIO_WEBHOOK_SECRET"]
sig = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()

print("Test 1: Valid Signature")
print(f"  Signature: {sig}")
r = requests.post(
    "http://localhost:5000/webhook",
    data=payload,
    headers={"x-hub-signature-256": sig, "Content-Type": "application/json"}
)
print(f"  Status: {r.status_code}")
print(f"  Response: {r.json()}")

print("\\nTest 2: Invalid Signature")
r = requests.post(
    "http://localhost:5000/webhook",
    data=payload,
    headers={"x-hub-signature-256": "invalid", "Content-Type": "application/json"}
)
print(f"  Status: {r.status_code}")
print(f"  Response: {r.json()}")

print("\\nTest 3: Missing Signature")
r = requests.post(
    "http://localhost:5000/webhook",
    data=payload,
    headers={"Content-Type": "application/json"}
)
print(f"  Status: {r.status_code}")
print(f"  Response: {r.json()}")
"""

cmd = f"docker exec pixxio-webhook-stub python3 -c {repr(test_code)}"
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

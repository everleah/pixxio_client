import json
import os
import hmac
import hashlib
import requests

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

print("=" * 60)
print("PIXXIO Webhook Signature Verification Tests")
print("=" * 60)

print("\nTest 1: Valid Signature")
print(f"  Signature: {sig}")
r = requests.post(
    "http://localhost:5000/webhook",
    data=payload,
    headers={"x-hub-signature-256": sig, "Content-Type": "application/json"}
)
print(f"  Status: {r.status_code}")
print(f"  Response: {r.json()}")
print(f"  Result: {'✅ PASS' if r.status_code == 200 else '❌ FAIL'}")

print("\nTest 2: Invalid Signature")
r = requests.post(
    "http://localhost:5000/webhook",
    data=payload,
    headers={"x-hub-signature-256": "invalid", "Content-Type": "application/json"}
)
print(f"  Status: {r.status_code}")
print(f"  Response: {r.json()}")
print(f"  Result: {'✅ PASS' if r.status_code == 401 else '❌ FAIL'}")

print("\nTest 3: Missing Signature")
r = requests.post(
    "http://localhost:5000/webhook",
    data=payload,
    headers={"Content-Type": "application/json"}
)
print(f"  Status: {r.status_code}")
print(f"  Response: {r.json()}")
print(f"  Result: {'✅ PASS' if r.status_code == 401 else '❌ FAIL'}")

print("\n" + "=" * 60)
print("Tests completed!")
print("=" * 60)

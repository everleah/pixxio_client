#!/bin/bash
# Test script for signature verification inside Docker

SECRET="${PIXXIO_WEBHOOK_SECRET:?PIXXIO_WEBHOOK_SECRET must be set}"

# Payload
PAYLOAD='{"events":[{"id":"evt_12345","eventKey":"fileModifiedMetadataFieldText","action":"Updated","name":"File Metadata Updated","createDate":"2025-11-11T14:48:24.431784","userID":"user_123","userName":"Test User","resourceType":"file","resourceID":"file_456","data":{"fieldName":"testField","oldValue":"old","newValue":"new"}}]}'

# Calculate signature
SIGNATURE=$(echo -n "$PAYLOAD" | sha256sum | awk '{print $1}' | xxd -r -p | base64 | tr -d '=\n')

# Actually, use Python for proper HMAC
SIGNATURE=$(python3 -c "
import hmac, hashlib, json
payload = '$PAYLOAD'
secret = '$SECRET'
sig = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
print(sig)
")

echo "====== Test 1: Valid Signature ======"
echo "Signature: $SIGNATURE"

curl -X POST http://localhost:5000/webhook \
  -H "x-hub-signature-256: $SIGNATURE" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  -w "\nStatus: %{http_code}\n"

echo -e "\n====== Test 2: Invalid Signature ======"
curl -X POST http://localhost:5000/webhook \
  -H "x-hub-signature-256: invalid_signature" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  -w "\nStatus: %{http_code}\n"

echo -e "\n====== Test 3: Missing Signature ======"
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  -w "\nStatus: %{http_code}\n"

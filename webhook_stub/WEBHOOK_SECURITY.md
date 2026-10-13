# PIXXIO Webhook Security

## Webhook Signature Verification

PIXXIO sends webhooks with an **HMAC-SHA256 signature** in the HTTP header for security verification.

### Header: `x-hub-signature-256`

```
x-hub-signature-256: c1382c2771b55a79aa22430329b36e09dec46aa25c575ce543d23e7fd5b877a0
```

This is a SHA256 HMAC of the webhook payload, signed with your webhook secret key.

## How to Verify Webhook Authenticity

### Step 1: Get Your Webhook Secret

Configure your webhook in PIXXIO admin panel and note the **secret key** provided.

### Step 2: Verify the Signature

When PIXXIO sends a webhook:

1. Extract the signature from header: `x-hub-signature-256`
2. Get the raw webhook body (JSON payload)
3. Calculate: `HMAC-SHA256(payload, secret_key)`
4. Compare with the header signature

**If they match**: Webhook is authentic ✅

### Python Example

```python
import hmac
import hashlib
import json

def verify_webhook(request_body: str, header_signature: str, secret: str) -> bool:
    """Verify PIXXIO webhook signature."""
    # Calculate expected signature
    expected_signature = hmac.new(
        secret.encode(),
        request_body.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Compare signatures
    return hmac.compare_digest(expected_signature, header_signature)

# Usage
webhook_secret = "your_webhook_secret_from_pixxio"
raw_body = '{"events": [...]}'  # Raw JSON as string
signature_header = "c1382c2771b55a79aa22430329b36e09dec46aa25c575ce543d23e7fd5b877a0"

is_valid = verify_webhook(raw_body, signature_header, webhook_secret)
print(f"Webhook is valid: {is_valid}")
```

### Node.js Example

```javascript
const crypto = require('crypto');

function verifyWebhook(rawBody, headerSignature, secret) {
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(rawBody)
    .digest('hex');
  
  return crypto.timingSafeEqual(
    Buffer.from(expectedSignature),
    Buffer.from(headerSignature)
  );
}

// Usage
const webhookSecret = "your_webhook_secret_from_pixxio";
const rawBody = '{"events": [...]}';
const signatureHeader = "c1382c2771b55a79aa22430329b36e09dec46aa25c575ce543d23e7fd5b877a0";

const isValid = verifyWebhook(rawBody, signatureHeader, webhookSecret);
console.log(`Webhook is valid: ${isValid}`);
```

### FastAPI Example (Production Ready)

```python
from fastapi import FastAPI, Request, HTTPException
import hmac
import hashlib

app = FastAPI()

WEBHOOK_SECRET = "your_webhook_secret"  # Store in environment variable!

@app.post("/webhook")
async def webhook(request: Request):
    """Receive and verify PIXXIO webhooks."""
    
    # Get signature from header
    signature = request.headers.get("x-hub-signature-256")
    if not signature:
        raise HTTPException(status_code=401, detail="Missing signature")
    
    # Get raw body for verification
    body = await request.body()
    
    # Verify signature
    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(expected_signature, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Process webhook (signature verified ✅)
    data = await request.json()
    # ... handle webhook ...
    
    return {"success": True}
```

## Finding Your Webhook Secret

1. Go to webhook settings in PIXXIO admin
2. View webhook configuration
3. Secret key should be displayed there
4. Copy and store securely (e.g., in environment variable)

## Security Best Practices

✅ **DO:**
- Store webhook secret in environment variables, not in code
- Always verify the signature before processing
- Use `hmac.compare_digest()` for signature comparison (timing-safe)
- Log successful verifications (no secrets in logs!)
- Reject webhooks with invalid signatures

❌ **DON'T:**
- Hardcode secrets in source code
- Use string comparison (`==`) for signature verification (vulnerable to timing attacks)
- Log the signature or secret values
- Process webhooks without verification
- Commit secrets to version control

## Debugging with Webhook Stub

The webhook stub saves all headers, including the signature:

1. Visit dashboard: `https://<your-stub-host>`
2. Click "🔐 Headers" link
3. Find the `x-hub-signature-256` header
4. Use it to test your verification code

## Environment Variable Setup

```bash
# .env file (never commit!)
PIXXIO_WEBHOOK_SECRET=your_secret_here_from_pixxio_admin

# Code
import os
webhook_secret = os.environ.get("PIXXIO_WEBHOOK_SECRET")
```

## Testing Webhook Security

Use the webhook stub to capture real signatures:

```bash
# 1. Send webhook from PIXXIO
# 2. Check dashboard → "🔐 Headers"
# 3. Copy the x-hub-signature-256 value
# 4. Test your verification code with the captured signature
```

## References

- HMAC-SHA256: Standard webhook authentication method
- Timing-safe comparison: Protection against timing attacks
- PIXXIO API: https://api.pixxio.com/docs


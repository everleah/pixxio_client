# PIXXIO Webhook Stub - Usage Guide

## Overview

The webhook stub server captures and displays webhook events from PIXXIO. This guide covers how to use the web interface, API, and configure PIXXIO to send webhooks.

## Web Dashboard

### Accessing the Dashboard

- **Local**: `http://localhost:5000`
- **Remote**: `https://pixxiostub.claudiapps.de`

### Dashboard Features

#### 1. **Status Bar**
```
🪝 PIXXIO Webhook Stub
● ONLINE | Endpoint: POST /webhook | Storage: /data/webhooks | Events received: 42
```

- Green dot indicates service is running
- Shows webhook endpoint URL
- Displays total events stored
- Shows storage directory

#### 2. **Event Table**

| Column | Description |
|--------|-------------|
| **Timestamp** | When the webhook was received (YYYY-MM-DD HH:MM:SS) |
| **Event Type** | Event name from PIXXIO (e.g., `file.uploaded`, `metadata.updated`) |
| **Filename** | Stored JSON file name (webhook_YYYYMMDD_HHMMSS_mmm.json) |
| **Size** | File size in KB |
| **Actions** | Download or Delete buttons |

#### 3. **Empty State**

When no events have been received:
```
📭
No webhook events received yet.
Configure PIXXIO to send webhooks to:
http://localhost:5000/webhook  (or https://pixxiostub.claudiapps.de/webhook)
```

### Dashboard Actions

#### Download Event

```
Click "Download" button next to event
```

Downloads the webhook JSON to your computer. File name: `webhook_YYYYMMDD_HHMMSS_mmm.json`

Use this to:
- Inspect webhook payload structure
- Archive important events
- Share with PIXXIO support

#### Delete Event

```
Click "Delete" button → Confirm in dialog
```

Removes single event from storage. Use to:
- Clean up test events
- Remove sensitive data
- Manage storage space

#### Clear All Events

```
Click "Clear All Events" button (orange) → Confirm in dialog
```

Removes all stored webhooks. Use to:
- Reset for fresh testing
- Free up storage space
- Start monitoring from clean slate

---

## API Usage

### Base URL
- **Local**: `http://localhost:5000`
- **Remote**: `https://pixxiostub.claudiapps.de`

### Interactive API Docs

**Swagger UI** (Try endpoints live):
```
https://pixxiostub.claudiapps.de/docs
```

**ReDoc** (Read-only reference):
```
https://pixxiostub.claudiapps.de/redoc
```

### API Endpoints

#### 1. **GET /** - Web Dashboard
```bash
curl https://pixxiostub.claudiapps.de/
```
Returns HTML page with event list and controls.

#### 2. **POST /webhook** - Receive Webhook
```bash
curl -X POST https://pixxiostub.claudiapps.de/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "event": "file.uploaded",
    "fileId": 12345,
    "fileName": "photo.jpg",
    "timestamp": "2025-11-11T12:30:00Z"
  }'
```

**Response** (201 Created):
```json
{
  "success": true,
  "message": "Webhook received and stored as webhook_20251111_123000_001.json",
  "filename": "webhook_20251111_123000_001.json"
}
```

#### 3. **GET /download/{filename}** - Download Event JSON
```bash
# List files first to get filename
curl -s https://pixxiostub.claudiapps.de/ | grep webhook_

# Download specific event
curl -O https://pixxiostub.claudiapps.de/download/webhook_20251111_123000_001.json
```

Returns JSON file with webhook payload.

#### 4. **POST /delete/{filename}** - Delete Event
```bash
curl -X POST https://pixxiostub.claudiapps.de/delete/webhook_20251111_123000_001.json
```

**Response**:
```json
{
  "success": true,
  "message": "Deleted webhook_20251111_123000_001.json"
}
```

#### 5. **POST /clear** - Delete All Events
```bash
curl -X POST https://pixxiostub.claudiapps.de/clear
```

**Response**:
```json
{
  "success": true,
  "message": "Deleted 42 events"
}
```

#### 6. **GET /health** - Health Check
```bash
curl https://pixxiostub.claudiapps.de/health
```

**Response**:
```json
{
  "status": "ok",
  "storage_dir": "/data/webhooks"
}
```

Use for monitoring and uptime checks.

---

## PIXXIO Configuration

### Step 1: Get Webhook URL

**Local**: `http://localhost:5000/webhook`
**Remote**: `https://pixxiostub.claudiapps.de/webhook`

### Step 2: Configure in PIXXIO Admin

1. Log in to PIXXIO as administrator
2. Navigate to **Settings** → **Webhooks** (or similar)
3. Click **Add Webhook** or **New Webhook**
4. Fill in the form:

   | Field | Value |
   |-------|-------|
   | **Name** | PIXXIO Webhook Stub (or any descriptive name) |
   | **URL** | `https://pixxiostub.claudiapps.de/webhook` |
   | **Method** | `POST` |
   | **Content-Type** | `application/json` |
   | **Events** | Select events to monitor (see below) |
   | **Active** | ✓ Enabled |

### Step 3: Select Events

Choose which PIXXIO events to monitor.

**PIXXIO Webhook Event Structure:**

PIXXIO webhooks are now **documented through actual payloads**! The webhook structure is:

```json
{
  "events": [
    {
      "id": 164137675,
      "eventKey": "fileModifiedMetadataFieldText",
      "action": "updated",
      "name": "updateFile",
      "createDate": "2025-11-11 13:32:52",
      "userID": 130052009,
      "userName": "admin_claudius",
      "resourceType": "file",
      "resourceID": 1930337128,
      "resourceName": "-",
      "data": { ... }
    }
  ]
}
```

**Known Event Types** (discovered from webhook stub):
- `fileModifiedMetadataFieldText` - Text metadata field changed
- `fileModifiedFileStateID` - File state/status changed
- `fileModifiedMetadataFieldMultiSelectionsAdded` - Multi-select metadata updated

**Recommended approach**:
1. Start with **"Select All Events"** in PIXXIO to capture everything
2. Monitor webhook stub dashboard for incoming events
3. Review captured payloads to understand available event types
4. Then narrow down to specific event types you need

### Step 4: Test Connection

1. Click **Test Webhook** button in PIXXIO
2. PIXXIO sends a test payload to your webhook stub
3. Check webhook stub dashboard
4. Event should appear in the list immediately

### Step 5: Monitor Events

Visit dashboard and watch for incoming webhooks as PIXXIO generates events.

---

## Common Use Cases

### ⚠️ Important Note About Event Types

The following use cases reference specific event names like `file.uploaded`, `metadata.changed`, etc. These are **educated guesses** based on typical DAM system behavior. 

**The actual event types and payload structures are not documented by PIXXIO.** You'll need to:

1. Test what events PIXXIO actually sends
2. Capture payloads in the webhook stub
3. Analyze the JSON to understand the structure
4. Document findings for your integration

This webhook stub exists **precisely to help you discover** what PIXXIO webhooks look like!

---

### Use Case 1: Monitor File Uploads

**Goal**: See when users upload files to PIXXIO

**Setup**:
1. Enable file-related events in webhook (or select all to discover)
2. Visit dashboard at `https://pixxiostub.claudiapps.de`
3. Trigger file upload in PIXXIO
4. Watch webhook appear in real-time on dashboard

**Analysis**:
- View event JSON to see file details
- Extract fileId to cross-reference in PIXXIO
- Check timestamps for audit trail
- **Document the actual event type and payload for future reference**

**Example Payload** (structure may vary):
```json
{
  "event": "file.uploaded",
  "fileId": 98765,
  "fileName": "project-proposal.pdf",
  "userId": 123,
  "uploadedAt": "2025-11-11T14:30:00Z",
  "fileSize": 2048576
}
```

### Use Case 2: Metadata Change Tracking

**Goal**: Track when asset metadata (keywords, ratings, etc.) is modified

**Setup**:
1. Enable `metadata.changed` events
2. Update asset metadata in PIXXIO
3. Check webhook stub for change event

**Analyze**:
- See which fields were modified
- Track who made changes and when
- Audit trail for compliance

### Use Case 3: Job Completion Notifications

**Goal**: Know when long-running tasks (export, conversion) complete

**Setup**:
1. Enable `job.completed` events
2. Start export/conversion job in PIXXIO
3. Monitor webhook stub for completion event

**Benefits**:
- Real-time notifications instead of polling
- Trigger downstream processes automatically
- Track job success/failure rates

### Use Case 4: User Activity Monitoring

**Goal**: Track user actions (login, logout, changes)

**Setup**:
1. Enable user-related events (`user.login`, `user.logout`, `user.updated`)
2. Monitor user activity in webhook stub
3. Build audit log from webhook data

**Use for**:
- Security monitoring
- Compliance reporting
- User behavior analysis

### Use Case 5: Integration Testing

**Goal**: Test webhook integration before production

**Steps**:
1. Deploy webhook stub to test server
2. Configure PIXXIO test environment to send webhooks
3. Verify payload structure and timing
4. Validate all event types are captured
5. Check timestamp precision and data completeness

---

## Analyzing Webhook Payloads

### Step 1: Receive Event

Events appear on dashboard as they arrive.

### Step 2: Download JSON

Click **Download** button to save event locally.

### Step 3: View in Editor

Open JSON in your text editor to inspect:

```json
{
  "event": "file.uploaded",
  "fileId": 12345,
  "fileName": "report.xlsx",
  "userId": 42,
  "timestamp": "2025-11-11T15:45:30Z",
  "metadata": {
    "format": "xlsx",
    "size": 524288,
    "dimensions": "1024x768"
  }
}
```

### Step 4: Extract Key Information

- **event**: Event type (use for filtering/routing)
- **fileId/assetId**: Reference for lookups
- **timestamp**: When event occurred (UTC)
- **userId**: Who triggered the event
- **metadata**: Event-specific data

### Step 5: Use in Integration

Once you understand the payload structure:

1. **Build integration logic** using extracted fields
2. **Validate data** matches your expectations
3. **Set up error handling** for missing fields
4. **Deploy to production** with confidence

---

## Automation Examples

### Example 1: Process Events with Script

```python
import requests
import json
import time

# Monitor webhook stub
while True:
    response = requests.get('https://pixxiostub.claudiapps.de/')
    # Parse HTML and extract events
    # Process each event
    # Do something with the data
    time.sleep(5)  # Check every 5 seconds
```

### Example 2: Forward Webhooks

```bash
# Receive from PIXXIO, forward to another service
curl -X POST https://pixxiostub.claudiapps.de/webhook \
  -d '{"event":"file.uploaded","fileId":12345}' \
  && curl -X POST https://your-system.com/webhook \
       -d '{"source":"pixxio","event":"file.uploaded","fileId":12345}'
```

### Example 3: Archive Events

```bash
# Backup all events daily
0 2 * * * docker exec pixxio-webhook-stub \
  tar czf /data/webhooks/archive-$(date +%Y%m%d).tar.gz /data/webhooks/*.json
```

---

## Storage & Retention

### Event Storage Location

- **Container**: `/data/webhooks/`
- **Host** (Netcup): `/var/lib/docker/volumes/webhook_stub_webhook_data/_data`

### Filename Format

```
webhook_YYYYMMDD_HHMMSS_mmm.json
         └─────┬─────┘ └──┬──┘ └┬┘
           Date/Time    Hour/Min/Sec  Milliseconds
```

Example: `webhook_20251111_143000_523.json`
- Date: 2025-11-11
- Time: 14:30:00 (2:30 PM)
- Milliseconds: 523

### Retention Policy

By default, all events are kept indefinitely.

**To manage storage**:

1. **Delete individual events**:
   - Dashboard → Click "Delete" button

2. **Clear all events**:
   - Dashboard → Click "Clear All Events"

3. **Automated cleanup** (cron job):
   ```bash
   # Delete events older than 30 days
   find /var/lib/docker/volumes/webhook_stub_webhook_data/_data -name "*.json" -mtime +30 -delete
   ```

4. **Archive before cleanup**:
   ```bash
   # Backup to S3 or cloud storage
   tar czf webhooks-backup-$(date +%Y%m%d).tar.gz /data/webhooks/
   aws s3 cp webhooks-backup-*.tar.gz s3://my-backups/
   ```

---

## Performance Tips

### Tip 1: Filter Events in PIXXIO

Instead of capturing ALL events, select only what you need:
- Reduces storage consumption
- Faster dashboard loading
- Easier to find relevant events

### Tip 2: Regular Cleanup

Clean up old test events periodically:
- Use dashboard "Clear All" button after testing
- Or delete old files from command line

### Tip 3: Monitor Dashboard Performance

If dashboard loads slowly:
1. Note number of events
2. If > 1000 events, clear some
3. Archive to backup if needed

### Tip 4: Use API for Bulk Operations

For automated processing, use API instead of dashboard:
```bash
# Clear all via API (faster than web interface)
curl -X POST https://pixxiostub.claudiapps.de/clear
```

---

## Troubleshooting Usage

### Issue: Events not appearing

**Check**:
1. Is webhook stub running? `https://pixxiostub.claudiapps.de/health`
2. Is PIXXIO webhook configured correctly? (URL, method, events)
3. Did you click "Save" in PIXXIO after configuration?
4. Try manual test from PIXXIO → "Test Webhook" button

### Issue: Old events disappearing

**Cause**: Container restarted without persistent volume

**Fix**: Events should persist across restarts. If they don't:
1. Check volume exists: `docker volume ls`
2. Verify volume mount: `docker-compose ps`
3. Rebuild: `docker-compose build && docker-compose up -d`

### Issue: Can't download event file

**Check**:
1. Event exists in list
2. Filename is correct
3. Storage has space: `df -h`
4. File permissions: `docker exec pixxio-webhook-stub ls -la /data/webhooks/`

### Issue: Wrong event data in payload

**Likely cause**: PIXXIO webhook triggered wrong event

**Solution**:
1. Verify event selection in PIXXIO config
2. Check PIXXIO logs for what events are being sent
3. Contact PIXXIO support with webhook stub event JSON

---

## Best Practices

✅ **DO**:
- Test webhooks in development/staging first
- Archive important events before clearing
- Monitor `/health` endpoint for uptime
- Document webhook payload structure
- Use descriptive webhook names in PIXXIO
- Review event payloads regularly

❌ **DON'T**:
- Leave test events forever (clean up periodically)
- Expose webhook URL to untrusted networks
- Store sensitive data without encryption
- Clear all events without backup
- Modify webhook files directly
- Run without SSL/TLS on public internet

---

## Advanced Usage

### Integration with External Systems

Once you understand webhook structure, integrate with:
- **Slack**: Post events to Slack channel
- **Database**: Store events in PostgreSQL/MongoDB
- **Message Queue**: Send to RabbitMQ/Kafka
- **Analytics**: Log to ELK/Datadog
- **Automation**: Trigger other workflows

### Custom Processing

Example: Extract fileId from webhook and fetch full asset details:

```python
import requests
import json

# Receive webhook
webhook_data = requests.post('...').json()
file_id = webhook_data['fileId']

# Query PIXXIO API for full details
asset = requests.get(f'https://api.pixxio.com/v1/files/{file_id}', 
                     headers={'Authorization': f'Bearer {token}'}).json()

# Use asset data
print(f"Downloaded: {asset['name']} ({asset['size']} bytes)")
```

---

## Support Resources

- **Setup Guide**: See SETUP.md
- **Deployment Guide**: See DEPLOYMENT.md
- **Troubleshooting**: See TROUBLESHOOTING.md
- **API Docs**: Visit `/docs` endpoint
- **PIXXIO Docs**: https://api.pixxio.com/docs


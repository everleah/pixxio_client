# PIXXIO Webhook Stub - Deployment Guide

## Overview

The webhook stub is a FastAPI-based service that receives and stores webhook events from PIXXIO. It's designed to run on your Netcup server behind a Traefik reverse proxy with automatic HTTPS/SSL via Let's Encrypt.

## Architecture

```
┌─────────────────────────────────────────┐
│     PIXXIO (External Service)           │
│  Sends webhooks to HTTPS endpoint       │
└──────────────┬──────────────────────────┘
               │ HTTPS POST
               │ pixxiostub.claudiapps.de/webhook
               ▼
┌─────────────────────────────────────────┐
│  Traefik (Reverse Proxy)                │
│  - SSL/TLS termination                  │
│  - Let's Encrypt certificate mgmt       │
│  - Route to internal webhook service    │
└──────────────┬──────────────────────────┘
               │ HTTP (internal only)
               │ port 5000
               ▼
┌─────────────────────────────────────────┐
│  FastAPI Webhook Stub Container         │
│  - Receives POST /webhook               │
│  - Stores JSON with timestamps          │
│  - Serves dashboard at GET /            │
│  - Exposes /health for monitoring       │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Docker Volume: webhook_data            │
│  Persists webhook events across restarts│
└─────────────────────────────────────────┘
```

## Prerequisites

- Docker and Docker Compose installed
- Traefik reverse proxy running on the server with `claudiapp-net` network
- DNS record: `pixxiostub.claudiapps.de` → your server IP
- Let's Encrypt certificate resolver named `letsencrypt` configured in Traefik

## Local Development & Testing

### Quick Start (Local)

```bash
cd webhook_stub
python app.py
```

Server runs on `http://localhost:5000`

### Docker Compose (Local)

```bash
cd webhook_stub
docker-compose -f docker-compose.yml up -d
```

Access at `http://localhost:5000`

### Test Webhook Locally

```bash
# Send test payload
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"event":"test.event","timestamp":"2025-11-11T12:00:00Z","data":{"test":true}}'

# Check health
curl http://localhost:5000/health

# View dashboard
curl http://localhost:5000/
```

## Netcup Deployment

### Prerequisites on Netcup Server

1. **Traefik running** with:
   - External network: `claudiapp-net`
   - Certificate resolver: `letsencrypt`
   - HTTPS entry point: `websecure` on port 443

2. **DNS record configured**:
   ```
   pixxiostub.claudiapps.de  A  <your-netcup-server-ip>
   ```

3. **SSH access** to your Netcup server

### Deployment Steps

1. **Clone or copy the webhook_stub folder**:

   ```bash
   ssh user@netcup-server
   cd /root
   git clone <repo-url>  # or copy webhook_stub folder
   cd pixxio_client/webhook_stub
   ```

2. **Build the Docker image**:

   ```bash
   docker-compose build --no-cache
   ```

3. **Deploy the container**:

   ```bash
   docker-compose up -d
   ```

4. **Verify deployment**:

   ```bash
   # Check container status
   docker-compose ps

   # Check logs
   docker-compose logs -f webhook-stub

   # Check container health
   docker inspect pixxio-webhook-stub | grep -A 20 '"Health"'
   ```

5. **Test HTTPS endpoint**:

   ```bash
   curl -X GET https://pixxiostub.claudiapps.de/health

   # Send test webhook
   curl -X POST https://pixxiostub.claudiapps.de/webhook \
     -H "Content-Type: application/json" \
     -d '{"event":"deployment.test","timestamp":"2025-11-11T12:00:00Z"}'
   ```

6. **Access web dashboard**:

   Open browser: `https://pixxiostub.claudiapps.de`

## Docker Compose Configuration

The `docker-compose.yml` is configured for Traefik integration:

```yaml
services:
  webhook-stub:
    build: .                              # Build from Dockerfile
    container_name: pixxio-webhook-stub
    restart: unless-stopped               # Auto-restart on failure
    volumes:
      - webhook_data:/data/webhooks      # Persistent storage
    environment:
      - WEBHOOK_STORAGE_DIR=/data/webhooks
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.webhook-stub.rule=Host(`pixxiostub.claudiapps.de`)"
      - "traefik.http.routers.webhook-stub.entrypoints=websecure"  # HTTPS
      - "traefik.http.routers.webhook-stub.tls.certresolver=letsencrypt"
      - "traefik.http.services.webhook-stub.loadbalancer.server.port=5000"
    networks:
      - claudiapp-net                    # External Traefik network
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Web dashboard with webhook list |
| GET | `/docs` | Interactive API documentation (Swagger UI) |
| POST | `/webhook` | Receive webhook from PIXXIO |
| GET | `/download/{filename}` | Download webhook JSON |
| POST | `/delete/{filename}` | Delete specific event |
| POST | `/clear` | Delete all events |
| GET | `/health` | Health check (for monitoring) |

## PIXXIO Webhook Configuration

1. **In PIXXIO Admin Panel**, configure webhook:
   - **URL**: `https://pixxiostub.claudiapps.de/webhook`
   - **Method**: `POST`
   - **Content-Type**: `application/json`
   - **Events**: Select events to monitor (file upload, metadata changes, etc.)

2. **Test webhook**:
   - PIXXIO will send a test payload
   - Check webhook stub dashboard: `https://pixxiostub.claudiapps.de`
   - Event should appear in the list

## Storage

Webhook events are stored in the Docker volume `webhook_data`:

- **Container path**: `/data/webhooks`
- **Host path** (on Netcup): `/var/lib/docker/volumes/webhook_stub_webhook_data/_data`
- **File format**: `webhook_YYYYMMDD_HHMMSS_mmm.json` (millisecond precision)

### Access stored webhooks

```bash
# List all stored webhooks
docker exec pixxio-webhook-stub ls -lah /data/webhooks

# View specific webhook
docker exec pixxio-webhook-stub cat /data/webhooks/webhook_20251111_121500_123.json

# Download via web interface
# Visit: https://pixxiostub.claudiapps.de
# Click "Download" on desired event
```

## Troubleshooting

### Container is unhealthy

**Error**: Health check failing with `ModuleNotFoundError: requests`

**Solution**: Rebuild image with requests package:
```bash
docker-compose build --no-cache
docker-compose up -d
```

### No webhooks received

1. **Check connectivity**:
   ```bash
   curl -v https://pixxiostub.claudiapps.de/health
   ```

2. **Check firewall**: Ensure port 443 is open

3. **Verify DNS**: 
   ```bash
   nslookup pixxiostub.claudiapps.de
   ```

4. **Check Traefik logs**:
   ```bash
   docker logs traefik
   ```

5. **Check webhook stub logs**:
   ```bash
   docker-compose logs -f webhook-stub
   ```

### Storage not persisting

1. **Verify volume exists**:
   ```bash
   docker volume ls | grep webhook_data
   ```

2. **Check volume permissions**:
   ```bash
   docker exec pixxio-webhook-stub ls -la /data/webhooks
   ```

3. **Inspect volume**:
   ```bash
   docker volume inspect webhook_stub_webhook_data
   ```

### Traefik not routing correctly

1. **Check labels are correct** in docker-compose.yml

2. **Verify network**:
   ```bash
   docker network inspect claudiapp-net
   docker inspect pixxio-webhook-stub | grep Networks
   ```

3. **Check Traefik routes**:
   ```bash
   curl http://localhost:8080/api/routes  # Traefik dashboard
   ```

## Monitoring

### Health Check

The container includes a built-in health check:

```bash
# Manual health check
curl https://pixxiostub.claudiapps.de/health

# Expected response
{"status":"ok","storage_dir":"/data/webhooks"}
```

### View Logs

```bash
# Real-time logs
docker-compose logs -f webhook-stub

# Last 100 lines
docker-compose logs --tail=100 webhook-stub

# With timestamps
docker-compose logs --timestamps webhook-stub
```

### Monitor Events Received

```bash
# Count stored events
docker exec pixxio-webhook-stub ls /data/webhooks | wc -l

# Watch for new events in real-time
watch -n 1 'docker exec pixxio-webhook-stub ls -lart /data/webhooks | tail -5'
```

## Maintenance

### Update webhook stub

1. **Pull latest code**:
   ```bash
   git pull origin main
   ```

2. **Rebuild and redeploy**:
   ```bash
   cd webhook_stub
   docker-compose build --no-cache
   docker-compose up -d
   ```

3. **Verify health**:
   ```bash
   docker-compose ps
   curl https://pixxiostub.claudiapps.de/health
   ```

### Backup stored webhooks

```bash
# Copy all events to backup location
docker run --rm -v webhook_stub_webhook_data:/data/webhooks \
  -v /root/backups:/backup \
  busybox cp -r /data/webhooks/* /backup/
```

### Clear old events

```bash
# Via web interface
# Visit: https://pixxiostub.claudiapps.de
# Click "Clear All Events"

# Or via API
curl -X POST https://pixxiostub.claudiapps.de/clear
```

### Stop the service

```bash
docker-compose down
```

### Restart the service

```bash
docker-compose up -d
```

## Security Notes

⚠️ **Important**: This is a development/analysis tool. For production use:

1. **Add authentication** to the web interface
2. **Implement rate limiting** for `/webhook` endpoint
3. **Add request validation** to verify webhook source (PIXXIO IP whitelist)
4. **Rotate stored webhooks** - implement retention policy
5. **Monitor API keys** - webhooks may contain sensitive data
6. **Use environment variables** for configuration instead of hardcoding
7. **Enable audit logging** for who accessed which events

## API Documentation

### Interactive Swagger UI

```
https://pixxiostub.claudiapps.de/docs
```

Try out endpoints directly in the browser!

### ReDoc Documentation

```
https://pixxiostub.claudiapps.de/redoc
```

## Support

For issues or improvements:

1. Check logs: `docker-compose logs`
2. Test health: `curl https://pixxiostub.claudiapps.de/health`
3. Review webhook payload in dashboard
4. Check PIXXIO webhook configuration
5. Verify Traefik configuration and routing

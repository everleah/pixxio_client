# PIXXIO Webhook Stub - Setup Guide

## Quick Reference

- **Service**: PIXXIO webhook receiver and analyzer
- **Technology**: FastAPI, Uvicorn, Docker, Traefik
- **Access**: `https://pixxiostub.claudiapps.de`
- **Storage**: Docker volume (`webhook_data`) - persistent
- **Health Check**: `https://pixxiostub.claudiapps.de/health`

## File Structure

```
webhook_stub/
├── app.py                    # FastAPI application
├── Dockerfile               # Docker image definition
├── docker-compose.yml       # Traefik + networking config
├── README.md               # User guide
├── DEPLOYMENT.md           # This file - detailed deployment
└── SETUP.md               # Quick setup reference
```

## 1-Minute Local Test

```bash
cd webhook_stub
python app.py
# Open http://localhost:5000
```

## 5-Minute Netcup Deployment

```bash
# SSH into Netcup server
ssh user@netcup-server

# Navigate to project
cd /root/pixxio_client/webhook_stub

# Build image
docker-compose build --no-cache

# Deploy
docker-compose up -d

# Wait 10 seconds for startup, then test
curl https://pixxiostub.claudiapps.de/health

# View dashboard
# Open: https://pixxiostub.claudiapps.de
```

## Key Components

### 1. **app.py**
- FastAPI application
- Endpoints: `/webhook`, `/download/`, `/delete/`, `/clear/`, `/health/`, `/`
- Storage: JSON files in `/data/webhooks/`
- Auto-generated API docs at `/docs`

### 2. **Dockerfile**
- Base image: `python:3.11-slim`
- Dependencies: FastAPI, Uvicorn, Jinja2, Requests
- Healthcheck: Tests `/health` endpoint every 30s
- Port: 5000 (internal only, exposed via Traefik)

### 3. **docker-compose.yml**
- Service: `webhook-stub`
- Network: `claudiapp-net` (external, shared with Traefik)
- Volume: `webhook_data` (persistent)
- Traefik labels for HTTPS routing
- Container: `pixxio-webhook-stub`

## Configuration Files Explained

### docker-compose.yml Traefik Labels

```yaml
labels:
  - "traefik.enable=true"
    # Enable Traefik routing
  
  - "traefik.http.routers.webhook-stub.rule=Host(`pixxiostub.claudiapps.de`)"
    # Route requests to this domain
  
  - "traefik.http.routers.webhook-stub.entrypoints=websecure"
    # Use HTTPS entry point
  
  - "traefik.http.routers.webhook-stub.tls.certresolver=letsencrypt"
    # Use Let's Encrypt for SSL cert
  
  - "traefik.http.services.webhook-stub.loadbalancer.server.port=5000"
    # Forward to port 5000 inside container
```

### Environment Variables

```bash
# In docker-compose.yml
WEBHOOK_STORAGE_DIR=/data/webhooks
# Where to store received webhook JSONs
```

## Common Tasks

### View running container
```bash
docker-compose ps
```

### View logs
```bash
docker-compose logs -f webhook-stub
```

### Check container health
```bash
docker inspect pixxio-webhook-stub | grep -A 20 '"Health"'
```

### Restart container
```bash
docker-compose restart
```

### Stop container
```bash
docker-compose down
```

### Delete all webhooks
```bash
docker volume rm webhook_stub_webhook_data
docker-compose up -d
```

## Testing PIXXIO Integration

1. **Get webhook URL**:
   ```
   https://pixxiostub.claudiapps.de/webhook
   ```

2. **In PIXXIO Admin**:
   - Add webhook
   - URL: (from above)
   - Method: POST
   - Events: Select what to monitor

3. **Send test from PIXXIO**:
   - PIXXIO should POST to `/webhook`
   - Check dashboard for received event
   - View event JSON via download link

## Performance & Limits

| Aspect | Value | Notes |
|--------|-------|-------|
| Max webhook size | ~50MB | Limited by FastAPI/Uvicorn |
| Storage | Unlimited | Limited by disk space |
| Concurrent requests | 1000s | Uvicorn async workers |
| Health check interval | 30s | Configurable in Dockerfile |
| Request timeout | 10s | Healthcheck timeout |

## Troubleshooting Matrix

| Problem | Cause | Solution |
|---------|-------|----------|
| Container unhealthy | Requests module missing | `docker-compose build --no-cache` |
| Can't access domain | DNS not resolved | `nslookup pixxiostub.claudiapps.de` |
| 404 on HTTPS endpoint | Traefik routing issue | Check `docker logs traefik` |
| No webhooks appear | PIXXIO not sending | Verify URL in PIXXIO config |
| Storage not persisting | Volume issue | `docker volume inspect webhook_stub_webhook_data` |

## Logs & Debugging

### Application logs
```bash
docker-compose logs webhook-stub
```

### Traefik routing debug
```bash
docker logs traefik | grep webhook
```

### Check if container is running
```bash
docker ps | grep pixxio-webhook
```

### View container IP (internal)
```bash
docker inspect pixxio-webhook-stub | grep IPAddress
```

### Test endpoint from within container
```bash
docker exec pixxio-webhook-stub curl http://localhost:5000/health
```

## Next Steps

1. Deploy on Netcup
2. Configure PIXXIO webhook to send to `https://pixxiostub.claudiapps.de/webhook`
3. Monitor dashboard at `https://pixxiostub.claudiapps.de`
4. Analyze webhook payloads to understand PIXXIO events
5. Extend with custom logic as needed

---

For detailed deployment guide, see **DEPLOYMENT.md**  
For user guide, see **README.md**

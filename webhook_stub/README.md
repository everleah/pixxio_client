# PIXXIO Webhook Stub

A FastAPI-based web server that receives and stores webhook events from PIXXIO. Since PIXXIO's webhook functionality is not fully documented, this stub server helps you understand and analyze the webhook payloads sent by PIXXIO.

## Features

- **Async Webhook Receiver**: FastAPI-based listener for POST requests at `/webhook` endpoint
- **Event Storage**: Stores incoming JSON payloads with millisecond-precision timestamps
- **Web Dashboard**: Browse received events with timestamps, event types, and file sizes
- **Download**: Download individual webhook events as JSON files
- **Delete**: Remove individual events or clear all events at once
- **Docker Ready**: Runs as a containerized service with health checks
- **Auto Documentation**: Built-in interactive API docs at `/docs`
- **Performance**: Async processing for high-throughput webhook handling

## Quick Start

### Using Docker Compose (Recommended)

```bash
cd webhook_stub
docker-compose up -d
```

The server will be available at `http://localhost:5000`

### Manual Docker Build

```bash
cd webhook_stub
docker build -t pixxio-webhook-stub .
docker run -p 5000:5000 -v webhook_data:/data/webhooks pixxio-webhook-stub
```

### Local Development

```bash
cd webhook_stub
pip install fastapi uvicorn jinja2
python app.py
```

Server runs on `http://localhost:5000`

## Configuration

Set environment variables to customize behavior:

```bash
export WEBHOOK_STORAGE_DIR=/custom/path/for/webhooks
python app.py
```

## PIXXIO Webhook Configuration

Configure PIXXIO to send webhooks to your server:

1. In PIXXIO admin settings, add a webhook
2. URL: `http://your-server:5000/webhook` (or your domain)
3. Method: `POST`
4. Events: Select events you want to monitor (uploads, metadata changes, etc.)
5. Start sending webhooks

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Dashboard with event list and download links |
| POST | `/webhook` | Receives webhook events from PIXXIO |
| GET | `/docs` | Interactive API documentation (Swagger UI) |
| GET | `/download/{filename}` | Download a webhook event JSON |
| POST | `/delete/{filename}` | Delete a specific event |
| POST | `/clear` | Delete all events |
| GET | `/health` | Health check endpoint |

## Example Webhook Payload

When PIXXIO sends a webhook, you'll see JSON like:

```json
{
  "event": "file.uploaded",
  "fileId": 123456,
  "fileName": "image.jpg",
  "timestamp": "2025-11-11T10:30:00Z",
  "...": "..."
}
```

## Storage

Webhook events are stored in `/data/webhooks` (inside container) or `webhook_data` volume.

Each event is saved as `webhook_YYYYMMDD_HHMMSS_mmm.json`

## Monitoring

View logs:
```bash
docker-compose logs -f webhook-stub
```

Check health:
```bash
curl http://localhost:5000/health
```

View API documentation:
```
http://localhost:5000/docs
```

## Security Notes

- ⚠️ This is a stub/development server—not for production
- No authentication required (add if using on public network)
- API keys in webhook payloads will be stored in plaintext
- Runs on `0.0.0.0:5000` (all interfaces)
- For production: Add reverse proxy, SSL, authentication, rate limiting

## Deployment on Netcup

Example setup on your Netcup server:

```bash
# SSH into your server
ssh user@netcup-server

# Clone or copy the webhook_stub folder
cd /opt/pixxio
git clone https://github.com/your-org/pixxio-client.git
cd pixxio-client/webhook_stub

# Start with Docker Compose
docker-compose up -d

# Configure PIXXIO to send webhooks to your domain
# URL: https://your-domain.com/webhook
# (Use reverse proxy for HTTPS)
```

For HTTPS/SSL on your Netcup server, use a reverse proxy like:
- Nginx
- Traefik
- Caddy

## Troubleshooting

**No events received?**
- Check firewall rules allow port 5000
- Verify PIXXIO webhook URL is correct
- Check logs: `docker-compose logs webhook-stub`

**Storage not persisting?**
- Ensure Docker volume is mounted: `docker volume ls`
- Check permissions on `/data/webhooks`

**Need to reset?**
```bash
docker-compose down -v  # Remove volume and container
docker-compose up -d    # Start fresh
```

## Tech Stack

- **Framework**: FastAPI 0.104+
- **Server**: Uvicorn
- **Templates**: Jinja2
- **Python**: 3.11+
- **Docker**: Supported

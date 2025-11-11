"""
Webhook Stub Server - receives and stores PIXXIO webhook events.
Serves a web interface for downloading stored JSON data.
"""
import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from jinja2 import Template
import uvicorn

app = FastAPI(
    title="PIXXIO Webhook Stub",
    description="Webhook receiver and analyzer for PIXXIO",
    version="1.0.0"
)

# Configuration
STORAGE_DIR = Path(os.environ.get("WEBHOOK_STORAGE_DIR", "/data/webhooks"))
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# HTML template for download page
TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PIXXIO Webhook Stub - Received Events</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            padding: 40px;
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
        }
        .status {
            background: #e8f5e9;
            color: #2e7d32;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 30px;
            border-left: 4px solid #4caf50;
        }
        .status-badge {
            display: inline-block;
            background: #4caf50;
            color: white;
            padding: 5px 10px;
            border-radius: 3px;
            font-weight: bold;
            margin-right: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background: #f5f5f5;
            font-weight: 600;
            color: #333;
        }
        tr:hover {
            background: #f9f9f9;
        }
        .download-btn {
            background: #667eea;
            color: white;
            padding: 8px 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            font-size: 14px;
        }
        .download-btn:hover {
            background: #5568d3;
        }
        .delete-btn {
            background: #f44336;
            color: white;
            padding: 8px 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        }
        .delete-btn:hover {
            background: #da190b;
        }
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #999;
        }
        .empty-state-icon {
            font-size: 48px;
            margin-bottom: 20px;
        }
        .clear-all {
            background: #ff9800;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 20px;
        }
        .clear-all:hover {
            background: #e68900;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🪝 PIXXIO Webhook Stub</h1>
        <div class="status">
            <span class="status-badge">● ONLINE</span>
            Endpoint: <code>POST /webhook</code> | 
            Storage: <code>{{ storage_location }}</code> | 
            Events received: <strong>{{ event_count }}</strong>
        </div>

        {% if events %}
            <table>
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>Event Type</th>
                        <th>Filename</th>
                        <th>Size</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for event in events %}
                    <tr>
                        <td>{{ event.timestamp }}</td>
                        <td><code>{{ event.event_type }}</code></td>
                        <td>{{ event.filename }}</td>
                        <td>{{ event.size }} KB</td>
                        <td>
                            <a href="/download/{{ event.filename }}" class="download-btn">Download</a>
                            <button class="delete-btn" onclick="deleteEvent('{{ event.filename }}')">Delete</button>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            <button class="clear-all" onclick="clearAll()">Clear All Events</button>
        {% else %}
            <div class="empty-state">
                <div class="empty-state-icon">📭</div>
                <p>No webhook events received yet.</p>
                <p style="font-size: 14px; margin-top: 10px;">Configure PIXXIO to send webhooks to:</p>
                <code>{{ webhook_url }}/webhook</code>
            </div>
        {% endif %}
    </div>
    <script>
        function deleteEvent(filename) {
            if (confirm(`Delete event "${filename}"?`)) {
                fetch(`/delete/${filename}`, { method: 'POST' })
                    .then(r => r.json())
                    .then(d => { if (d.success) location.reload(); })
                    .catch(e => alert('Error: ' + e));
            }
        }
        function clearAll() {
            if (confirm('Delete ALL events?')) {
                fetch('/clear', { method: 'POST' })
                    .then(r => r.json())
                    .then(d => { if (d.success) location.reload(); })
                    .catch(e => alert('Error: ' + e));
            }
        }
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> str:
    """Serve the webhook events dashboard."""
    events = []
    try:
        for file in sorted(STORAGE_DIR.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True):
            size = file.stat().st_size / 1024  # Convert to KB
            try:
                with open(file, "r") as f:
                    data = json.load(f)
                event_type = data.get("event", "unknown")
            except:
                event_type = "invalid"
            
            events.append({
                "filename": file.name,
                "timestamp": datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "event_type": event_type,
                "size": f"{size:.2f}"
            })
    except Exception as e:
        logger.error(f"Error reading events: {e}")
    
    webhook_url = str(request.url).split("?")[0].rstrip("/")
    template = Template(TEMPLATE)
    return template.render(
        events=events,
        event_count=len(events),
        storage_location=str(STORAGE_DIR),
        webhook_url=webhook_url
    )


@app.post("/webhook")
async def webhook(request: Request) -> Dict[str, Any]:
    """Receive and store webhook events from PIXXIO."""
    try:
        data = await request.json()
        if not data:
            logger.warning("Received empty webhook payload")
            raise HTTPException(status_code=400, detail="No JSON data")
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"webhook_{timestamp}.json"
        filepath = STORAGE_DIR / filename
        
        # Store the JSON data
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Stored webhook event: {filename} | Event: {data.get('event', 'unknown')}")
        return {
            "success": True,
            "message": f"Webhook received and stored as {filename}",
            "filename": filename
        }
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download/{filename}")
async def download(filename: str) -> FileResponse:
    """Download a stored webhook event."""
    try:
        # Prevent directory traversal attacks
        if ".." in filename or "/" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        filepath = STORAGE_DIR / filename
        if not filepath.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        logger.info(f"Downloaded webhook event: {filename}")
        return FileResponse(
            filepath,
            filename=filename,
            media_type="application/json"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/delete/{filename}")
async def delete(filename: str) -> Dict[str, Any]:
    """Delete a stored webhook event."""
    try:
        if ".." in filename or "/" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        filepath = STORAGE_DIR / filename
        if not filepath.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        filepath.unlink()
        logger.info(f"Deleted webhook event: {filename}")
        return {"success": True, "message": f"Deleted {filename}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/clear")
async def clear_all() -> Dict[str, Any]:
    """Delete all stored webhook events."""
    try:
        count = 0
        for file in STORAGE_DIR.glob("*.json"):
            file.unlink()
            count += 1
        logger.info(f"Cleared all webhook events ({count} files deleted)")
        return {"success": True, "message": f"Deleted {count} events"}
    except Exception as e:
        logger.error(f"Error clearing events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health() -> Dict[str, Any]:
    """Health check endpoint."""
    return {"status": "ok", "storage_dir": str(STORAGE_DIR)}


if __name__ == "__main__":
    logger.info(f"Starting PIXXIO Webhook Stub on 0.0.0.0:5000")
    logger.info(f"Storage directory: {STORAGE_DIR}")
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")

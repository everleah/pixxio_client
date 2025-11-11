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
        .show-btn {
            background: #2196F3;
            color: white;
            padding: 8px 12px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin-right: 3px;
            min-width: 36px;
            height: 36px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            transition: background 0.2s;
        }
        .show-btn:hover {
            background: #0b7dda;
        }
        .download-btn {
            background: #667eea;
            color: white;
            padding: 8px 12px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            margin-right: 3px;
            min-width: 36px;
            height: 36px;
            transition: background 0.2s;
        }
        .download-btn:hover {
            background: #5568d3;
        }
        .delete-btn {
            background: #f44336;
            color: white;
            padding: 8px 12px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            min-width: 36px;
            height: 36px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            transition: background 0.2s;
        }
        .delete-btn:hover {
            background: #da190b;
        }
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
        }
        .modal-content {
            background-color: #fefefe;
            margin: 5% auto;
            padding: 20px;
            border-radius: 8px;
            max-width: 90%;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            border-bottom: 1px solid #ddd;
            padding-bottom: 10px;
        }
        .modal-header h2 {
            margin: 0;
            color: #333;
        }
        .modal-close {
            font-size: 28px;
            font-weight: bold;
            color: #aaa;
            cursor: pointer;
            background: none;
            border: none;
            padding: 0;
            line-height: 1;
        }
        .modal-close:hover {
            color: #000;
        }
        .json-viewer {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            white-space: pre-wrap;
            word-wrap: break-word;
            max-height: 60vh;
            overflow-y: auto;
            border: 1px solid #ddd;
        }
        .json-viewer code {
            color: #333;
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
                        <th>Events</th>
                        <th>Size</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for event in events %}
                    <tr>
                        <td>{{ event.timestamp }}</td>
                        <td><code style="font-size: 11px;">{{ event.event_type }}</code></td>
                        <td><span style="background: #e3f2fd; padding: 2px 8px; border-radius: 3px; font-weight: 500;">{{ event.event_count }}</span></td>
                        <td>{{ event.size }} KB</td>
                        <td>
                            <button class="show-btn" onclick="showJSON('{{ event.filename }}')" title="Show JSON">👁️</button>
                            <a href="/download/{{ event.filename }}" class="download-btn" title="Download JSON">⬇️</a>
                            <button class="delete-btn" onclick="deleteEvent('{{ event.filename }}')" title="Delete event">🗑️</button>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            <button class="clear-all" onclick="clearAll()" title="Delete all events">🗑️ Clear All Events</button>
        {% else %}
            <div class="empty-state">
                <div class="empty-state-icon">📭</div>
                <p>No webhook events received yet.</p>
                <p style="font-size: 14px; margin-top: 10px;">Configure PIXXIO to send webhooks to:</p>
                <code>{{ webhook_url }}/webhook</code>
            </div>
        {% endif %}
    </div>

    <!-- JSON Viewer Modal -->
    <div id="jsonModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>Webhook Payload</h2>
                <button class="modal-close" onclick="closeJSON()">&times;</button>
            </div>
            <div class="json-viewer" id="jsonContent"><code></code></div>
        </div>
    </div>

    <script>
        function showJSON(filename) {
            fetch(`/download/${filename}`)
                .then(r => r.text())
                .then(json => {
                    try {
                        // Parse and pretty print JSON
                        const data = JSON.parse(json);
                        const formatted = JSON.stringify(data, null, 2);
                        
                        // Show in modal with syntax highlighting info
                        const modal = document.getElementById('jsonModal');
                        const contentDiv = document.getElementById('jsonContent');
                        contentDiv.innerHTML = '';
                        
                        // Add filename header
                        const fileInfo = document.createElement('div');
                        fileInfo.style.cssText = 'margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid #ddd; font-size: 11px; color: #666;';
                        fileInfo.textContent = `File: ${filename}`;
                        contentDiv.appendChild(fileInfo);
                        
                        // Add JSON code
                        const code = document.createElement('code');
                        code.textContent = formatted;
                        code.style.display = 'block';
                        contentDiv.appendChild(code);
                        
                        modal.style.display = 'block';
                    } catch (e) {
                        alert('Error parsing JSON: ' + e);
                    }
                })
                .catch(e => alert('Error loading JSON: ' + e));
        }

        function closeJSON() {
            document.getElementById('jsonModal').style.display = 'none';
        }

        // Close modal when clicking outside it
        window.onclick = function(event) {
            const modal = document.getElementById('jsonModal');
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        }

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
                
                # Extract event type from PIXXIO webhook structure
                event_type = "unknown"
                event_count_in_file = 0
                
                if isinstance(data, dict) and "events" in data:
                    events_list = data.get("events", [])
                    event_count_in_file = len(events_list)
                    if events_list and len(events_list) > 0:
                        first_event = events_list[0]
                        event_key = first_event.get("eventKey", "unknown")
                        action = first_event.get("action", "")
                        
                        # Format event type nicely
                        if action:
                            event_type = f"{action.capitalize()} - {event_key}"
                        else:
                            event_type = event_key
                else:
                    # Fallback for old format
                    event_type = data.get("event", "unknown")
            except Exception as e:
                logger.error(f"Error parsing event {file.name}: {e}")
                event_type = "parse-error"
            
            events.append({
                "filename": file.name,
                "timestamp": datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "event_type": event_type,
                "size": f"{size:.2f}",
                "event_count": event_count_in_file
            })
    except Exception as e:
        logger.error(f"Error reading events: {e}")
    
    webhook_url = str(request.url).split("?")[0].rstrip("/")
    try:
        template = Template(TEMPLATE)
        html = template.render(
            events=events,
            event_count=len(events),
            storage_location=str(STORAGE_DIR),
            webhook_url=webhook_url
        )
        logger.info(f"Rendered HTML: {len(html)} bytes, events: {len(events)}")
        return html
    except Exception as e:
        logger.error(f"Template render error: {e}")
        raise HTTPException(status_code=500, detail=f"Template error: {str(e)}")


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


@app.get("/test", response_class=HTMLResponse)
async def test() -> str:
    """Simple test endpoint to verify app is running."""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Test</title></head>
    <body>
        <h1>✅ FastAPI Webhook Stub is Running</h1>
        <p><a href="/">Go to Dashboard</a></p>
    </body>
    </html>
    """


if __name__ == "__main__":
    logger.info(f"Starting PIXXIO Webhook Stub on 0.0.0.0:5000")
    logger.info(f"Storage directory: {STORAGE_DIR}")
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")

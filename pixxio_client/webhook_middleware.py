"""
PIXXIO Webhook Middleware Examples

This module provides ready-to-use middleware and decorators for integrating
PIXXIO webhook parsing into your application. Examples for FastAPI, Flask,
and Django are included.

Each example shows:
1. How to receive and validate webhooks
2. How to parse them into WebhookEvent objects
3. How to dispatch events to handlers
4. How to respond correctly to PIXXIO

Usage:
    See the specific framework section you're using (FastAPI, Flask, Django).
"""

from typing import Callable, Dict, List, Optional, Any, TYPE_CHECKING
from functools import wraps
import logging

if TYPE_CHECKING:
    from pixxio_client.webhook_parser import WebhookEvent

logger = logging.getLogger(__name__)


class WebhookEventHandler:
    """
    Base class for handling webhook events.
    
    Subclass this and implement handle() to process events.
    """
    
    def handle(self, event: 'WebhookEvent') -> bool:
        """
        Handle a webhook event.
        
        Args:
            event: WebhookEvent to process
        
        Returns:
            True if handled successfully, False otherwise
        """
        raise NotImplementedError
    
    def can_handle(self, event: 'WebhookEvent') -> bool:
        """
        Check if this handler can process the event.
        
        Args:
            event: WebhookEvent to check
        
        Returns:
            True if this handler can handle the event
        """
        return True


class WebhookDispatcher:
    """
    Dispatches webhook events to registered handlers.
    
    Example:
        dispatcher = WebhookDispatcher()
        dispatcher.register(FileUploadHandler())
        dispatcher.register(MetadataChangeHandler())
        
        events = parse_pixxio_webhook(request.json())
        dispatcher.dispatch_all(events)
    """
    
    def __init__(self):
        """Initialize the dispatcher."""
        self.handlers: List[WebhookEventHandler] = []
    
    def register(self, handler: WebhookEventHandler) -> None:
        """Register a webhook event handler."""
        self.handlers.append(handler)
        logger.info(f"Registered handler: {handler.__class__.__name__}")
    
    def dispatch(self, event: 'WebhookEvent') -> bool:
        """
        Dispatch an event to the first handler that can handle it.
        
        Args:
            event: WebhookEvent to dispatch
        
        Returns:
            True if event was handled
        """
        for handler in self.handlers:
            if handler.can_handle(event):
                try:
                    if handler.handle(event):
                        logger.info(f"Event {event.event_id} handled by {handler.__class__.__name__}")
                        return True
                except Exception as e:
                    logger.error(f"Error in handler {handler.__class__.__name__}: {e}")
        
        return False
    
    def dispatch_all(self, events: List['WebhookEvent']) -> Dict[str, int]:
        """
        Dispatch all events to handlers.
        
        Args:
            events: List of WebhookEvent objects
        
        Returns:
            Dict with stats: {"total": int, "handled": int, "failed": int}
        """
        stats = {"total": len(events), "handled": 0, "failed": 0}
        
        for event in events:
            try:
                if self.dispatch(event):
                    stats["handled"] += 1
                else:
                    stats["failed"] += 1
            except Exception as e:
                logger.error(f"Failed to dispatch event {event.event_id}: {e}")
                stats["failed"] += 1
        
        logger.info(f"Dispatch stats: {stats}")
        return stats


# ============================================================================
# FastAPI Example
# ============================================================================

"""
FastAPI Webhook Integration Example

This example shows how to use the PIXXIO webhook parser with FastAPI.

Installation:
    pip install fastapi uvicorn

Example code:

    from fastapi import FastAPI, Request, HTTPException
    from pixxio_client import WebhookParser, WebhookEvent
    from pixxio_client.webhook_middleware import WebhookEventHandler, WebhookDispatcher
    
    app = FastAPI()
    parser = WebhookParser()
    dispatcher = WebhookDispatcher()
    
    class FileUploadHandler(WebhookEventHandler):
        def can_handle(self, event: WebhookEvent) -> bool:
            return event.is_file_event() and event.event_key == "fileUploaded"
        
        def handle(self, event: WebhookEvent) -> bool:
            print(f"File uploaded: {event.resource_id}")
            # Process file upload...
            return True
    
    dispatcher.register(FileUploadHandler())
    
    @app.post("/webhook")
    async def webhook(request: Request):
        # Get signature for verification (optional)
        signature = request.headers.get("x-hub-signature-256")
        
        # Parse webhook
        body = await request.body()
        try:
            events = parser.parse_webhook(body)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid webhook: {str(e)}")
        
        # Dispatch to handlers
        stats = dispatcher.dispatch_all(events)
        
        # Return success response
        return {
            "success": True,
            "processed": stats["handled"],
            "failed": stats["failed"]
        }
"""


# ============================================================================
# Flask Example
# ============================================================================

"""
Flask Webhook Integration Example

This example shows how to use the PIXXIO webhook parser with Flask.

Installation:
    pip install flask

Example code:

    from flask import Flask, request, jsonify
    from pixxio_client import WebhookParser, WebhookEvent
    from pixxio_client.webhook_middleware import WebhookEventHandler, WebhookDispatcher
    
    app = Flask(__name__)
    parser = WebhookParser()
    dispatcher = WebhookDispatcher()
    
    class MetadataChangeHandler(WebhookEventHandler):
        def can_handle(self, event: WebhookEvent) -> bool:
            return event.is_metadata_event()
        
        def handle(self, event: WebhookEvent) -> bool:
            field_name = event.get_changed_field_name()
            print(f"Metadata changed: {field_name}")
            # Process metadata change...
            return True
    
    dispatcher.register(MetadataChangeHandler())
    
    @app.route("/webhook", methods=["POST"])
    def webhook():
        try:
            events = parser.parse_webhook(request.json)
        except ValueError as e:
            return jsonify({"error": f"Invalid webhook: {str(e)}"}), 400
        
        stats = dispatcher.dispatch_all(events)
        
        return jsonify({
            "success": True,
            "processed": stats["handled"],
            "failed": stats["failed"]
        })
"""


# ============================================================================
# Django Example
# ============================================================================

"""
Django Webhook Integration Example

This example shows how to use the PIXXIO webhook parser with Django.

Installation:
    pip install django djangorestframework

urls.py:
    from django.urls import path
    from . import views
    
    urlpatterns = [
        path("webhook/", views.webhook, name="pixxio_webhook"),
    ]

views.py:

    from django.http import JsonResponse
    from django.views.decorators.http import require_http_methods
    from django.views.decorators.csrf import csrf_exempt
    from pixxio_client import WebhookParser, WebhookEvent
    from pixxio_client.webhook_middleware import WebhookEventHandler, WebhookDispatcher
    import json
    
    parser = WebhookParser()
    dispatcher = WebhookDispatcher()
    
    class AuditLogHandler(WebhookEventHandler):
        def can_handle(self, event: WebhookEvent) -> bool:
            return True  # Handle all events
        
        def handle(self, event: WebhookEvent) -> bool:
            # Log to database
            print(f"User {event.user_name} performed {event.action} on {event.resource_type}")
            return True
    
    dispatcher.register(AuditLogHandler())
    
    @csrf_exempt
    @require_http_methods(["POST"])
    def webhook(request):
        try:
            data = json.loads(request.body)
            events = parser.parse_webhook(data)
        except (ValueError, json.JSONDecodeError) as e:
            return JsonResponse({"error": f"Invalid webhook: {str(e)}"}, status=400)
        
        stats = dispatcher.dispatch_all(events)
        
        return JsonResponse({
            "success": True,
            "processed": stats["handled"],
            "failed": stats["failed"]
        })
"""


# ============================================================================
# Decorator for Handler Registration
# ============================================================================

def webhook_handler(event_filter: Optional[Callable] = None):
    """
    Decorator to register a function as a webhook event handler.
    
    Args:
        event_filter: Optional function to filter events. Should take WebhookEvent
                     and return True if the function should handle it.
    
    Example:
        @webhook_handler(lambda e: e.is_file_event() and e.action == "created")
        def on_file_created(event):
            print(f"File created: {event.resource_id}")
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(event: 'WebhookEvent') -> bool:
            try:
                if event_filter is None or event_filter(event):
                    result = func(event)
                    return result if isinstance(result, bool) else True
                return False
            except Exception as e:
                logger.error(f"Error in webhook handler {func.__name__}: {e}")
                return False
        
        return wrapper
    
    return decorator


# ============================================================================
# Standard Response Format
# ============================================================================

class WebhookResponse:
    """
    Standard response format for webhook endpoints.
    
    Usage:
        response = WebhookResponse()
        response.add_event(event_id, "processed", "File uploaded successfully")
        return response.to_json()
    """
    
    def __init__(self, success: bool = True):
        """Initialize response."""
        self.success = success
        self.events_processed: List[Dict[str, Any]] = []
        self.errors: List[str] = []
    
    def add_event(self, event_id: int, status: str, message: str = "") -> None:
        """Add an event processing result."""
        self.events_processed.append({
            "id": event_id,
            "status": status,
            "message": message
        })
    
    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)
        self.success = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "processed": len(self.events_processed),
            "errors": len(self.errors),
            "events": self.events_processed,
            "error_messages": self.errors if self.errors else None,
        }
    
    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return self.to_dict()

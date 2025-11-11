FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir fastapi==0.104.1 uvicorn==0.24.0 jinja2==3.1.2 requests

# Copy application
COPY app.py .

# Create data directory
RUN mkdir -p /data/webhooks

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

# Run application
CMD ["python", "app.py"]

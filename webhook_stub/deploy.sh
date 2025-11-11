#!/bin/bash
# Build and deploy webhook stub to Netcup server

set -e

NETCUP_HOST=${NETCUP_HOST:-"user@netcup-server"}
REMOTE_PATH=${REMOTE_PATH:-"/opt/pixxio/webhook_stub"}

echo "📦 Building Docker image..."
docker build -t pixxio-webhook-stub:latest .

echo "📤 Copying to Netcup server..."
rsync -avz \
    --exclude '__pycache__' \
    --exclude '.git' \
    --exclude 'webhook_data' \
    ./ "$NETCUP_HOST:$REMOTE_PATH/"

echo "🚀 Starting on Netcup server..."
ssh "$NETCUP_HOST" << 'EOF'
    cd /opt/pixxio/webhook_stub
    docker-compose down || true
    docker-compose pull || true
    docker-compose up -d
    docker-compose logs -f
EOF

echo "✅ Deployment complete!"
echo "📊 Dashboard: http://netcup-server:5000"

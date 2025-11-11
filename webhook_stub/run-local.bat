@echo off
REM Build and run webhook stub locally on Windows

echo Building Docker image...
docker build -t pixxio-webhook-stub:latest .

echo.
echo Starting webhook stub container...
docker run ^
    --name pixxio-webhook-stub ^
    -p 5000:5000 ^
    -v webhook_data:/data/webhooks ^
    pixxio-webhook-stub:latest

pause

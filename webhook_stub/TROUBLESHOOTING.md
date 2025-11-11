# Webhook Stub - Troubleshooting Guide

## Health Check Failures

### ❌ "ModuleNotFoundError: No module named 'requests'"

**Symptom**: Container marked as unhealthy, logs show requests import error

**Root Cause**: Dockerfile missing `requests` package

**Fix**:
```bash
# Rebuild image with all dependencies
docker-compose build --no-cache
docker-compose up -d

# Wait ~30 seconds for health check to pass
docker-compose ps  # Status should show "healthy" after a minute
```

---

## Connectivity Issues

### ❌ "Could not resolve host: pixxiostub.claudiapps.de"

**Symptom**: DNS resolution fails

**Check**:
```bash
nslookup pixxiostub.claudiapps.de
ping pixxiostub.claudiapps.de
```

**Fix**:
1. Verify DNS record exists in your registrar
2. Wait for DNS propagation (up to 24 hours)
3. Test with IP directly: `curl https://[server-ip]/health`

---

### ❌ "Connection refused" or "No route to host"

**Symptom**: Can't reach webhook stub endpoint

**Check container status**:
```bash
docker-compose ps
docker inspect pixxio-webhook-stub
docker-compose logs webhook-stub
```

**Check Traefik routing**:
```bash
docker logs traefik | grep webhook
docker exec traefik traefik config show
```

**Fix**:
1. Restart container: `docker-compose restart`
2. Verify Traefik is running: `docker ps | grep traefik`
3. Check network: `docker network inspect claudiapp-net`

---

### ❌ "SSL certificate error" or "CERTIFICATE_VERIFY_FAILED"

**Symptom**: HTTPS connection fails with cert error

**Check certificate**:
```bash
curl -v https://pixxiostub.claudiapps.de/health
openssl s_client -connect pixxiostub.claudiapps.de:443
```

**Fix**:
1. Wait for Let's Encrypt to issue cert (usually < 1 minute)
2. Check Traefik logs: `docker logs traefik | grep letsencrypt`
3. Verify domain/DNS is resolvable
4. Restart Traefik if needed

---

## No Webhooks Received

### ❌ Dashboard empty, no events appearing

**Symptom**: Configure PIXXIO to send webhooks, but nothing appears

**Check endpoint accessibility**:
```bash
# Test from PIXXIO server or externally
curl -X POST https://pixxiostub.claudiapps.de/webhook \
  -H "Content-Type: application/json" \
  -d '{"event":"test","timestamp":"2025-11-11T12:00:00Z"}'

# Check if event was stored
docker exec pixxio-webhook-stub ls /data/webhooks/
```

**Diagnose PIXXIO configuration**:
1. Verify webhook URL in PIXXIO: `https://pixxiostub.claudiapps.de/webhook`
2. Check webhook is enabled in PIXXIO
3. Try sending a test webhook from PIXXIO admin
4. View webhook stub logs: `docker-compose logs webhook-stub`

**Fix**:
1. Correct webhook URL if wrong
2. Verify network connectivity between PIXXIO and your server
3. Check firewall/security group allows HTTPS outbound from PIXXIO
4. Test manually: `curl -X POST https://pixxiostub.claudiapps.de/webhook ...`

---

## Storage Issues

### ❌ Events disappear after container restart

**Symptom**: Webhook events stored, but gone after `docker-compose restart`

**Check volume**:
```bash
docker volume ls | grep webhook
docker volume inspect webhook_stub_webhook_data
docker exec pixxio-webhook-stub ls -la /data/webhooks/
```

**Fix**:
```bash
# Ensure volume is mounted correctly
docker-compose down -v  # This DELETES the volume!

# Don't do above unless you want to lose data!
# Instead, just restart:
docker-compose restart

# Verify events still there
docker exec pixxio-webhook-stub ls /data/webhooks/
```

---

### ❌ "No space left on device" when storing webhooks

**Symptom**: Error when receiving large webhook payloads

**Check disk space**:
```bash
df -h
docker system df
```

**Fix**:
1. Clean up old webhooks: Access dashboard and click "Clear All Events"
2. Backup old webhooks first: See DEPLOYMENT.md
3. Free up server disk space
4. If volume corrupted: `docker volume prune`

---

### ❌ Can't access stored webhook files

**Symptom**: `docker exec` fails or permission denied

**Check permissions**:
```bash
docker exec pixxio-webhook-stub ls -la /data/webhooks/
docker exec pixxio-webhook-stub stat /data/webhooks/
```

**Fix**:
```bash
# Fix permissions inside container
docker exec pixxio-webhook-stub chmod 755 /data/webhooks

# Or rebuild image if Dockerfile has permission issues
docker-compose build --no-cache
```

---

## Container Issues

### ❌ Container crashes immediately

**Symptom**: Container exits with error code

**Check logs**:
```bash
docker-compose logs webhook-stub
docker-compose up  # Run in foreground to see startup errors
```

**Common causes**:
- Port already in use (shouldn't affect since no port exposed)
- Missing volume mount
- Bad environment variable
- Python syntax error in app.py

**Fix**:
1. Review error message in logs
2. Rebuild: `docker-compose build --no-cache`
3. Check for recent changes to app.py or requirements
4. Test locally first: `python webhook_stub/app.py`

---

### ❌ Container stuck in "unhealthy" state

**Symptom**: `docker-compose ps` shows `unhealthy`

**Check health**:
```bash
docker inspect pixxio-webhook-stub | grep -A 20 '"Health"'
docker exec pixxio-webhook-stub curl http://localhost:5000/health
```

**Common causes**:
- Requests module missing → rebuild with `docker-compose build --no-cache`
- App crashed → check logs: `docker-compose logs webhook-stub`
- Port 5000 not responding → check if app is running

**Fix**:
```bash
# Force rebuild
docker-compose build --no-cache

# Restart
docker-compose down
docker-compose up -d

# Wait 30-60 seconds for health check to pass
sleep 60
docker-compose ps
```

---

### ❌ "Cannot find docker network claudiapp-net"

**Symptom**: Error when starting container: network not found

**Check networks**:
```bash
docker network ls | grep claudiapp
```

**Fix**:
1. Create network if missing: `docker network create claudiapp-net`
2. Or update `docker-compose.yml` to use internal network instead
3. Ensure Traefik is running on same network: `docker inspect traefik | grep claudiapp`

---

## Performance Issues

### ❌ Slow dashboard loading or timeout

**Symptom**: Dashboard takes > 5 seconds to load or times out

**Causes**: Too many webhook files, slow disk I/O

**Fix**:
1. Clear old events: Dashboard → "Clear All Events"
2. Or manually: `docker exec pixxio-webhook-stub rm /data/webhooks/*.json`
3. Check disk health: `docker system df`
4. Check container resource limits: `docker stats pixxio-webhook-stub`

---

## Traefik Integration Issues

### ❌ Webhook stub not appearing in Traefik dashboard

**Symptom**: Other containers show in Traefik but not webhook stub

**Check Traefik labels**:
```bash
docker inspect pixxio-webhook-stub | grep -A 20 "Labels"
```

**Verify labels match**:
- `traefik.enable=true`
- `traefik.http.routers.webhook-stub.rule=Host(...)`
- `traefik.http.services.webhook-stub.loadbalancer.server.port=5000`

**Fix**:
1. Update docker-compose.yml labels if missing
2. Rebuild and restart: `docker-compose build && docker-compose up -d`
3. Check Traefik logs: `docker logs traefik`

---

## Network Debugging

### ❌ Can't communicate between Traefik and webhook stub

**Symptom**: Traefik routes request but container doesn't respond

**Test from Traefik**:
```bash
docker exec traefik curl http://webhook-stub:5000/health
# Should return 200 OK with health check JSON
```

**Fix**:
1. Verify both containers are on `claudiapp-net`: `docker network inspect claudiapp-net`
2. Check firewall rules between containers
3. Verify port 5000 is exposed in Dockerfile

---

## Reset / Clean Start

### Complete reset (WARNING: Deletes all webhooks!)

```bash
# Stop container
docker-compose down

# Delete volume (webhooks will be lost)
docker volume rm webhook_stub_webhook_data

# Rebuild image
docker-compose build --no-cache

# Restart fresh
docker-compose up -d

# Wait for health check
sleep 60
docker-compose ps
```

---

## Get Help

### Collect diagnostic info

```bash
echo "=== Container Status ==="
docker-compose ps

echo "=== Health Status ==="
docker inspect pixxio-webhook-stub | grep -A 20 '"Health"'

echo "=== Recent Logs ==="
docker-compose logs --tail=50 webhook-stub

echo "=== Network ==="
docker network inspect claudiapp-net

echo "=== Storage ==="
docker exec pixxio-webhook-stub ls -lah /data/webhooks/ | head -10
```

### Manual health check

```bash
# From within container
docker exec pixxio-webhook-stub curl -v http://localhost:5000/health

# From host (if accessible)
curl -v https://pixxiostub.claudiapps.de/health
```

---

## Still Having Issues?

1. Check DEPLOYMENT.md for detailed deployment guide
2. Review SETUP.md for configuration details
3. Check logs: `docker-compose logs -f`
4. Verify environment: `docker inspect pixxio-webhook-stub`
5. Test manually with curl before integrating with PIXXIO

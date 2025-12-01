# Airflow Webserver Fix for macOS

## Problem
When running `airflow webserver --port 8080` on macOS, you may encounter:
```
[ERROR] Worker (pid:XXXX) was sent SIGSEGV!
```

This is caused by compatibility issues between Gunicorn's `sync` worker and macOS's `fork()` behavior.

## Solution

Use the standalone webserver mode instead:

```bash
# Stop any running Airflow processes
pkill -f airflow

# Set environment
export AIRFLOW_HOME=$(pwd)

# Start webserver in standalone mode (no Gunicorn workers)
airflow webserver --port 8080 --workers 1 --worker-timeout 120
```

## Alternative Solutions

### Option 1: Use Standalone Development Server
```bash
export AIRFLOW__WEBSERVER__WORKER_CLASS=sync
export AIRFLOW__WEBSERVER__WORKERS=1
airflow webserver --port 8080
```

### Option 2: Modify airflow.cfg
Edit `airflow.cfg` and change:
```ini
[webserver]
worker_class = sync
workers = 1
```

### Option 3: Use Docker Instead (Recommended for Production)
```bash
# Use Docker Compose
docker-compose up -d
```

## Quick Fix Command

```bash
# Kill all airflow processes
pkill -f airflow

# Start with single worker
export AIRFLOW_HOME=$(pwd)
airflow webserver --port 8080 --workers 1
```

## Verification

After starting, check:
```bash
# Check if webserver is running
ps aux | grep "airflow webserver"

# Check port
lsof -i :8080

# Access UI
open http://localhost:8080
```

## Common macOS-Specific Issues

1. **SIGSEGV Errors**: Use `--workers 1`
2. **Port Already in Use**: Kill existing process or use different port
3. **Database Locked**: Check SQLite file permissions

## Production Recommendation

For production or serious development on macOS, use Docker:

```bash
# See docker-compose.yml for full setup
docker-compose up airflow-webserver airflow-scheduler
```

This avoids all macOS-specific fork issues.

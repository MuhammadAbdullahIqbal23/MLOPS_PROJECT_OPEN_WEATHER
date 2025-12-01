# Quick Start Guide - MLOps Weather Pipeline

This guide will get your complete MLOps pipeline running in under 10 minutes.

## Prerequisites

- Python 3.8+
- Docker Desktop
- Git
- OpenWeatherMap API key (free tier)

## Step 1: Clone and Setup (2 minutes)

```bash
# Navigate to project
cd /Users/abdurrehmansubhani/Desktop/Abdullah/MLOps-Project

# Install dependencies
pip install -r requirements.txt

# Create environment file
cat > .env << 'EOF'
OPENWEATHER_API_KEY=your_api_key_here
OPENWEATHER_CITIES=London,Paris,Tokyo,NewYork,Sydney
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=mlops-data
EOF

# Replace with your actual API key
nano .env  # or use any editor
```

## Step 2: Start MinIO (1 minute)

```bash
docker run -d \
  --name minio \
  -p 9000:9000 \
  -p 9001:9001 \
  -e "MINIO_ROOT_USER=minioadmin" \
  -e "MINIO_ROOT_PASSWORD=minioadmin" \
  quay.io/minio/minio server /data --console-address ":9001"

# Verify it's running
docker ps | grep minio
```

Access MinIO: http://localhost:9001 (minioadmin/minioadmin)

## Step 3: Initialize DVC (1 minute)

```bash
# Initialize DVC
dvc init

# Configure MinIO as remote
dvc remote add -d minio s3://mlops-data/dvc-storage
dvc remote modify minio endpointurl http://localhost:9000
dvc remote modify minio access_key_id minioadmin
dvc remote modify minio secret_access_key minioadmin
```

## Step 4: Setup Airflow (3 minutes)

```bash
# Set Airflow home
export AIRFLOW_HOME=$(pwd)

# Create required directories
mkdir -p data/raw data/processed reports logs

# Initialize Airflow database
airflow db init

# Create admin user
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin
```

## Step 5: Start Airflow (1 minute)

Open **two separate terminals**:

### Terminal 1: Webserver
```bash
cd /Users/abdurrehmansubhani/Desktop/Abdullah/MLOps-Project
export AIRFLOW_HOME=$(pwd)
# macOS: Use single worker to avoid crashes
airflow webserver --port 8080 --workers 1
```

### Terminal 2: Scheduler
```bash
cd /Users/abdurrehmansubhani/Desktop/Abdullah/MLOps-Project
export AIRFLOW_HOME=$(pwd)
airflow scheduler
```

**Note for macOS Users**: If you see `Worker (pid:XXXX) was sent SIGSEGV!` errors, the `--workers 1` flag fixes this. See [`AIRFLOW_MACOS_FIX.md`](AIRFLOW_MACOS_FIX.md) for details.

Access Airflow: http://localhost:8080 (admin/admin)

## Step 6: Run the Pipeline (2 minutes)

1. **Open Airflow UI**: http://localhost:8080
2. **Login**: admin/admin
3. **Find DAG**: `weather_prediction_pipeline`
4. **Enable**: Toggle the switch to ON
5. **Trigger**: Click the "Play" button ▶️
6. **Monitor**: Watch the tasks turn green!

## Verify Everything Works

### Check 1: Data Extraction
```bash
ls -lh data/raw/
# Should see: weather_data_YYYYMMDD_HHMMSS.csv
```

### Check 2: Data Processing
```bash
ls -lh data/processed/
# Should see: weather_data_*_processed.csv and .dvc files
```

### Check 3: MinIO Storage
Visit http://localhost:9001
- Navigate to `mlops-data` bucket
- Check `processed_data/` folder
- Check `dvc-storage/` folder

### Check 4: Reports
```bash
open reports/weather_data_*_profile.html
# Opens Pandas profiling report in browser
```

### Check 5: DVC Status
```bash
dvc status
# Should show: Data and pipelines are up to date.
```

## What Just Happened?

Your pipeline automatically:

1. ✅ **Extracted** live weather data from OpenWeatherMap API
2. ✅ **Validated** data quality (null checks, schema validation)
3. ✅ **Generated** comprehensive data profiling report
4. ✅ **Transformed** data with time-series feature engineering:
   - Lag features (1h, 3h, 6h)
   - Rolling means (3h, 6h, 12h)
   - Time-based features (hour, day, month)
5. ✅ **Stored** processed data in MinIO (S3-compatible storage)
6. ✅ **Versioned** data using DVC
7. ✅ **Logged** everything to MLflow (artifacts and metrics)

## Next Steps

### View the DAG Structure
```bash
# Open VS Code
code dags/weather_pipeline_dag.py
```

### Manually Trigger Again
```bash
airflow dags trigger weather_prediction_pipeline
```

### Check Logs
```bash
# In Airflow UI, click any task → View Log
# Or via CLI:
airflow tasks test weather_prediction_pipeline extract_data 2025-12-01
```

### Test Quality Gate Failure
```bash
# Create bad data
python -c "
import pandas as pd
import numpy as np
data = {'temp': [np.nan]*60 + list(range(40))}
pd.DataFrame(data).to_csv('data/raw/bad.csv', index=False)
"

# Test quality check
python -c "
from src.data_quality import validate_data_quality
validate_data_quality('data/raw/bad.csv', ['temp'])
"
# Should FAIL with: "✗ Null value check: FAILED (60.0% > 1.0%)"
```

### View MLflow Experiments (Optional)
```bash
# Start MLflow UI in new terminal
mlflow ui --port 5000

# Open in browser
open http://localhost:5000
```

## Troubleshooting

### DAG not appearing?
```bash
# Check for import errors
airflow dags list-import-errors

# Check DAG syntax
python dags/weather_pipeline_dag.py
```

### MinIO connection issues?
```bash
# Test connection
python -c "from src.storage_versioning import MinIOStorage; MinIOStorage()"
```

### Import errors in tasks?
```bash
# Add project to Python path
export PYTHONPATH=$(pwd):$PYTHONPATH
```

### Webserver won't start?
```bash
# Kill existing processes
pkill -f airflow

# Check if port is in use
lsof -i :8080

# Restart with single worker (macOS fix)
airflow webserver --port 8080 --workers 1
```

**macOS SIGSEGV Errors**: See [`AIRFLOW_MACOS_FIX.md`](AIRFLOW_MACOS_FIX.md) for detailed solutions.

## Stop Everything

```bash
# Stop Airflow (in both terminal windows)
Ctrl+C

# Stop MinIO
docker stop minio

# (Optional) Clean data
rm -rf data/raw/* data/processed/* reports/*
```

## Restart Everything

```bash
# Start MinIO
docker start minio

# Terminal 1: Webserver (with macOS fix)
export AIRFLOW_HOME=$(pwd)
airflow webserver --port 8080 --workers 1

# Terminal 2: Scheduler
export AIRFLOW_HOME=$(pwd)
airflow scheduler
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Apache Airflow DAG                        │
│                (Orchestration & Scheduling)                  │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
   Extract Data         Quality Gate         Transform Data
   (API Call)      (Null/Schema Check)    (Feature Engineering)
        │                     │                     │
        │              FAIL → STOP                  │
        │                     │                     │
        └─────────────────────┴─────────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │  Generate Profile    │
                    │  (Pandas Profiling)  │
                    └─────────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │  Log to MLflow      │
                    │  (Artifacts+Metrics) │
                    └─────────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │  Store in MinIO     │
                    │  (S3-Compatible)    │
                    └─────────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │  Version with DVC   │
                    │  (Data Versioning)  │
                    └─────────────────────┘
```

## Pipeline Features

### ✅ Mandatory Quality Gates
- Null value check (< 1% threshold)
- Schema validation
- Data type validation
- Value range validation
- Row count validation

### ✅ Feature Engineering
- **Lag Features**: Past values (1h, 3h, 6h ago)
- **Rolling Statistics**: Moving averages
- **Time Features**: Hour, day, month, weekday
- **Cyclic Encoding**: Sin/cos transformations

### ✅ Storage & Versioning
- MinIO object storage (S3-compatible)
- DVC data versioning
- Git integration (metadata only)

### ✅ Monitoring & Tracking
- Pandas profiling reports
- MLflow experiment tracking
- Airflow task logs
- Quality check reports

## Production Checklist

- [ ] API key added to `.env`
- [ ] MinIO running and accessible
- [ ] Airflow webserver running
- [ ] Airflow scheduler running
- [ ] DVC remote configured
- [ ] DAG enabled in Airflow UI
- [ ] First run successful
- [ ] Quality checks passing
- [ ] Data stored in MinIO
- [ ] DVC files in Git
- [ ] Reports generated
- [ ] Screenshots captured

## Need Help?

1. **Check logs**: Airflow UI → Task → View Log
2. **Review documentation**: See `AIRFLOW_COMMANDS_SCREENSHOTS.md`
3. **Test components individually**:
   ```bash
   # Test extraction
   python src/data_extraction.py
   
   # Test quality checks
   python src/data_quality.py data/raw/weather_data_*.csv
   
   # Test transformation
   python src/data_transformation.py
   
   # Test storage
   python src/storage_versioning.py data/processed/weather_data_*_processed.csv
   ```

## Congratulations! 🎉

You now have a production-ready MLOps pipeline with:
- Automated data extraction
- Strict quality gates
- Feature engineering
- Cloud storage
- Data versioning
- Experiment tracking

**Ready for Phase 2: Model Training & Deployment!**

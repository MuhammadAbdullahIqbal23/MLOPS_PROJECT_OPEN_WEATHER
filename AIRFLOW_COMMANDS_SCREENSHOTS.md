# Apache Airflow MLOps Pipeline - Commands & Screenshots Guide

## Overview
This guide documents all commands needed to run the complete MLOps pipeline with Apache Airflow, including mandatory quality gates, data profiling, and versioning.

---

## Part 1: Environment Setup

### 1. Create Screenshots Folder Structure
```bash
mkdir -p screenshots/airflow screenshots/storage_versioning screenshots/mlflow screenshots/data_quality
```
**Screenshot Required**: `screenshots/airflow/01_folder_structure.png`
- Show the created directory structure in VS Code or terminal

### 2. Install Dependencies
```bash
cd /Users/abdurrehmansubhani/Desktop/Abdullah/MLOps-Project
pip install -r requirements.txt
```
**Screenshot Required**: `screenshots/airflow/02_pip_install.png`
- Terminal showing successful installation of all packages

### 3. Create Environment File
```bash
cat > .env << 'EOF'
# OpenWeatherMap API
OPENWEATHER_API_KEY=your_api_key_here
OPENWEATHER_CITIES=London,Paris,Tokyo,NewYork,Sydney

# MinIO Configuration
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=mlops-data

# MLflow Configuration (Optional - for DagsHub)
MLFLOW_TRACKING_URI=https://dagshub.com/your_username/MLOPS_PROJECT_OPEN_WEATHER.mlflow
DAGSHUB_USERNAME=your_username
DAGSHUB_TOKEN=your_token
EOF
```
**Screenshot Required**: `screenshots/airflow/03_env_file.png`
- Contents of `.env` file (mask sensitive data)

---

## Part 2: Infrastructure Setup

### 4. Start Docker Services (MinIO)
```bash
docker run -d \
  --name minio \
  -p 9000:9000 \
  -p 9001:9001 \
  -e "MINIO_ROOT_USER=minioadmin" \
  -e "MINIO_ROOT_PASSWORD=minioadmin" \
  quay.io/minio/minio server /data --console-address ":9001"
```
**Screenshot Required**: `screenshots/airflow/04_minio_running.png`
- `docker ps` showing MinIO container running

### 5. Access MinIO Console
```bash
open http://localhost:9001
```
**Screenshot Required**: `screenshots/airflow/05_minio_console.png`
- MinIO web console logged in, showing dashboard

### 6. Create MinIO Bucket
**Screenshot Required**: `screenshots/airflow/06_minio_bucket_created.png`
- MinIO console showing `mlops-data` bucket created

### 7. Initialize DVC
```bash
cd /Users/abdurrehmansubhani/Desktop/Abdullah/MLOps-Project
dvc init
dvc remote add -d minio s3://mlops-data/dvc-storage
dvc remote modify minio endpointurl http://localhost:9000
dvc remote modify minio access_key_id minioadmin
dvc remote modify minio secret_access_key minioadmin
```
**Screenshot Required**: `screenshots/airflow/07_dvc_initialized.png`
- Terminal showing DVC initialization and remote configuration

---

## Part 3: Airflow Setup

### 8. Create Airflow Directories
```bash
mkdir -p dags logs plugins data/raw data/processed reports
```
**Screenshot Required**: `screenshots/airflow/08_airflow_dirs.png`
- Directory structure showing all created folders

### 9. Set Airflow Home
```bash
export AIRFLOW_HOME=/Users/abdurrehmansubhani/Desktop/Abdullah/MLOps-Project
echo "export AIRFLOW_HOME=/Users/abdurrehmansubhani/Desktop/Abdullah/MLOps-Project" >> ~/.zshrc
```
**Screenshot Required**: `screenshots/airflow/09_airflow_home.png`
- Terminal showing AIRFLOW_HOME environment variable set

### 10. Initialize Airflow Database
```bash
airflow db init
```
**Screenshot Required**: `screenshots/airflow/10_airflow_db_init.png`
- Terminal showing successful database initialization

### 11. Create Airflow Admin User
```bash
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin
```
**Screenshot Required**: `screenshots/airflow/11_airflow_user_created.png`
- Terminal showing successful user creation

### 12. Start Airflow Webserver
```bash
# In terminal 1
# Note: On macOS, use single worker to avoid SIGSEGV errors
airflow webserver --port 8080 --workers 1

# Alternative if still having issues:
# export AIRFLOW__WEBSERVER__WORKERS=1
# airflow webserver --port 8080
```
**Screenshot Required**: `screenshots/airflow/12_airflow_webserver_running.png`
- Terminal showing webserver started successfully
- Should see "Listening at: http://0.0.0.0:8080"

**Note**: If you see `Worker (pid:XXXX) was sent SIGSEGV!` errors, see [`AIRFLOW_MACOS_FIX.md`](AIRFLOW_MACOS_FIX.md)

### 13. Start Airflow Scheduler
```bash
# In terminal 2
airflow scheduler
```
**Screenshot Required**: `screenshots/airflow/13_airflow_scheduler_running.png`
- Terminal showing scheduler running and picking up DAGs

### 14. Access Airflow Web UI
```bash
open http://localhost:8080
```
**Screenshot Required**: `screenshots/airflow/14_airflow_login.png`
- Airflow login page

**Screenshot Required**: `screenshots/airflow/15_airflow_dashboard.png`
- Airflow dashboard after login (username: admin, password: admin)

---

## Part 4: DAG Verification

### 15. List DAGs
```bash
airflow dags list
```
**Screenshot Required**: `screenshots/airflow/16_dags_list.png`
- Terminal showing `weather_prediction_pipeline` DAG listed

### 16. View DAG in UI
**Screenshot Required**: `screenshots/airflow/17_dag_in_ui.png`
- Airflow UI showing the `weather_prediction_pipeline` DAG in the list

### 17. View DAG Graph
**Screenshot Required**: `screenshots/airflow/18_dag_graph_view.png`
- DAG graph showing all tasks: Extract → Quality Check → [Profile, Transform] → Load → Complete

### 18. View DAG Code
**Screenshot Required**: `screenshots/airflow/19_dag_code_view.png`
- Airflow UI showing the DAG code in the Code tab

---

## Part 5: Pipeline Execution

### 19. Enable DAG
**Screenshot Required**: `screenshots/airflow/20_dag_enabled.png`
- DAG toggle switched to ON (blue/enabled state)

### 20. Trigger DAG Manually
**Screenshot Required**: `screenshots/airflow/21_trigger_dag.png`
- Click "Play" button to trigger DAG manually
- Confirmation dialog showing

### 21. Monitor DAG Run - Extract Task
**Screenshot Required**: `screenshots/airflow/22_extract_task_running.png`
- Task `extract_data` in running (yellow) state

**Screenshot Required**: `screenshots/airflow/23_extract_task_success.png`
- Task `extract_data` completed successfully (green)

### 22. View Extract Task Logs
**Screenshot Required**: `screenshots/airflow/24_extract_task_logs.png`
- Logs showing:
  - API connection successful
  - Data fetched for multiple cities
  - Raw data saved with timestamp
  - XCom push of filepath

### 23. Verify Raw Data Saved
```bash
ls -lh data/raw/
cat data/raw/weather_data_*.csv | head -20
```
**Screenshot Required**: `screenshots/airflow/25_raw_data_saved.png`
- Terminal showing raw CSV file with timestamp and sample data

---

## Part 6: Quality Gate Execution

### 24. Monitor Quality Check Task
**Screenshot Required**: `screenshots/airflow/26_quality_check_running.png`
- Task `quality_check` in running state

**Screenshot Required**: `screenshots/airflow/27_quality_check_success.png`
- Task `quality_check` completed successfully (green)

### 25. View Quality Check Logs
**Screenshot Required**: `screenshots/airflow/28_quality_check_logs.png`
- Logs showing:
  - ✓ Null value check: PASSED (<1%)
  - ✓ Schema validation: PASSED
  - ✓ Data type check: PASSED
  - ✓ Value range check: PASSED
  - ✓ Row count check: PASSED

### 26. Quality Check - Full Report
**Screenshot Required**: `screenshots/airflow/29_quality_report_details.png`
- Detailed quality check report showing all validation results

---

## Part 7: Data Profiling with MLflow

### 27. Monitor Data Profile Task
**Screenshot Required**: `screenshots/airflow/30_profile_task_running.png`
- Task `generate_data_profile` in running state

**Screenshot Required**: `screenshots/airflow/31_profile_task_success.png`
- Task `generate_data_profile` completed successfully

### 28. View Profile Task Logs
**Screenshot Required**: `screenshots/airflow/32_profile_task_logs.png`
- Logs showing:
  - Pandas profiling report generated
  - Report saved to `reports/` directory
  - Artifact logged to MLflow

### 29. View Generated Profile Report
```bash
open reports/weather_data_*_profile.html
```
**Screenshot Required**: `screenshots/airflow/33_profile_report_overview.png`
- Pandas profiling HTML report - Overview section

**Screenshot Required**: `screenshots/airflow/34_profile_report_variables.png`
- Pandas profiling HTML report - Variables section showing distributions

**Screenshot Required**: `screenshots/airflow/35_profile_report_correlations.png`
- Pandas profiling HTML report - Correlations heatmap

### 30. View MLflow Tracking UI
```bash
# If using local MLflow
mlflow ui --port 5000

# Or access DagsHub MLflow
open https://dagshub.com/your_username/MLOPS_PROJECT_OPEN_WEATHER/experiments
```
**Screenshot Required**: `screenshots/airflow/36_mlflow_experiments.png`
- MLflow UI showing `weather_prediction_pipeline` experiment

**Screenshot Required**: `screenshots/airflow/37_mlflow_run_details.png`
- MLflow run details showing:
  - Parameters (data_source, num_rows, num_columns)
  - Metrics (null_count, null_percentage)

**Screenshot Required**: `screenshots/airflow/38_mlflow_artifacts.png`
- MLflow artifacts tab showing logged profile report HTML file

---

## Part 8: Data Transformation

### 31. Monitor Transform Task
**Screenshot Required**: `screenshots/airflow/39_transform_task_running.png`
- Task `transform_data` in running state

**Screenshot Required**: `screenshots/airflow/40_transform_task_success.png`
- Task `transform_data` completed successfully

### 32. View Transform Task Logs
**Screenshot Required**: `screenshots/airflow/41_transform_task_logs.png`
- Logs showing:
  - Feature engineering started
  - Created lag features (1h, 3h, 6h)
  - Created rolling means (3h, 6h, 12h)
  - Created time-based features
  - Processed data saved

### 33. View Processed Data
```bash
ls -lh data/processed/
head -20 data/processed/weather_data_*_processed.csv
```
**Screenshot Required**: `screenshots/airflow/42_processed_data_saved.png`
- Terminal showing processed CSV with all engineered features

### 34. Compare Raw vs Processed Data
```bash
# Count columns
echo "Raw columns:"
head -1 data/raw/weather_data_*.csv | tr ',' '\n' | wc -l

echo "Processed columns:"
head -1 data/processed/weather_data_*_processed.csv | tr ',' '\n' | wc -l
```
**Screenshot Required**: `screenshots/airflow/43_data_comparison.png`
- Terminal showing increased column count after feature engineering

---

## Part 9: Storage & Versioning

### 35. Monitor Load & Version Task
**Screenshot Required**: `screenshots/airflow/44_load_task_running.png`
- Task `load_and_version` in running state

**Screenshot Required**: `screenshots/airflow/45_load_task_success.png`
- Task `load_and_version` completed successfully

### 36. View Load Task Logs
**Screenshot Required**: `screenshots/airflow/46_load_task_logs.png`
- Logs showing:
  - [1/5] MinIO storage initialized
  - [2/5] File uploaded to MinIO
  - [3/5] DVC initialized
  - [4/5] DVC remote configured
  - [5/5] File added to DVC and pushed

### 37. Verify MinIO Upload
**Screenshot Required**: `screenshots/airflow/47_minio_processed_data.png`
- MinIO console showing uploaded file in `processed_data/` folder

### 38. Verify DVC Files Created
```bash
ls -la data/processed/*.dvc
cat data/processed/weather_data_*_processed.csv.dvc
```
**Screenshot Required**: `screenshots/airflow/48_dvc_files_created.png`
- Terminal showing `.dvc` file and its contents (MD5 hash, size)

### 39. Verify DVC Push to MinIO
**Screenshot Required**: `screenshots/airflow/49_minio_dvc_storage.png`
- MinIO console showing `dvc-storage/` folder with DVC cache files

### 40. Check DVC Status
```bash
dvc status
```
**Screenshot Required**: `screenshots/airflow/50_dvc_status.png`
- Terminal showing DVC status (everything up to date)

---

## Part 10: Pipeline Completion

### 41. Monitor Completion Task
**Screenshot Required**: `screenshots/airflow/51_completion_task_success.png`
- Task `log_completion` completed successfully
- All tasks in DAG showing green (success)

### 42. View Completion Task Logs
**Screenshot Required**: `screenshots/airflow/52_completion_logs.png`
- Logs showing:
  - Pipeline completion summary
  - Raw data path
  - Processed data path
  - Timestamp

### 43. DAG Run Complete
**Screenshot Required**: `screenshots/airflow/53_dag_run_complete.png`
- DAG run view showing all tasks completed successfully
- Duration and status displayed

### 44. View DAG Run Gantt Chart
**Screenshot Required**: `screenshots/airflow/54_dag_gantt_chart.png`
- Gantt chart view showing task execution timeline and parallelism

---

## Part 11: Quality Gate Failure Scenario

### 45. Simulate Quality Failure
```bash
# Create bad data with >1% nulls
python -c "
import pandas as pd
import numpy as np
from datetime import datetime

# Create data with excessive nulls
data = {
    'collection_timestamp': [datetime.now()] * 100,
    'temperature': [np.nan] * 50 + list(range(50)),  # 50% nulls
    'humidity': list(range(100)),
    'pressure': list(range(100))
}
df = pd.DataFrame(data)
df.to_csv('data/raw/bad_weather_data.csv', index=False)
print('Bad data created with 50% nulls in temperature')
"
```
**Screenshot Required**: `screenshots/airflow/55_bad_data_created.png`
- Terminal showing bad data creation

### 46. Test Quality Check on Bad Data
```bash
python -c "
from src.data_quality import validate_data_quality

expected_columns = ['collection_timestamp', 'temperature', 'humidity', 'pressure']
result = validate_data_quality('data/raw/bad_weather_data.csv', expected_columns)
print(f'Quality check result: {result}')
"
```
**Screenshot Required**: `screenshots/airflow/56_quality_check_failed.png`
- Terminal showing:
  - ✗ Null value check: FAILED
  - Failed columns: temperature (50.0%)
  - Pipeline stopped

### 47. View Failed DAG Run
**Screenshot Required**: `screenshots/airflow/57_dag_run_failed.png`
- DAG run with `quality_check` task in red (failed)
- Downstream tasks not executed

### 48. View Failure Logs
**Screenshot Required**: `screenshots/airflow/58_failure_logs.png`
- Quality check task logs showing:
  - AirflowException raised
  - "Data quality checks FAILED! Pipeline stopped."

---

## Part 12: Scheduled DAG Execution

### 49. View DAG Schedule
**Screenshot Required**: `screenshots/airflow/59_dag_schedule.png`
- DAG details showing schedule: `@daily`
- Next run time displayed

### 50. View Run History
**Screenshot Required**: `screenshots/airflow/60_dag_run_history.png`
- DAG runs page showing multiple successful runs over time

### 51. View Task Duration Statistics
**Screenshot Required**: `screenshots/airflow/61_task_duration_stats.png`
- Task duration chart showing performance over multiple runs

---

## Part 13: Git Version Control

### 52. Check Git Status
```bash
git status
```
**Screenshot Required**: `screenshots/airflow/62_git_status.png`
- Git status showing:
  - `.dvc/` directory
  - `.dvcignore` file
  - `data/processed/*.dvc` files
  - No large data files (excluded by `.gitignore`)

### 53. Add DVC Files to Git
```bash
git add .dvc .dvcignore data/processed/*.dvc
git add dags/ src/ requirements.txt
git commit -m "Add complete MLOps pipeline with quality gates and versioning"
```
**Screenshot Required**: `screenshots/airflow/63_git_commit.png`
- Terminal showing successful commit

### 54. View Git Log
```bash
git log --oneline --graph -5
```
**Screenshot Required**: `screenshots/airflow/64_git_log.png`
- Git log showing pipeline commits

### 55. Push to Remote
```bash
git push origin phase-1
```
**Screenshot Required**: `screenshots/airflow/65_git_push.png`
- Terminal showing successful push

---

## Part 14: System Overview

### 56. Check All Running Services
```bash
# Check Docker
docker ps

# Check Airflow processes
ps aux | grep airflow | grep -v grep

# Check ports
lsof -i :8080,9000,9001,5000
```
**Screenshot Required**: `screenshots/airflow/66_all_services_running.png`
- Terminal showing all services active

### 57. Directory Structure Overview
```bash
tree -L 3 -I '__pycache__|*.pyc|mlruns'
```
**Screenshot Required**: `screenshots/airflow/67_project_structure.png`
- Complete project directory tree

### 58. Final Dashboard View
**Screenshot Required**: `screenshots/airflow/68_final_overview.png`
- Split screen showing:
  - Airflow UI with successful DAG run
  - MinIO console with stored data
  - MLflow UI with logged experiments
  - VS Code with project structure

---

## Summary of Required Screenshots

Total Screenshots Required: **68**

### Breakdown by Category:
- **Setup & Installation**: 8 screenshots (01-08)
- **Airflow Configuration**: 12 screenshots (09-20)
- **Pipeline Execution - Extraction**: 6 screenshots (21-26)
- **Quality Gate**: 4 screenshots (26-29)
- **Data Profiling & MLflow**: 9 screenshots (30-38)
- **Transformation**: 5 screenshots (39-43)
- **Storage & Versioning**: 8 screenshots (44-51)
- **Pipeline Completion**: 4 screenshots (51-54)
- **Quality Failure Scenario**: 4 screenshots (55-58)
- **Scheduling & History**: 3 screenshots (59-61)
- **Git Integration**: 4 screenshots (62-65)
- **System Overview**: 3 screenshots (66-68)

---

## Quick Reference Commands

### Start All Services
```bash
# Terminal 1: MinIO
docker start minio || docker run -d --name minio -p 9000:9000 -p 9001:9001 \
  -e "MINIO_ROOT_USER=minioadmin" -e "MINIO_ROOT_PASSWORD=minioadmin" \
  quay.io/minio/minio server /data --console-address ":9001"

# Terminal 2: Airflow Webserver (macOS: use single worker)
export AIRFLOW_HOME=/Users/abdurrehmansubhani/Desktop/Abdullah/MLOps-Project
airflow webserver --port 8080 --workers 1

# Terminal 3: Airflow Scheduler
export AIRFLOW_HOME=/Users/abdurrehmansubhani/Desktop/Abdullah/MLOps-Project
airflow scheduler

# Terminal 4 (optional): MLflow UI
mlflow ui --port 5000
```

### Trigger Pipeline
```bash
airflow dags trigger weather_prediction_pipeline
```

### Monitor Pipeline
```bash
# Check DAG runs
airflow dags list-runs -d weather_prediction_pipeline

# Check task status
airflow tasks list weather_prediction_pipeline

# View logs
airflow tasks test weather_prediction_pipeline extract_data 2025-12-01
```

### Cleanup
```bash
# Stop Airflow
pkill -f airflow

# Stop MinIO
docker stop minio

# Clean data (be careful!)
rm -rf data/raw/* data/processed/* reports/*
```

---

## Access URLs

- **Airflow UI**: http://localhost:8080 (admin/admin)
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)
- **MLflow UI**: http://localhost:5000 (if running locally)
- **DagsHub**: https://dagshub.com/your_username/MLOPS_PROJECT_OPEN_WEATHER

---

## Troubleshooting

### Common Issues and Solutions

1. **DAG not showing in Airflow**
   ```bash
   # Check DAG syntax
   python dags/weather_pipeline_dag.py
   
   # Check DAG parse errors
   airflow dags list-import-errors
   ```

2. **MinIO connection failed**
   ```bash
   # Test connection
   python -c "from src.storage_versioning import MinIOStorage; m = MinIOStorage()"
   ```

3. **DVC push failed**
   ```bash
   # Check DVC config
   dvc remote list -v
   
   # Test connection
   dvc remote default minio
   ```

4. **Import errors in DAG**
   ```bash
   # Check Python path
   echo $PYTHONPATH
   
   # Add src to path
   export PYTHONPATH=/Users/abdurrehmansubhani/Desktop/Abdullah/MLOps-Project:$PYTHONPATH
   ```

5. **Airflow Webserver SIGSEGV Errors (macOS)**
   ```bash
   # Kill existing processes
   pkill -f airflow
   
   # Start with single worker
   export AIRFLOW_HOME=$(pwd)
   airflow webserver --port 8080 --workers 1
   
   # See AIRFLOW_MACOS_FIX.md for detailed solutions
   ```

6. **Port already in use**
   ```bash
   # Check what's using the port
   lsof -i :8080
   
   # Kill the process
   kill -9 <PID>
   
   # Or use different port
   airflow webserver --port 8081
   ```

---

## Notes

- Replace `your_api_key_here`, `your_username`, and `your_token` with actual values
- Mask sensitive information in screenshots
- Take screenshots in high resolution (at least 1920x1080)
- Use annotation tools to highlight important elements in screenshots
- Store all screenshots in the designated folders under `screenshots/`

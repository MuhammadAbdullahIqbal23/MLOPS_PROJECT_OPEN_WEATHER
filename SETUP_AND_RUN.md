# MLOps Pipeline - Setup and Execution Guide

## Complete Step-by-Step Instructions with Screenshots

This guide provides detailed instructions for setting up and running the MLOps pipeline, with specific points where screenshots should be taken for documentation.

---

## Prerequisites Setup

### 1. Get OpenWeatherMap API Key

1. Go to https://openweathermap.org/api
2. Sign up for a free account
3. Navigate to API keys section
4. Copy your API key

📸 **Screenshot 0**: OpenWeatherMap API key page

---

## Initial Setup

### Step 1: Navigate to Project Directory

```bash
cd /Users/abdurrehmansubhani/Desktop/Abdullah/MLOps-Project
```

### Step 2: Create Environment File

```bash
cp .env.example .env
```

Now edit the `.env` file and add your OpenWeatherMap API key:

```bash
nano .env
# or
open -e .env
```

Update this line with your actual API key:
```
OPENWEATHER_API_KEY=your_actual_api_key_here
```

---

## Starting the Services

### Step 3: Start Docker Compose Services

```bash
docker-compose up -d
```

This command will:
- Pull Docker images (first time only)
- Start Airflow webserver, scheduler, and MinIO
- Initialize Airflow database
- Create default admin user

**Wait 2-3 minutes for all services to initialize**

### Step 4: Verify Services Are Running

```bash
docker-compose ps
```

📸 **Screenshot 1: Docker Services Running**
- Take screenshot showing all services with "Up" status
- Should show: airflow-webserver, airflow-scheduler, minio

Expected output:
```
NAME                    STATUS          PORTS
airflow-webserver       Up (healthy)    0.0.0.0:8080->8080/tcp
airflow-scheduler       Up (healthy)    
minio                   Up (healthy)    0.0.0.0:9000-9001->9000-9001/tcp
```

---

## Accessing the Services

### Step 5: Open Airflow Web UI

Open your browser and go to: **http://localhost:8080**

Login credentials:
- Username: `admin`
- Password: `admin`

📸 **Screenshot 2: Airflow DAG List**
- Take screenshot of the Airflow homepage showing the DAG list
- You should see `weather_prediction_pipeline` DAG

### Step 6: View DAG Graph

1. Click on the `weather_prediction_pipeline` DAG
2. Click on the "Graph" tab

📸 **Screenshot 3: DAG Graph View**
- Take screenshot showing the complete DAG structure
- Should show 6 tasks with their dependencies:
  - extract_data
  - quality_check
  - generate_data_profile
  - transform_data
  - load_and_version
  - log_completion

### Step 7: Open MinIO Console

Open your browser and go to: **http://localhost:9001**

Login credentials:
- Username: `minioadmin`
- Password: `minioadmin`

📸 **Screenshot 4: MinIO Bucket Created**
- Take screenshot of MinIO console
- Should show the `mlops-data` bucket

---

## Running the Pipeline

### Step 8: Trigger the DAG

In the Airflow UI:
1. Make sure the DAG is **unpaused** (toggle switch should be blue/on)
2. Click the "▶ Play" button on the right side
3. Select "Trigger DAG"

📸 **Screenshot 5: Trigger DAG Run**
- Take screenshot of the trigger confirmation dialog or the triggered DAG

### Step 9: Monitor DAG Execution

Watch the DAG run in real-time:
- Refresh the page or enable auto-refresh
- Tasks will change color:
  - **White/Grey**: Queued
  - **Yellow**: Running
  - **Green**: Success
  - **Red**: Failed

📸 **Screenshot 6: DAG Run in Progress**
- Take screenshot showing tasks in progress (some green, some yellow)

---

## Examining Task Outputs

### Step 10: View Data Extraction Logs

1. Click on the `extract_data` task (green box)
2. Click "Log" button
3. Scroll through the logs

📸 **Screenshot 7: Data Extraction Task Logs**
- Take screenshot showing:
  - API call success
  - Data shape (40, 20)
  - File saved path

Look for output like:
```
Data extracted and saved to /opt/airflow/data/raw/weather_data_20251201_103045.csv
Shape: (40, 20)
Collection time: 2025-12-01 10:30:45
```

### Step 11: View Quality Check Logs

1. Click on the `quality_check` task
2. Click "Log" button

📸 **Screenshot 8: Quality Check Task Logs**
- Take screenshot showing quality report
- Should show all checks passed (✓ symbols)

Look for:
```
DATA QUALITY REPORT
Overall Status: ✓ PASSED
Passed: 5/5
✓ NULL_VALUES
✓ SCHEMA_VALIDATION
✓ DATA_TYPES
✓ VALUE_RANGES
✓ ROW_COUNT
```

---

## Verifying Data Quality

### Step 12: View Quality Report JSON

```bash
docker-compose exec airflow-scheduler \
  cat /opt/airflow/data/raw/*_quality_report.json | \
  python3 -m json.tool
```

📸 **Screenshot 9: Quality Report JSON**
- Take screenshot of formatted JSON output
- Should show detailed check results

### Step 13: Access Pandas Profiling Report

```bash
# List reports
docker-compose exec airflow-scheduler ls -lh /opt/airflow/reports/

# Copy report to local machine for viewing
docker cp $(docker-compose ps -q airflow-scheduler):/opt/airflow/reports/weather_data_XXXXXX_profile.html ./profiling_report.html

# Open in browser
open profiling_report.html
```

📸 **Screenshot 10: Pandas Profiling Report**
- Take screenshot of the HTML profiling report in browser
- Show the overview section with dataset statistics

---

## Examining Transformed Data

### Step 14: View Transformation Logs

1. In Airflow UI, click on `transform_data` task
2. Click "Log" button

📸 **Screenshot 11: Transformation Task Logs**
- Take screenshot showing feature engineering steps
- Should show:
  - Initial shape: (40, 20)
  - Final shape: (38, 59)
  - Total features: 59

### Step 15: View Processed Data Sample

```bash
# List processed files
docker-compose exec airflow-scheduler ls -lh /opt/airflow/data/processed/

# View first 10 rows with column headers
docker-compose exec airflow-scheduler head -10 /opt/airflow/data/processed/*.csv
```

📸 **Screenshot 12: Processed Data Sample**
- Take screenshot showing first few rows of processed data
- Should show many engineered features (59 columns)

---

## Verifying Storage and Versioning

### Step 16: Check MinIO Storage

1. Go back to MinIO console (http://localhost:9001)
2. Click on `mlops-data` bucket
3. Navigate to folders to see uploaded files

📸 **Screenshot 13: MinIO Data Uploaded**
- Take screenshot showing files in MinIO bucket
- Should see processed_data/ and dvc-storage/ folders

### Step 17: Verify DVC Files

```bash
# List DVC metadata files
docker-compose exec airflow-scheduler ls -la /opt/airflow/data/processed/
```

📸 **Screenshot 14: DVC Files Generated**
- Take screenshot showing .dvc files alongside data files
- Should see files like: `weather_data_XXXXX_processed.csv.dvc`

---

## Final Verification

### Step 18: View Complete DAG Run

1. Return to Airflow UI
2. View the Graph view again
3. All tasks should be green

📸 **Screenshot 15: Complete DAG Run**
- Take screenshot showing all 6 tasks completed successfully (all green)

### Step 19: View Run Statistics

1. Click on "Grid" view in Airflow
2. Shows history of DAG runs

📸 **Screenshot 16 (Optional): DAG Run History**
- Take screenshot showing successful run in grid view

---

## Additional Verification Commands

### Verify Raw Data

```bash
# Count rows in raw data
docker-compose exec airflow-scheduler bash -c "wc -l /opt/airflow/data/raw/*.csv"

# View data structure
docker-compose exec airflow-scheduler bash -c "head -1 /opt/airflow/data/raw/*.csv | tr ',' '\n'"
```

### Verify Feature Count

```bash
# Count features in processed data
docker-compose exec airflow-scheduler bash -c "head -1 /opt/airflow/data/processed/*.csv | tr ',' '\n' | wc -l"
```

Expected output: 59

### Verify MinIO Objects

```bash
docker-compose exec airflow-scheduler python3 << 'EOF'
from minio import Minio
client = Minio('minio:9000', access_key='minioadmin', secret_key='minioadmin', secure=False)
objects = client.list_objects('mlops-data', recursive=True)
print("Objects in MinIO:")
for obj in objects:
    print(f"  {obj.object_name} - {obj.size} bytes")
EOF
```

### Check DVC Status

```bash
docker-compose exec airflow-scheduler bash -c "cd /opt/airflow && dvc status"
```

---

## Generating the PDF Report

### Step 20: Compile LaTeX Document

First, ensure you have the screenshots saved in a `screenshots/` directory:

```bash
mkdir -p screenshots
# Place all screenshots in this folder with the names referenced in the LaTeX
```

Then compile the LaTeX document:

```bash
# Install LaTeX if needed (macOS)
brew install --cask mactex

# Or use online LaTeX editor like Overleaf

# Compile locally
pdflatex MLOps_Phase1_Report.tex
pdflatex MLOps_Phase1_Report.tex  # Run twice for table of contents
```

📸 **Screenshot 17: Generated PDF**
- Take screenshot of the generated PDF document

---

## Screenshot Summary

Here's a checklist of all required screenshots:

- [ ] **Screenshot 0**: OpenWeatherMap API key page
- [ ] **Screenshot 1**: Docker services running (`docker-compose ps`)
- [ ] **Screenshot 2**: Airflow DAG list
- [ ] **Screenshot 3**: DAG graph view with all tasks
- [ ] **Screenshot 4**: MinIO bucket in console
- [ ] **Screenshot 5**: Triggering the DAG
- [ ] **Screenshot 6**: DAG run in progress
- [ ] **Screenshot 7**: Data extraction task logs
- [ ] **Screenshot 8**: Quality check task logs
- [ ] **Screenshot 9**: Quality report JSON output
- [ ] **Screenshot 10**: Pandas profiling HTML report
- [ ] **Screenshot 11**: Transformation task logs
- [ ] **Screenshot 12**: Processed data sample
- [ ] **Screenshot 13**: MinIO storage with uploaded files
- [ ] **Screenshot 14**: DVC metadata files
- [ ] **Screenshot 15**: Complete DAG run (all green)

---

## Cleaning Up

### Stop Services

```bash
docker-compose down
```

### Remove All Data (Clean Restart)

```bash
docker-compose down -v
rm -rf data/raw/* data/processed/* reports/*
```

### Restart Fresh

```bash
docker-compose up -d
```

---

## Troubleshooting

### Issue: Services Won't Start

```bash
# Check logs
docker-compose logs

# Try rebuilding
docker-compose down -v
docker-compose up -d --build
```

### Issue: API Key Not Working

```bash
# Verify environment variable in container
docker-compose exec airflow-scheduler env | grep OPENWEATHER

# Restart services after updating .env
docker-compose restart
```

### Issue: DAG Not Appearing

```bash
# Check for syntax errors
docker-compose exec airflow-scheduler python3 -m py_compile /opt/airflow/dags/weather_pipeline_dag.py

# Restart scheduler
docker-compose restart airflow-scheduler
```

### Issue: MinIO Connection Failed

```bash
# Check MinIO health
curl http://localhost:9000/minio/health/live

# Recreate bucket manually
docker-compose exec airflow-scheduler python3 << 'EOF'
from minio import Minio
client = Minio('minio:9000', access_key='minioadmin', secret_key='minioadmin', secure=False)
if not client.bucket_exists('mlops-data'):
    client.make_bucket('mlops-data')
    print('Bucket created')
EOF
```

---

## Tips for Screenshots

1. **Use high resolution**: Take screenshots at full resolution
2. **Highlight important parts**: Use annotation tools to highlight key information
3. **Include timestamps**: Show date/time in screenshots when possible
4. **Consistent naming**: Name screenshots as referenced in LaTeX (screenshot_01_docker_services.png, etc.)
5. **Clean UI**: Close unnecessary tabs/windows before taking screenshots

---

## LaTeX Document Notes

The LaTeX document expects screenshots in the following format:
- Location: `screenshots/` directory (same level as .tex file)
- Naming: `screenshot_XX_description.png`
- Format: PNG or JPG

If a screenshot is missing, LaTeX will show a placeholder. You can continue and add screenshots later.

---

## Success Criteria

Your pipeline is working correctly if:

✅ All 6 tasks complete successfully (green)  
✅ Quality report shows 5/5 checks passed  
✅ Processed data has 59 features  
✅ Data is uploaded to MinIO  
✅ DVC .dvc files are created  
✅ Pandas profiling report is generated  
✅ No errors in any task logs

---

## Next Steps

After completing Phase I:

1. **Model Training**: Add model training task to DAG
2. **Model Registry**: Implement MLflow model versioning
3. **Model Serving**: Deploy model with FastAPI
4. **Monitoring**: Add Prometheus and Grafana
5. **CI/CD**: Implement GitHub Actions

---

## Contact and Support

For issues or questions:
- Check the README.md
- Review Airflow task logs
- Check Docker logs: `docker-compose logs`

Good luck with your MLOps pipeline! 🚀

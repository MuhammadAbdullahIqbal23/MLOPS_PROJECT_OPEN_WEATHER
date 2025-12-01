# MLOps Pipeline - Commands and Screenshots Guide

## Quick Reference: All Commands and Screenshot Points

This document provides all the commands you need to run in sequence, with clear indicators of when to take screenshots for your LaTeX report.

---

## PART 1: INITIAL SETUP

### Step 1: Navigate to project
```bash
cd /Users/abdurrehmansubhani/Desktop/Abdullah/MLOps-Project
```

### Step 2: Configure environment
```bash
# Create .env file
cp .env.example .env

# Edit and add your OpenWeatherMap API key
nano .env
# Update: OPENWEATHER_API_KEY=your_actual_api_key_here
```

---

## PART 2: START SERVICES

### Step 3: Quick start (recommended)
```bash
./quickstart.sh
```

OR manually:
```bash
docker-compose up -d
sleep 60  # Wait for initialization
```

### Step 4: Verify services
```bash
docker-compose ps
```

📸 **SCREENSHOT 1: Docker Services Running**
- Show all 3 services: airflow-webserver, airflow-scheduler, minio
- Status should be "Up (healthy)"

---

## PART 3: ACCESS WEB INTERFACES

### Step 5: Open Airflow
- Browser: http://localhost:8080
- Login: admin / admin

📸 **SCREENSHOT 2: Airflow DAG List**
- Show the main Airflow page with weather_prediction_pipeline DAG

### Step 6: View DAG structure
- Click on weather_prediction_pipeline
- Click "Graph" tab

📸 **SCREENSHOT 3: DAG Graph View**
- Show all 6 tasks and their dependencies

### Step 7: Open MinIO
- Browser: http://localhost:9001
- Login: minioadmin / minioadmin

📸 **SCREENSHOT 4: MinIO Bucket**
- Show the mlops-data bucket

---

## PART 4: RUN THE PIPELINE

### Step 8: Trigger DAG
In Airflow UI:
1. Toggle DAG to ON
2. Click Play button → "Trigger DAG"

📸 **SCREENSHOT 5: Trigger DAG**
- Show the trigger action

### Step 9: Watch execution
Wait for tasks to complete (2-3 minutes)

📸 **SCREENSHOT 6: DAG Running**
- Show some tasks green, some yellow (in progress)

---

## PART 5: EXAMINE OUTPUTS

### Step 10: Data Extraction logs
In Airflow UI: Click extract_data task → Log

📸 **SCREENSHOT 7: Extraction Logs**
- Show "Data extracted and saved" message with file path

### Step 11: Quality Check logs
Click quality_check task → Log

📸 **SCREENSHOT 8: Quality Check Logs**
- Show "DATA QUALITY REPORT" with all ✓ PASSED

### Step 12: Quality Report JSON
```bash
docker-compose exec airflow-scheduler cat /opt/airflow/data/raw/*_quality_report.json | python3 -m json.tool
```

📸 **SCREENSHOT 9: Quality Report JSON**
- Show formatted JSON with check results

### Step 13: Pandas Profiling Report
```bash
# List reports
docker-compose exec airflow-scheduler ls -lh /opt/airflow/reports/

# Copy to local
docker cp $(docker-compose ps -q airflow-scheduler):/opt/airflow/reports/weather_data_$(docker-compose exec airflow-scheduler ls /opt/airflow/reports/ | grep profile | head -1) ./profiling_report.html

# Open in browser
open profiling_report.html
```

📸 **SCREENSHOT 10: Profiling Report**
- Show the HTML report overview section in browser

### Step 14: Transformation logs
In Airflow UI: Click transform_data task → Log

📸 **SCREENSHOT 11: Transformation Logs**
- Show feature engineering steps and final shape (38, 59)

### Step 15: Processed data sample
```bash
docker-compose exec airflow-scheduler head -10 /opt/airflow/data/processed/*.csv
```

📸 **SCREENSHOT 12: Processed Data**
- Show first few rows with many columns

---

## PART 6: VERIFY STORAGE

### Step 16: MinIO storage
In MinIO Console (http://localhost:9001):
- Navigate to mlops-data bucket
- Browse folders

📸 **SCREENSHOT 13: MinIO Data**
- Show uploaded files in processed_data/ folder

### Step 17: DVC files
```bash
docker-compose exec airflow-scheduler ls -la /opt/airflow/data/processed/
```

📸 **SCREENSHOT 14: DVC Files**
- Show .dvc metadata files next to data files

### Step 18: Complete DAG
In Airflow UI: View Graph again

📸 **SCREENSHOT 15: Complete DAG**
- Show all 6 tasks in green (success)

---

## PART 7: ADDITIONAL VERIFICATION

### Verify data counts
```bash
# Count raw data rows
docker-compose exec airflow-scheduler bash -c "wc -l /opt/airflow/data/raw/*.csv"

# Expected: ~41 lines (40 data + 1 header)

# Count features
docker-compose exec airflow-scheduler bash -c "head -1 /opt/airflow/data/processed/*.csv | tr ',' '\n' | wc -l"

# Expected: 59 features
```

### Verify MinIO objects
```bash
docker-compose exec airflow-scheduler python3 << 'EOF'
from minio import Minio
client = Minio('minio:9000', access_key='minioadmin', secret_key='minioadmin', secure=False)
objects = client.list_objects('mlops-data', recursive=True)
print("\n=== MinIO Objects ===")
for obj in objects:
    print(f"{obj.object_name:50s} {obj.size:>10,} bytes")
print("=" * 70)
EOF
```

### Check DVC status
```bash
docker-compose exec airflow-scheduler bash -c "cd /opt/airflow && dvc status"
```

### View quality report details
```bash
docker-compose exec airflow-scheduler python3 << 'EOF'
import json
import glob

files = glob.glob('/opt/airflow/data/raw/*_quality_report.json')
if files:
    with open(files[0]) as f:
        report = json.load(f)
    
    print("\n" + "="*50)
    print("DATA QUALITY REPORT SUMMARY")
    print("="*50)
    print(f"Overall Status: {'✓ PASSED' if report['overall_passed'] else '✗ FAILED'}")
    print(f"Total Checks: {report['total_checks']}")
    print(f"Passed: {report['passed_checks']}")
    print(f"Failed: {report['failed_checks']}")
    print("\nIndividual Checks:")
    for check in report['checks']:
        status = "✓" if check['passed'] else "✗"
        print(f"  {status} {check['check'].upper()}")
    print("="*50 + "\n")
EOF
```

---

## PART 8: CREATE PDF DOCUMENTATION

### Step 19: Organize screenshots
```bash
# Create screenshots directory
mkdir -p screenshots

# Move or place your screenshots with these names:
# screenshot_01_docker_services.png
# screenshot_02_airflow_dag_list.png
# screenshot_03_dag_graph.png
# screenshot_04_minio_bucket.png
# screenshot_05_trigger_dag.png
# screenshot_06_dag_progress.png
# screenshot_07_extraction_logs.png
# screenshot_08_quality_check.png
# screenshot_09_quality_report.png
# screenshot_10_profiling_report.png
# screenshot_11_transformation.png
# screenshot_12_processed_data.png
# screenshot_13_minio_data.png
# screenshot_14_dvc_files.png
# screenshot_15_complete_dag.png
```

### Step 20: Compile LaTeX (if you have LaTeX installed)
```bash
# Install LaTeX (macOS - skip if already installed)
# brew install --cask mactex

# Compile PDF
pdflatex MLOps_Phase1_Report.tex
pdflatex MLOps_Phase1_Report.tex  # Run twice for TOC

# Open PDF
open MLOps_Phase1_Report.pdf
```

Alternatively, use Overleaf:
1. Go to https://www.overleaf.com/
2. Create new project → Upload Project
3. Upload MLOps_Phase1_Report.tex and screenshots/ folder
4. Compile and download PDF

---

## TROUBLESHOOTING COMMANDS

### If services won't start:
```bash
docker-compose down -v
docker-compose up -d
```

### If DAG doesn't appear:
```bash
# Check DAG for syntax errors
docker-compose exec airflow-scheduler python3 -m py_compile /opt/airflow/dags/weather_pipeline_dag.py

# Restart scheduler
docker-compose restart airflow-scheduler
```

### If API key error:
```bash
# Verify API key in container
docker-compose exec airflow-scheduler env | grep OPENWEATHER

# After updating .env, restart
docker-compose restart
```

### View service logs:
```bash
# All logs
docker-compose logs

# Specific service
docker-compose logs airflow-scheduler
docker-compose logs airflow-webserver
docker-compose logs minio

# Follow logs
docker-compose logs -f airflow-scheduler
```

### Reset everything:
```bash
# Stop and remove everything
docker-compose down -v

# Remove data files
rm -rf data/raw/* data/processed/* reports/*

# Start fresh
docker-compose up -d
```

---

## COMPLETE WORKFLOW SUMMARY

```bash
# 1. Setup
cd /Users/abdurrehmansubhani/Desktop/Abdullah/MLOps-Project
cp .env.example .env
# Edit .env with your API key

# 2. Start services
./quickstart.sh
# Wait 2-3 minutes

# 3. Verify
docker-compose ps
# 📸 Screenshot 1

# 4. Access Airflow
# Open http://localhost:8080 (admin/admin)
# 📸 Screenshots 2, 3

# 5. Access MinIO  
# Open http://localhost:9001 (minioadmin/minioadmin)
# 📸 Screenshot 4

# 6. Run pipeline
# Trigger DAG in Airflow UI
# 📸 Screenshots 5, 6

# 7. Check outputs
# View task logs in Airflow
# 📸 Screenshots 7, 8, 11

# 8. Verify data
docker-compose exec airflow-scheduler cat /opt/airflow/data/raw/*_quality_report.json | python3 -m json.tool
# 📸 Screenshot 9

docker-compose exec airflow-scheduler head -10 /opt/airflow/data/processed/*.csv
# 📸 Screenshot 12

# 9. Verify storage
# Check MinIO console
# 📸 Screenshot 13

docker-compose exec airflow-scheduler ls -la /opt/airflow/data/processed/
# 📸 Screenshot 14

# 10. Final verification
# View completed DAG in Airflow
# 📸 Screenshot 15

# 11. Generate PDF
pdflatex MLOps_Phase1_Report.tex
pdflatex MLOps_Phase1_Report.tex
open MLOps_Phase1_Report.pdf
```

---

## SCREENSHOTS CHECKLIST

- [ ] Screenshot 1: Docker services running (docker-compose ps)
- [ ] Screenshot 2: Airflow DAG list page
- [ ] Screenshot 3: DAG graph view with 6 tasks
- [ ] Screenshot 4: MinIO bucket (mlops-data)
- [ ] Screenshot 5: Triggering DAG
- [ ] Screenshot 6: DAG execution in progress
- [ ] Screenshot 7: Data extraction task logs
- [ ] Screenshot 8: Quality check task logs (all passed)
- [ ] Screenshot 9: Quality report JSON formatted
- [ ] Screenshot 10: Pandas profiling HTML report
- [ ] Screenshot 11: Transformation task logs (59 features)
- [ ] Screenshot 12: Sample processed data
- [ ] Screenshot 13: MinIO with uploaded data files
- [ ] Screenshot 14: DVC .dvc metadata files
- [ ] Screenshot 15: Completed DAG (all green)

---

## SUCCESS CRITERIA

Your pipeline is working if:

✅ `docker-compose ps` shows 3 services "Up (healthy)"  
✅ Airflow UI accessible at http://localhost:8080  
✅ MinIO console accessible at http://localhost:9001  
✅ DAG completes with all 6 tasks green  
✅ Quality report shows 5/5 checks passed  
✅ Processed data has 59 features  
✅ Data uploaded to MinIO  
✅ DVC .dvc files created  

---

## STOP SERVICES

When done:
```bash
# Stop services
docker-compose down

# Or stop and remove all data
docker-compose down -v
```

---

**Ready to start? Run:**
```bash
./quickstart.sh
```

Then follow the SETUP_AND_RUN.md guide for detailed instructions!

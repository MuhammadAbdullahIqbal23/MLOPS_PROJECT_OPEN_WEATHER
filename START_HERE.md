# 🚀 EXECUTION GUIDE - START HERE

## Complete MLOps Pipeline Implementation

**Welcome!** This guide will walk you through running the complete MLOps pipeline and generating your PDF report with screenshots.

---

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] Docker Desktop installed and running
- [ ] At least 4GB RAM available
- [ ] Ports 8080, 9000, 9001 available (not in use)
- [ ] OpenWeatherMap API key (get free at https://openweathermap.org/api)
- [ ] Terminal/command line access
- [ ] Web browser
- [ ] Screenshot tool ready

---

## 🎯 PHASE 1: SETUP (5 minutes)

### Step 1: Navigate to Project

```bash
cd /Users/abdurrehmansubhani/Desktop/Abdullah/MLOps-Project
```

### Step 2: Configure API Key

```bash
# Copy environment template
cp .env.example .env

# Edit .env file
nano .env
# OR
open -e .env
```

**Add your OpenWeatherMap API key:**
```
OPENWEATHER_API_KEY=your_actual_api_key_here
```

Save and close the file.

### Step 3: Quick Start

```bash
./quickstart.sh
```

This script will:
- ✅ Check Docker is running
- ✅ Start all services (Airflow + MinIO)
- ✅ Initialize the environment
- ✅ Show service status

**⏳ Wait 2-3 minutes for initialization**

---

## 🖼️ PHASE 2: TAKE SCREENSHOTS (30 minutes)

### 📸 Screenshot 1: Docker Services

```bash
docker-compose ps
```

**What to capture:**
- All 3 services showing "Up (healthy)" status
- airflow-webserver, airflow-scheduler, minio

**Save as:** `screenshots/screenshot_01_docker_services.png`

---

### 📸 Screenshot 2: Airflow DAG List

1. Open browser: http://localhost:8080
2. Login: admin / admin

**What to capture:**
- Main Airflow page
- `weather_prediction_pipeline` DAG visible in list

**Save as:** `screenshots/screenshot_02_airflow_dag_list.png`

---

### 📸 Screenshot 3: DAG Graph View

1. Click on `weather_prediction_pipeline` DAG
2. Click "Graph" tab

**What to capture:**
- Complete DAG structure
- All 6 tasks with arrows showing dependencies
- Tasks: extract_data → quality_check → [generate_data_profile, transform_data] → load_and_version → log_completion

**Save as:** `screenshots/screenshot_03_dag_graph.png`

---

### 📸 Screenshot 4: MinIO Bucket

1. Open browser: http://localhost:9001
2. Login: minioadmin / minioadmin
3. Navigate to Buckets

**What to capture:**
- MinIO console
- `mlops-data` bucket visible

**Save as:** `screenshots/screenshot_04_minio_bucket.png`

---

### 📸 Screenshot 5: Trigger DAG

**In Airflow UI:**
1. Ensure DAG is toggled ON (blue toggle)
2. Click the ▶ (Play) button
3. Select "Trigger DAG"

**What to capture:**
- The moment of triggering (dialog or confirmation)

**Save as:** `screenshots/screenshot_05_trigger_dag.png`

---

### 📸 Screenshot 6: DAG Running

**Wait 30 seconds, then refresh Airflow**

**What to capture:**
- DAG execution in progress
- Some tasks green (completed)
- Some tasks yellow (running)

**Save as:** `screenshots/screenshot_06_dag_progress.png`

---

### 📸 Screenshot 7: Extraction Logs

1. Click on `extract_data` task (should be green)
2. Click "Log" button
3. Scroll to see output

**What to capture:**
- Log output showing:
  - "Data extracted and saved to..."
  - "Shape: (40, 20)"
  - Collection timestamp

**Save as:** `screenshots/screenshot_07_extraction_logs.png`

---

### 📸 Screenshot 8: Quality Check Logs

1. Click on `quality_check` task
2. Click "Log" button

**What to capture:**
- "DATA QUALITY REPORT"
- "Overall Status: ✓ PASSED"
- All checks showing ✓ (passed)
- "Passed: 5/5"

**Save as:** `screenshots/screenshot_08_quality_check.png`

---

### 📸 Screenshot 9: Quality Report JSON

Run in terminal:
```bash
docker-compose exec airflow-scheduler cat /opt/airflow/data/raw/*_quality_report.json | python3 -m json.tool
```

**What to capture:**
- Formatted JSON output
- "overall_passed": true
- All checks listed with "passed": true

**Save as:** `screenshots/screenshot_09_quality_report.png`

---

### 📸 Screenshot 10: Pandas Profiling Report

```bash
# Copy report to local
docker cp $(docker-compose ps -q airflow-scheduler):/opt/airflow/reports/weather_data_$(docker-compose exec airflow-scheduler ls /opt/airflow/reports/ | head -1) ./profiling_report.html

# Open in browser
open profiling_report.html
```

**What to capture:**
- HTML profiling report in browser
- Overview section showing:
  - Number of variables
  - Number of observations
  - Missing cells
  - Variable types

**Save as:** `screenshots/screenshot_10_profiling_report.png`

---

### 📸 Screenshot 11: Transformation Logs

1. Click on `transform_data` task in Airflow
2. Click "Log" button

**What to capture:**
- "Creating time features..."
- "Creating lag features..."
- "Creating rolling features..."
- "Initial shape: (40, 20)"
- "Final shape: (38, 59)"
- "Total features: 59"

**Save as:** `screenshots/screenshot_11_transformation.png`

---

### 📸 Screenshot 12: Processed Data Sample

```bash
docker-compose exec airflow-scheduler head -10 /opt/airflow/data/processed/*.csv
```

**What to capture:**
- First 10 rows of processed data
- Many columns visible (59 total)
- Headers showing engineered features

**Save as:** `screenshots/screenshot_12_processed_data.png`

---

### 📸 Screenshot 13: MinIO Storage

1. Go back to MinIO console (http://localhost:9001)
2. Click on `mlops-data` bucket
3. Browse folders (processed_data/, dvc-storage/)

**What to capture:**
- Files uploaded to MinIO
- processed_data folder with CSV files

**Save as:** `screenshots/screenshot_13_minio_data.png`

---

### 📸 Screenshot 14: DVC Files

```bash
docker-compose exec airflow-scheduler ls -la /opt/airflow/data/processed/
```

**What to capture:**
- Directory listing showing:
  - .csv data files
  - .csv.dvc metadata files
  - File sizes and timestamps

**Save as:** `screenshots/screenshot_14_dvc_files.png`

---

### 📸 Screenshot 15: Complete DAG

**In Airflow UI:**
1. Go back to Graph view
2. Ensure all tasks are complete

**What to capture:**
- All 6 tasks showing GREEN (success)
- Complete pipeline execution
- No failed or running tasks

**Save as:** `screenshots/screenshot_15_complete_dag.png`

---

## 📊 PHASE 3: VERIFY RESULTS (10 minutes)

### Verification Commands

Run these to ensure everything worked:

```bash
# 1. Check data row count
docker-compose exec airflow-scheduler bash -c "wc -l /opt/airflow/data/raw/*.csv"
# Expected: ~41 lines (40 data + 1 header)

# 2. Count features
docker-compose exec airflow-scheduler bash -c "head -1 /opt/airflow/data/processed/*.csv | tr ',' '\n' | wc -l"
# Expected: 59

# 3. Verify MinIO objects
docker-compose exec airflow-scheduler python3 << 'EOF'
from minio import Minio
client = Minio('minio:9000', access_key='minioadmin', secret_key='minioadmin', secure=False)
objects = list(client.list_objects('mlops-data', recursive=True))
print(f"\n✅ MinIO has {len(objects)} objects stored\n")
for obj in objects[:5]:
    print(f"  • {obj.object_name}")
EOF

# 4. View quality summary
docker-compose exec airflow-scheduler python3 << 'EOF'
import json, glob
files = glob.glob('/opt/airflow/data/raw/*_quality_report.json')
if files:
    with open(files[0]) as f:
        r = json.load(f)
    print(f"\n✅ Quality: {r['passed_checks']}/{r['total_checks']} checks passed\n")
EOF
```

### Success Criteria

You should see:
- ✅ All Docker services running
- ✅ DAG completed with 6 green tasks
- ✅ Quality checks 5/5 passed
- ✅ 59 features generated
- ✅ Data in MinIO
- ✅ DVC files created
- ✅ 15 screenshots taken

---

## 📄 PHASE 4: GENERATE PDF (15 minutes)

### Option A: Using Local LaTeX

```bash
# Ensure screenshots are in place
ls screenshots/

# Compile PDF
pdflatex MLOps_Phase1_Report.tex
pdflatex MLOps_Phase1_Report.tex  # Run twice for table of contents

# Open PDF
open MLOps_Phase1_Report.pdf
```

### Option B: Using Overleaf (Recommended)

1. Go to https://www.overleaf.com/
2. Create account (free)
3. New Project → Upload Project
4. Upload:
   - `MLOps_Phase1_Report.tex`
   - All files from `screenshots/` folder
5. Click "Recompile"
6. Download PDF

### If Screenshots Missing

The LaTeX will compile with placeholders. You can:
1. Add missing screenshots later
2. Recompile to update

---

## 🎉 PHASE 5: COMPLETION

### Final Checklist

- [ ] All 15 screenshots taken and saved
- [ ] All verification commands run successfully
- [ ] PDF report generated
- [ ] Project files organized
- [ ] Services stopped (optional)

### Stop Services (Optional)

```bash
# Stop services
docker-compose down

# Or keep running for demo
```

---

## 📚 Additional Resources

### Documentation Files
- **README.md**: Overview and architecture
- **SETUP_AND_RUN.md**: Detailed setup guide
- **COMMANDS_REFERENCE.md**: Quick command reference
- **PROJECT_SUMMARY.md**: High-level summary

### Key Commands
```bash
# View logs
docker-compose logs -f airflow-scheduler

# Restart services
docker-compose restart

# Clean restart
docker-compose down -v
docker-compose up -d

# Access container shell
docker-compose exec airflow-scheduler bash
```

---

## 🐛 Troubleshooting

### Services Won't Start
```bash
docker-compose down -v
docker-compose up -d
```

### DAG Not Appearing
```bash
docker-compose restart airflow-scheduler
# Wait 30 seconds and refresh browser
```

### API Key Error
```bash
# Verify in container
docker-compose exec airflow-scheduler env | grep OPENWEATHER
# If missing, check .env file and restart
docker-compose restart
```

### Quality Check Failed
- Check API is responding
- Verify API key is valid
- Check data in raw/ folder

---

## 💡 Pro Tips

1. **Take Clear Screenshots**: Use full screen, good resolution
2. **Annotate if Needed**: Highlight important parts
3. **Keep Terminal Output**: Copy interesting outputs
4. **Document Issues**: Note any errors for report
5. **Test Before Demo**: Run through once completely

---

## ⏱️ Time Estimates

- Setup: 5 minutes
- Taking Screenshots: 30 minutes
- Verification: 10 minutes
- PDF Generation: 15 minutes
- **Total: ~60 minutes**

---

## 🎯 What You're Demonstrating

This project shows:

1. ✅ **MLOps Pipeline**: End-to-end automated workflow
2. ✅ **Data Engineering**: ETL with quality gates
3. ✅ **Feature Engineering**: Time-series features
4. ✅ **Orchestration**: Airflow DAG management
5. ✅ **Versioning**: DVC data version control
6. ✅ **Storage**: Object storage (S3-compatible)
7. ✅ **Tracking**: MLflow experiment tracking
8. ✅ **Containerization**: Docker deployment
9. ✅ **Documentation**: Professional LaTeX report

---

## 🚀 Ready to Start?

```bash
cd /Users/abdurrehmansubhani/Desktop/Abdullah/MLOps-Project
./quickstart.sh
```

Then follow this guide step by step!

**Good luck! 🎉**

---

## 📞 Need Help?

Refer to:
- **SETUP_AND_RUN.md**: Detailed instructions
- **COMMANDS_REFERENCE.md**: Command quick reference
- **README.md**: Technical documentation

Or check:
- Airflow logs: `docker-compose logs airflow-scheduler`
- Task logs: In Airflow UI → Click task → Log
- Docker status: `docker-compose ps`

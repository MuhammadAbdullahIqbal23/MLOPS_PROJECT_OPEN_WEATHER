# 🚀 Getting Started - MLOps Weather Pipeline

Welcome! This guide will help you navigate the documentation and get the pipeline running.

## 📚 Documentation Structure

This project has comprehensive documentation organized as follows:

### 🏃 Quick Setup (Start Here!)
**File**: [`QUICKSTART.md`](QUICKSTART.md)
- ⏱️ **10-minute setup** from zero to running pipeline
- Step-by-step commands
- Verification steps
- Perfect for first-time users

### 📋 Complete Command Reference
**File**: [`AIRFLOW_COMMANDS_SCREENSHOTS.md`](AIRFLOW_COMMANDS_SCREENSHOTS.md)
- **68 detailed steps** with commands
- Every command needed for full setup
- Screenshot requirements for each step
- Troubleshooting scenarios
- Quality gate failure demonstrations
- Use this for complete documentation

### 📊 Implementation Summary
**File**: [`PHASE1_IMPLEMENTATION_SUMMARY.md`](PHASE1_IMPLEMENTATION_SUMMARY.md)
- Architecture overview
- Requirements mapping
- Technology stack
- Key features
- Success metrics
- Use this to understand what was built

### 📸 Screenshots Guide
**Folder**: [`screenshots/`](screenshots/)
**File**: [`screenshots/README.md`](screenshots/README.md)
- Organized folder structure
- Naming conventions
- Quality guidelines
- **95+ screenshots** to capture
- Categories: Airflow, Storage, MLflow, Quality

---

## 🎯 Choose Your Path

### Path 1: I Want to Run It NOW! 🏃‍♂️
1. Read [`QUICKSTART.md`](QUICKSTART.md) (5 min)
2. Follow the 6 steps (10 min)
3. Watch your pipeline run! ✅

**Time**: 15 minutes

### Path 2: I Want Complete Documentation 📚
1. Read [`PHASE1_IMPLEMENTATION_SUMMARY.md`](PHASE1_IMPLEMENTATION_SUMMARY.md) (15 min)
2. Follow [`AIRFLOW_COMMANDS_SCREENSHOTS.md`](AIRFLOW_COMMANDS_SCREENSHOTS.md) (60 min)
3. Capture all screenshots (60 min)
4. Have a production-ready documented system ✅

**Time**: 2-3 hours

### Path 3: I Want to Understand the Code 💻
1. Read [`PHASE1_IMPLEMENTATION_SUMMARY.md`](PHASE1_IMPLEMENTATION_SUMMARY.md)
2. Explore the codebase:
   - [`dags/weather_pipeline_dag.py`](dags/weather_pipeline_dag.py) - Orchestration
   - [`src/data_extraction.py`](src/data_extraction.py) - API fetching
   - [`src/data_quality.py`](src/data_quality.py) - Quality gates
   - [`src/data_transformation.py`](src/data_transformation.py) - Feature engineering
   - [`src/storage_versioning.py`](src/storage_versioning.py) - MinIO + DVC
   - [`src/mlflow_integration.py`](src/mlflow_integration.py) - Experiment tracking
3. Run components individually for testing

**Time**: 1-2 hours

---

## 🏗️ What You'll Build

A complete MLOps pipeline that:

```
┌─────────────────────────────────────────────────────────┐
│                  Daily at Midnight                       │
│                 (Apache Airflow)                         │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────┐
        │   1. Extract Weather Data       │
        │   (OpenWeatherMap API)          │
        └─────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────┐
        │   2. Quality Gate ⚠️             │
        │   • Check nulls (<1%)           │
        │   • Validate schema             │
        │   • STOP if fails!              │
        └─────────────────────────────────┘
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
┌──────────────────────┐     ┌──────────────────────┐
│  3a. Profile Data    │     │  3b. Transform Data  │
│  (Pandas Profiling)  │     │  (Feature Eng.)      │
│  → Log to MLflow     │     │  • Lag features      │
└──────────────────────┘     │  • Rolling stats     │
          │                  │  • Time features     │
          │                  └──────────────────────┘
          │                               │
          └───────────────┬───────────────┘
                          ▼
        ┌─────────────────────────────────┐
        │   4. Store & Version            │
        │   • Upload to MinIO             │
        │   • Version with DVC            │
        │   • Commit .dvc to Git          │
        └─────────────────────────────────┘
                          │
                          ▼
                    ✅ SUCCESS!
```

---

## 🛠️ Prerequisites Checklist

Before you start, ensure you have:

- [ ] **Python 3.8+** installed
  ```bash
  python --version  # Should show 3.8 or higher
  ```

- [ ] **Docker Desktop** installed and running
  ```bash
  docker --version
  docker ps  # Should not error
  ```

- [ ] **Git** installed
  ```bash
  git --version
  ```

- [ ] **OpenWeatherMap API Key** (free)
  - Sign up at: https://openweathermap.org/api
  - Get your API key from: https://home.openweathermap.org/api_keys
  - Free tier: 1000 calls/day, 60 calls/minute

- [ ] **Sufficient disk space**: ~5GB
  - Docker images: ~2GB
  - Python packages: ~1GB
  - Data and logs: ~1GB
  - Buffer: ~1GB

---

## 🚦 Quick Start (5 Commands)

If you want to skip reading and just run:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure (add your API key)
echo "OPENWEATHER_API_KEY=your_key_here" >> .env

# 3. Start MinIO
docker run -d --name minio -p 9000:9000 -p 9001:9001 \
  -e "MINIO_ROOT_USER=minioadmin" -e "MINIO_ROOT_PASSWORD=minioadmin" \
  quay.io/minio/minio server /data --console-address ":9001"

# 4. Initialize and start Airflow
export AIRFLOW_HOME=$(pwd)
airflow db init
airflow users create --username admin --password admin \
  --firstname Admin --lastname User --role Admin --email admin@example.com

# 5. Start Airflow (in two terminals)
# Terminal 1:
airflow webserver --port 8080
# Terminal 2:
airflow scheduler
```

Then open http://localhost:8080 and trigger the DAG!

---

## 📖 Detailed Guides

### For Installation
👉 [`QUICKSTART.md`](QUICKSTART.md)
- Complete installation steps
- Service configuration
- First pipeline run
- Verification commands

### For Screenshots & Documentation
👉 [`AIRFLOW_COMMANDS_SCREENSHOTS.md`](AIRFLOW_COMMANDS_SCREENSHOTS.md)
- 68 commands with descriptions
- Screenshot requirements
- Failure scenarios
- Troubleshooting

### For Understanding the System
👉 [`PHASE1_IMPLEMENTATION_SUMMARY.md`](PHASE1_IMPLEMENTATION_SUMMARY.md)
- Architecture deep-dive
- Technology choices
- Feature explanations
- Success criteria

### For Code Structure
👉 Browse the [`src/`](src/) directory
```
src/
├── data_extraction.py       # Fetch from API
├── data_quality.py          # Validate quality
├── data_transformation.py   # Engineer features
├── mlflow_integration.py    # Track experiments
└── storage_versioning.py    # Store & version
```

---

## 🎓 Learning Path

### Day 1: Setup & Run (2 hours)
1. ✅ Read QUICKSTART.md
2. ✅ Install all services
3. ✅ Run first pipeline
4. ✅ Verify all components

### Day 2: Deep Dive (3 hours)
1. ✅ Read PHASE1_IMPLEMENTATION_SUMMARY.md
2. ✅ Explore each Python module
3. ✅ Understand the DAG structure
4. ✅ Review quality checks

### Day 3: Documentation (2 hours)
1. ✅ Follow AIRFLOW_COMMANDS_SCREENSHOTS.md
2. ✅ Capture all screenshots
3. ✅ Test failure scenarios
4. ✅ Complete documentation

---

## 🔍 Key Concepts

### Apache Airflow
- **DAG**: Directed Acyclic Graph - your pipeline workflow
- **Task**: Individual step in the pipeline
- **Scheduler**: Runs DAGs on schedule
- **Webserver**: UI for monitoring

### Data Version Control (DVC)
- **Lightweight**: Only metadata in Git
- **Large files**: Stored in MinIO
- **Versioning**: Track data changes over time
- **Reproducibility**: Recreate any dataset version

### MinIO
- **S3-compatible**: Works like AWS S3
- **Self-hosted**: Run locally or in cloud
- **Bucket**: Container for objects
- **Object**: Individual file

### MLflow
- **Experiments**: Group related runs
- **Runs**: Individual pipeline executions
- **Parameters**: Configuration values
- **Metrics**: Numeric measurements
- **Artifacts**: Files (reports, models)

---

## 🆘 Need Help?

### Documentation Issues
- Check [`AIRFLOW_COMMANDS_SCREENSHOTS.md`](AIRFLOW_COMMANDS_SCREENSHOTS.md) troubleshooting section
- Review [`QUICKSTART.md`](QUICKSTART.md) "Need Help?" section

### Service Issues
```bash
# Check if services are running
docker ps                          # MinIO should be listed
ps aux | grep airflow              # Airflow processes
lsof -i :8080,9000,9001           # Check ports
```

### Code Issues
```bash
# Test individual components
python src/data_extraction.py      # Test extraction
python src/data_quality.py         # Test quality checks
python src/data_transformation.py  # Test transformation
```

### DAG Issues
```bash
# Check DAG syntax
python dags/weather_pipeline_dag.py

# Check for import errors
airflow dags list-import-errors

# Test specific task
airflow tasks test weather_prediction_pipeline extract_data 2025-12-01
```

---

## 📦 What's Included

### Source Code (5 modules)
- ✅ Data extraction from API
- ✅ Quality validation (5 checks)
- ✅ Feature engineering (15+ features)
- ✅ MinIO storage integration
- ✅ DVC versioning
- ✅ MLflow tracking
- ✅ Airflow orchestration

### Documentation (4 guides)
- ✅ Quick start guide
- ✅ Complete command reference (68 steps)
- ✅ Implementation summary
- ✅ Screenshot guidelines

### Infrastructure (3 services)
- ✅ Apache Airflow
- ✅ MinIO (S3-compatible storage)
- ✅ MLflow (optional DagsHub integration)

---

## 🎯 Success Criteria

You're successful when:

- [ ] MinIO console accessible at http://localhost:9001
- [ ] Airflow UI accessible at http://localhost:8080
- [ ] DAG `weather_prediction_pipeline` visible in Airflow
- [ ] DAG run completes successfully (all tasks green)
- [ ] Raw data saved in `data/raw/`
- [ ] Processed data saved in `data/processed/`
- [ ] `.dvc` files created
- [ ] Data visible in MinIO bucket
- [ ] Profile report in `reports/`
- [ ] All quality checks passing

---

## 🚀 Next Steps After Setup

### Immediate
1. ✅ Trigger the DAG manually
2. ✅ Monitor task execution
3. ✅ Review generated reports
4. ✅ Check MinIO storage

### Short-term
1. ✅ Capture all screenshots
2. ✅ Test failure scenarios
3. ✅ Customize for your cities
4. ✅ Adjust quality thresholds

### Long-term (Phase 2)
1. 🔄 Train forecasting model
2. 🔄 Deploy model endpoint
3. 🔄 Set up monitoring
4. 🔄 Implement CI/CD

---

## 📞 Project Info

- **Phase**: 1 of 3 (ETL & Orchestration)
- **Status**: ✅ Complete
- **Technology**: Apache Airflow + DVC + MLflow
- **Data Source**: OpenWeatherMap API
- **Schedule**: Daily

---

## 🏆 What You'll Learn

By completing this project, you'll understand:

1. **MLOps Fundamentals**
   - Pipeline orchestration
   - Data versioning
   - Experiment tracking
   - Quality gates

2. **Apache Airflow**
   - DAG creation
   - Task dependencies
   - Scheduling
   - Monitoring

3. **Data Engineering**
   - API integration
   - ETL pipelines
   - Feature engineering
   - Data validation

4. **Production Skills**
   - Error handling
   - Logging
   - Configuration management
   - Documentation

---

## 📝 Quick Reference

| What | Where | URL |
|------|-------|-----|
| Airflow UI | Browser | http://localhost:8080 |
| MinIO Console | Browser | http://localhost:9001 |
| MLflow UI | Browser | http://localhost:5000 |
| DAG Code | VS Code | `dags/weather_pipeline_dag.py` |
| Source Code | VS Code | `src/*.py` |
| Data | Finder | `data/raw/` & `data/processed/` |
| Reports | Browser | `reports/*.html` |

---

## ✨ Ready to Start?

Choose your path and dive in! 🚀

1. 🏃 **Quick Start**: [`QUICKSTART.md`](QUICKSTART.md)
2. 📚 **Complete Guide**: [`AIRFLOW_COMMANDS_SCREENSHOTS.md`](AIRFLOW_COMMANDS_SCREENSHOTS.md)
3. 📊 **Understanding**: [`PHASE1_IMPLEMENTATION_SUMMARY.md`](PHASE1_IMPLEMENTATION_SUMMARY.md)

**Happy Learning! 🎓**

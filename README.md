# Real-Time Weather Prediction MLOps Pipeline

## Overview
This project implements a complete MLOps pipeline for real-time weather prediction using Apache Airflow, MLflow, DVC, and MinIO. The pipeline automatically fetches weather data from OpenWeatherMap API, performs quality checks, feature engineering, and versions the data for model training.

## Architecture

### Components
1. **Data Source**: OpenWeatherMap API (Environmental Domain)
2. **Orchestration**: Apache Airflow (DAG-based workflow)
3. **Storage**: MinIO (S3-compatible object storage)
4. **Version Control**: DVC (Data Version Control)
5. **Experiment Tracking**: MLflow with DagsHub integration
6. **Data Quality**: Automated quality gates with Pandas Profiling

### Pipeline Stages
1. **Extraction**: Fetch live weather data from API
2. **Quality Check**: Validate data (>1% null threshold, schema validation)
3. **Profiling**: Generate data quality report with Pandas Profiling
4. **Transformation**: Feature engineering (lag features, rolling windows, time encodings)
5. **Loading**: Store in MinIO and version with DVC

## Prerequisites

- Docker and Docker Compose
- Python 3.11+
- OpenWeatherMap API key (free tier)
- Git

## Setup Instructions

### Step 1: Clone and Configure

```bash
# Navigate to project directory
cd /Users/abdurrehmansubhani/Desktop/Abdullah/MLOps-Project

# Copy environment template
cp .env.example .env
```

### Step 2: Configure Environment Variables

Edit `.env` file with your credentials:

```bash
# OpenWeatherMap API Configuration
OPENWEATHER_API_KEY=your_actual_api_key_here
OPENWEATHER_CITY=London
OPENWEATHER_LAT=51.5074
OPENWEATHER_LON=-0.1278

# MLflow and DagsHub Configuration (optional)
MLFLOW_TRACKING_URI=https://dagshub.com/your_username/MLOps-Project.mlflow
DAGSHUB_USERNAME=your_username
DAGSHUB_TOKEN=your_token

# MinIO Configuration (defaults work)
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=mlops-data
```

### Step 3: Start Services

```bash
# Start Airflow and MinIO with Docker Compose
docker-compose up -d

# Wait for services to be ready (2-3 minutes)
# Check status
docker-compose ps
```

### Step 4: Access Services

- **Airflow UI**: http://localhost:8080
  - Username: `admin`
  - Password: `admin`

- **MinIO Console**: http://localhost:9001
  - Username: `minioadmin`
  - Password: `minioadmin`

### Step 5: Initialize Git and DVC

```bash
# Initialize git repository (if not already done)
git init
git add .gitignore README.md requirements.txt

# DVC will be initialized automatically by the pipeline
# But you can also initialize manually inside the container:
docker-compose exec airflow-scheduler bash
cd /opt/airflow
dvc init
git add .dvc/config .dvc/.gitignore
exit
```

### Step 6: Run the Pipeline

1. Open Airflow UI at http://localhost:8080
2. Find the DAG named `weather_prediction_pipeline`
3. Toggle the DAG to "ON" (unpause)
4. Click "Trigger DAG" to run manually

## Running Commands and Taking Screenshots

### Screenshot 1: Docker Services Running
```bash
docker-compose ps
```
**Screenshot**: Take screenshot showing all services (airflow-webserver, airflow-scheduler, minio) running

### Screenshot 2: Airflow DAG List
**Screenshot**: Open http://localhost:8080, show the weather_prediction_pipeline DAG in the list

### Screenshot 3: DAG Graph View
**Screenshot**: Click on the DAG, navigate to "Graph" view showing all tasks and dependencies

### Screenshot 4: MinIO Bucket Created
**Screenshot**: Open http://localhost:9001, show the mlops-data bucket

### Screenshot 5: Trigger DAG Run
**Screenshot**: Click "Trigger DAG" button in Airflow UI

### Screenshot 6: DAG Run Progress
**Screenshot**: Show the DAG running with tasks in progress (green/yellow indicators)

### Screenshot 7: Task Logs - Data Extraction
**Screenshot**: Click on "extract_data" task, show logs with API call and data saved

### Screenshot 8: Task Logs - Quality Check
**Screenshot**: Click on "quality_check" task, show quality report with all checks passed

### Screenshot 9: Data Quality Report JSON
```bash
# View quality report
docker-compose exec airflow-scheduler ls -lh /opt/airflow/data/raw/
docker-compose exec airflow-scheduler cat /opt/airflow/data/raw/*_quality_report.json
```
**Screenshot**: Show the quality report JSON content

### Screenshot 10: Pandas Profiling Report
**Screenshot**: Open the generated HTML report from reports/ directory in a browser

### Screenshot 11: Task Logs - Feature Engineering
**Screenshot**: Click on "transform_data" task, show transformation logs with feature counts

### Screenshot 12: Processed Data Sample
```bash
# View processed data
docker-compose exec airflow-scheduler head -20 /opt/airflow/data/processed/*.csv
```
**Screenshot**: Show the processed CSV with engineered features

### Screenshot 13: MinIO Data Uploaded
**Screenshot**: In MinIO console, show the processed_data folder with uploaded files

### Screenshot 14: DVC Files Generated
```bash
docker-compose exec airflow-scheduler ls -la /opt/airflow/data/processed/
```
**Screenshot**: Show .dvc files created for version control

### Screenshot 15: Complete DAG Run
**Screenshot**: Show completed DAG with all tasks green (success)

## Verification Commands

### Check Data Extraction
```bash
# List raw data files
docker-compose exec airflow-scheduler ls -lh /opt/airflow/data/raw/

# View first few rows
docker-compose exec airflow-scheduler head /opt/airflow/data/raw/weather_data_*.csv
```

### Check Data Quality Reports
```bash
# List quality reports
docker-compose exec airflow-scheduler ls -lh /opt/airflow/data/raw/*_quality_report.json

# View report
docker-compose exec airflow-scheduler cat /opt/airflow/data/raw/*_quality_report.json | python3 -m json.tool
```

### Check Transformed Data
```bash
# List processed files
docker-compose exec airflow-scheduler ls -lh /opt/airflow/data/processed/

# Check feature count
docker-compose exec airflow-scheduler head -1 /opt/airflow/data/processed/*.csv | tr ',' '\n' | wc -l
```

### Check MinIO Storage
```bash
# List MinIO objects
docker-compose exec airflow-scheduler python3 -c "
from minio import Minio
client = Minio('minio:9000', access_key='minioadmin', secret_key='minioadmin', secure=False)
objects = client.list_objects('mlops-data', recursive=True)
for obj in objects:
    print(f'{obj.object_name} - {obj.size} bytes')
"
```

### Check DVC Status
```bash
docker-compose exec airflow-scheduler bash -c "cd /opt/airflow && dvc status"
```

## Pipeline Features

### Data Quality Checks (Mandatory Gate)
- **Null Value Check**: Fails if >1% null values in any column
- **Schema Validation**: Ensures all expected columns are present
- **Data Type Validation**: Verifies numeric columns are numeric
- **Value Range Check**: Validates values are within expected ranges
- **Row Count Check**: Ensures minimum data volume

### Feature Engineering
- **Time Features**: Hour, day of week, month, cyclical encodings
- **Lag Features**: Previous 1, 2, 3, 6 time steps
- **Rolling Features**: Mean, std, min, max over 3, 6, 12 windows
- **Weather Features**: Temperature range, comfort index, wind chill
- **Target Variable**: Temperature 6 hours ahead

### Data Versioning (DVC)
- Automatic versioning of processed datasets
- Remote storage in MinIO (S3-compatible)
- Git-tracked .dvc metadata files
- Full reproducibility of data pipelines

## Troubleshooting

### Services Not Starting
```bash
# Check logs
docker-compose logs airflow-webserver
docker-compose logs minio

# Restart services
docker-compose down
docker-compose up -d
```

### API Key Issues
```bash
# Verify API key in container
docker-compose exec airflow-scheduler env | grep OPENWEATHER
```

### MinIO Connection Issues
```bash
# Check MinIO health
curl http://localhost:9000/minio/health/live

# Recreate bucket
docker-compose exec airflow-scheduler python3 -c "
from minio import Minio
client = Minio('minio:9000', access_key='minioadmin', secret_key='minioadmin', secure=False)
if not client.bucket_exists('mlops-data'):
    client.make_bucket('mlops-data')
    print('Bucket created')
"
```

## Project Structure
```
MLOps-Project/
├── dags/
│   └── weather_pipeline_dag.py      # Main Airflow DAG
├── src/
│   ├── data_extraction.py           # API data fetching
│   ├── data_quality.py              # Quality checks
│   ├── data_transformation.py       # Feature engineering
│   ├── mlflow_integration.py        # MLflow tracking
│   └── storage_versioning.py        # MinIO and DVC
├── data/
│   ├── raw/                         # Raw API data
│   └── processed/                   # Transformed data
├── reports/                         # Pandas Profiling reports
├── docker-compose.yml               # Service definitions
├── requirements.txt                 # Python dependencies
└── .env                            # Environment configuration
```

## Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

## Next Steps

1. **Model Training**: Add model training task to DAG
2. **Concept Drift Detection**: Implement drift monitoring
3. **Model Serving**: Deploy model with FastAPI
4. **Monitoring Dashboard**: Create Grafana dashboards
5. **CI/CD**: Add GitHub Actions for automation

## License
MIT License

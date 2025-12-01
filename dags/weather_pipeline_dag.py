"""
Weather Prediction MLOps Pipeline DAG
Complete ETL pipeline with quality gates, feature engineering, and versioning
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.exceptions import AirflowException
import sys
import os

# Add src to path
sys.path.insert(0, '/opt/airflow/src')

from data_extraction import WeatherDataExtractor
from data_quality import validate_data_quality
from data_transformation import WeatherFeatureEngineering
from mlflow_integration import generate_and_log_profile
from storage_versioning import setup_storage_and_versioning


# Expected columns for quality check
EXPECTED_COLUMNS = [
    'collection_timestamp', 'forecast_timestamp', 'city', 'latitude', 'longitude',
    'temperature', 'feels_like', 'temp_min', 'temp_max', 'pressure', 'humidity',
    'weather_main', 'weather_description', 'clouds', 'wind_speed', 'wind_deg',
    'visibility', 'pop', 'rain_3h', 'snow_3h'
]

# Default arguments for the DAG
default_args = {
    'owner': 'mlops-team',
    'depends_on_past': False,
    'start_date': datetime(2025, 12, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Create DAG
dag = DAG(
    'weather_prediction_pipeline',
    default_args=default_args,
    description='Real-time weather prediction MLOps pipeline',
    schedule_interval='@daily',  # Run daily
    catchup=False,
    tags=['mlops', 'weather', 'etl', 'ml'],
)


def extract_weather_data(**context):
    """Task 1: Extract data from OpenWeatherMap API"""
    print("="*50)
    print("TASK 1: DATA EXTRACTION")
    print("="*50)
    
    extractor = WeatherDataExtractor()
    output_path = '/opt/airflow/data/raw'
    
    # Extract and save
    filepath = extractor.extract_and_save(output_path)
    
    # Push filepath to XCom for next tasks
    context['ti'].xcom_push(key='raw_data_filepath', value=filepath)
    
    print(f"✓ Data extraction complete: {filepath}")
    return filepath


def quality_check_data(**context):
    """Task 2: Perform mandatory data quality checks"""
    print("="*50)
    print("TASK 2: DATA QUALITY CHECKS")
    print("="*50)
    
    # Get filepath from previous task
    ti = context['ti']
    filepath = ti.xcom_pull(task_ids='extract_data', key='raw_data_filepath')
    
    if not filepath:
        raise AirflowException("No data filepath received from extraction task")
    
    # Run quality checks
    passed = validate_data_quality(filepath, EXPECTED_COLUMNS)
    
    if not passed:
        raise AirflowException("Data quality checks FAILED! Pipeline stopped.")
    
    print("✓ All data quality checks PASSED")
    return True


def generate_data_profile(**context):
    """Task 3: Generate Pandas Profiling report and log to MLflow"""
    print("="*50)
    print("TASK 3: DATA PROFILING")
    print("="*50)
    
    # Get filepath from extraction task
    ti = context['ti']
    filepath = ti.xcom_pull(task_ids='extract_data', key='raw_data_filepath')
    
    # Generate and log profile
    report_path = generate_and_log_profile(filepath, report_dir='/opt/airflow/reports')
    
    print(f"✓ Data profile generated and logged: {report_path}")
    return report_path


def transform_data(**context):
    """Task 4: Transform data with feature engineering"""
    print("="*50)
    print("TASK 4: DATA TRANSFORMATION")
    print("="*50)
    
    # Get filepath from extraction task
    ti = context['ti']
    raw_filepath = ti.xcom_pull(task_ids='extract_data', key='raw_data_filepath')
    
    # Create output filepath
    filename = os.path.basename(raw_filepath).replace('.csv', '_processed.csv')
    processed_filepath = os.path.join('/opt/airflow/data/processed', filename)
    
    # Transform data
    transformer = WeatherFeatureEngineering()
    output_path = transformer.transform(raw_filepath, processed_filepath)
    
    # Push to XCom
    ti.xcom_push(key='processed_data_filepath', value=output_path)
    
    print(f"✓ Data transformation complete: {output_path}")
    return output_path


def load_and_version_data(**context):
    """Task 5: Load to MinIO and version with DVC"""
    print("="*50)
    print("TASK 5: DATA LOADING AND VERSIONING")
    print("="*50)
    
    # Get filepath from transformation task
    ti = context['ti']
    processed_filepath = ti.xcom_pull(task_ids='transform_data', key='processed_data_filepath')
    
    # Setup storage and versioning
    setup_storage_and_versioning(processed_filepath)
    
    print("✓ Data loaded to MinIO and versioned with DVC")
    return True


def log_pipeline_completion(**context):
    """Task 6: Log pipeline completion"""
    print("="*50)
    print("PIPELINE COMPLETION")
    print("="*50)
    
    ti = context['ti']
    raw_filepath = ti.xcom_pull(task_ids='extract_data', key='raw_data_filepath')
    processed_filepath = ti.xcom_pull(task_ids='transform_data', key='processed_data_filepath')
    
    print(f"Raw data: {raw_filepath}")
    print(f"Processed data: {processed_filepath}")
    print("✓ Weather prediction pipeline completed successfully!")
    
    return {
        'status': 'success',
        'raw_data': raw_filepath,
        'processed_data': processed_filepath,
        'timestamp': datetime.now().isoformat()
    }


# Define tasks
task_extract = PythonOperator(
    task_id='extract_data',
    python_callable=extract_weather_data,
    dag=dag,
)

task_quality_check = PythonOperator(
    task_id='quality_check',
    python_callable=quality_check_data,
    dag=dag,
)

task_data_profile = PythonOperator(
    task_id='generate_data_profile',
    python_callable=generate_data_profile,
    dag=dag,
)

task_transform = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    dag=dag,
)

task_load = PythonOperator(
    task_id='load_and_version',
    python_callable=load_and_version_data,
    dag=dag,
)

task_complete = PythonOperator(
    task_id='log_completion',
    python_callable=log_pipeline_completion,
    dag=dag,
)

# Define task dependencies
# Extract -> Quality Check -> [Data Profile, Transform] -> Load -> Complete
task_extract >> task_quality_check
task_quality_check >> [task_data_profile, task_transform]
[task_data_profile, task_transform] >> task_load
task_load >> task_complete

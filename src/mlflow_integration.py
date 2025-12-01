"""
MLflow Integration Module
Handles experiment tracking and artifact logging
"""
import os
import mlflow
import dagshub
from ydata_profiling import ProfileReport
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


class MLflowTracker:
    """MLflow tracking with DagsHub integration"""
    
    def __init__(self):
        self.tracking_uri = os.getenv('MLFLOW_TRACKING_URI')
        self.dagshub_username = os.getenv('DAGSHUB_USERNAME')
        self.dagshub_token = os.getenv('DAGSHUB_TOKEN')
        
        # Initialize DagsHub (optional if using DagsHub)
        if self.dagshub_username and self.dagshub_token:
            try:
                dagshub.init(repo_owner=self.dagshub_username, 
                            repo_name='MLOps-Project',
                            mlflow=True)
                print("DagsHub initialized successfully")
            except Exception as e:
                print(f"DagsHub initialization skipped: {e}")
        
        # Set MLflow tracking URI
        if self.tracking_uri:
            mlflow.set_tracking_uri(self.tracking_uri)
        else:
            # Use local tracking
            mlflow.set_tracking_uri("file:./mlruns")
        
        print(f"MLflow tracking URI: {mlflow.get_tracking_uri()}")
    
    def create_data_profile(self, data_filepath: str, output_path: str) -> str:
        """
        Generate Pandas Profiling report
        
        Args:
            data_filepath: Path to CSV file
            output_path: Directory to save report
            
        Returns:
            Path to generated report
        """
        print(f"Loading data from {data_filepath}")
        df = pd.read_csv(data_filepath)
        
        print("Generating data profile report...")
        profile = ProfileReport(df, 
                               title="Weather Data Quality Report",
                               explorative=True,
                               minimal=False)
        
        # Save report
        os.makedirs(output_path, exist_ok=True)
        report_filename = os.path.basename(data_filepath).replace('.csv', '_profile.html')
        report_path = os.path.join(output_path, report_filename)
        
        profile.to_file(report_path)
        print(f"Profile report saved to: {report_path}")
        
        return report_path
    
    def log_data_profile(self, data_filepath: str, report_path: str, 
                        experiment_name: str = "weather_prediction_pipeline"):
        """
        Log data profile to MLflow
        
        Args:
            data_filepath: Path to data CSV
            report_path: Path to profile report HTML
            experiment_name: MLflow experiment name
        """
        mlflow.set_experiment(experiment_name)
        
        with mlflow.start_run(run_name="data_profiling"):
            # Load data for metrics
            df = pd.read_csv(data_filepath)
            
            # Log parameters
            mlflow.log_param("data_source", os.path.basename(data_filepath))
            mlflow.log_param("num_rows", len(df))
            mlflow.log_param("num_columns", len(df.columns))
            
            # Log metrics
            mlflow.log_metric("data_shape_rows", len(df))
            mlflow.log_metric("data_shape_cols", len(df.columns))
            mlflow.log_metric("null_count_total", df.isnull().sum().sum())
            mlflow.log_metric("null_percentage", (df.isnull().sum().sum() / df.size) * 100)
            
            # Log numerical statistics
            numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
            for col in numeric_cols[:10]:  # Log first 10 numeric columns
                mlflow.log_metric(f"{col}_mean", df[col].mean())
                mlflow.log_metric(f"{col}_std", df[col].std())
            
            # Log artifact (profile report)
            mlflow.log_artifact(report_path, artifact_path="data_profiles")
            
            # Log data file itself
            mlflow.log_artifact(data_filepath, artifact_path="data")
            
            print(f"✓ Data profile logged to MLflow experiment: {experiment_name}")
            print(f"  Run ID: {mlflow.active_run().info.run_id}")
    
    def log_pipeline_run(self, stage: str, metrics: dict, artifacts: dict = None,
                        experiment_name: str = "weather_prediction_pipeline"):
        """
        Log pipeline stage execution
        
        Args:
            stage: Pipeline stage name (extraction, transformation, etc.)
            metrics: Dictionary of metrics to log
            artifacts: Dictionary of artifact paths to log
            experiment_name: MLflow experiment name
        """
        mlflow.set_experiment(experiment_name)
        
        with mlflow.start_run(run_name=f"pipeline_{stage}"):
            # Log stage
            mlflow.log_param("stage", stage)
            
            # Log metrics
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    mlflow.log_metric(key, value)
                else:
                    mlflow.log_param(key, str(value))
            
            # Log artifacts
            if artifacts:
                for artifact_name, artifact_path in artifacts.items():
                    if os.path.exists(artifact_path):
                        mlflow.log_artifact(artifact_path, artifact_path=f"{stage}_artifacts")
            
            print(f"✓ Pipeline stage '{stage}' logged to MLflow")


def generate_and_log_profile(data_filepath: str, report_dir: str = "/opt/airflow/reports"):
    """
    Main function to generate and log data profile
    
    Args:
        data_filepath: Path to data CSV
        report_dir: Directory to save report
    """
    tracker = MLflowTracker()
    
    # Generate profile
    report_path = tracker.create_data_profile(data_filepath, report_dir)
    
    # Log to MLflow
    tracker.log_data_profile(data_filepath, report_path)
    
    return report_path


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        data_path = sys.argv[1]
        generate_and_log_profile(data_path)
    else:
        print("Usage: python mlflow_integration.py <data_filepath>")

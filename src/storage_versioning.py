"""
Storage and Versioning Module
Handles MinIO storage and DVC versioning
"""
import os
from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv
import subprocess
import shutil

load_dotenv()


class MinIOStorage:
    """MinIO object storage client"""
    
    def __init__(self):
        self.endpoint = os.getenv('MINIO_ENDPOINT', 'localhost:9000')
        self.access_key = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
        self.secret_key = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
        self.bucket_name = os.getenv('MINIO_BUCKET', 'mlops-data')
        
        # Initialize MinIO client
        self.client = Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=False  # Set to True if using HTTPS
        )
        
        # Create bucket if it doesn't exist
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                print(f"✓ Created MinIO bucket: {self.bucket_name}")
            else:
                print(f"✓ MinIO bucket exists: {self.bucket_name}")
        except S3Error as e:
            print(f"Error creating bucket: {e}")
            raise
    
    def upload_file(self, file_path: str, object_name: str = None):
        """
        Upload file to MinIO
        
        Args:
            file_path: Local file path
            object_name: Object name in bucket (defaults to filename)
        """
        if object_name is None:
            object_name = os.path.basename(file_path)
        
        try:
            self.client.fput_object(
                self.bucket_name,
                object_name,
                file_path
            )
            print(f"✓ Uploaded {file_path} to {self.bucket_name}/{object_name}")
        except S3Error as e:
            print(f"Error uploading file: {e}")
            raise
    
    def download_file(self, object_name: str, file_path: str):
        """
        Download file from MinIO
        
        Args:
            object_name: Object name in bucket
            file_path: Local file path to save
        """
        try:
            self.client.fget_object(
                self.bucket_name,
                object_name,
                file_path
            )
            print(f"✓ Downloaded {object_name} to {file_path}")
        except S3Error as e:
            print(f"Error downloading file: {e}")
            raise
    
    def list_objects(self, prefix: str = None):
        """List objects in bucket"""
        try:
            objects = self.client.list_objects(self.bucket_name, prefix=prefix)
            return [obj.object_name for obj in objects]
        except S3Error as e:
            print(f"Error listing objects: {e}")
            raise


class DVCManager:
    """DVC (Data Version Control) manager"""
    
    def __init__(self, repo_path: str = "/opt/airflow"):
        self.repo_path = repo_path
    
    def init_dvc(self):
        """Initialize DVC in repository"""
        try:
            # Check if DVC is already initialized
            dvc_dir = os.path.join(self.repo_path, '.dvc')
            if os.path.exists(dvc_dir):
                print("✓ DVC already initialized")
                return
            
            # Initialize DVC
            result = subprocess.run(
                ['dvc', 'init'],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✓ DVC initialized successfully")
            else:
                print(f"DVC init output: {result.stdout}")
                print(f"DVC init error: {result.stderr}")
        except Exception as e:
            print(f"Error initializing DVC: {e}")
    
    def configure_remote(self, remote_name: str = 'minio'):
        """Configure DVC remote storage (MinIO/S3)"""
        try:
            endpoint = os.getenv('MINIO_ENDPOINT', 'localhost:9000')
            access_key = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
            secret_key = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
            bucket = os.getenv('MINIO_BUCKET', 'mlops-data')
            
            # Set remote URL
            remote_url = f"s3://{bucket}/dvc-storage"
            
            commands = [
                ['dvc', 'remote', 'add', '-d', remote_name, remote_url],
                ['dvc', 'remote', 'modify', remote_name, 'endpointurl', f'http://{endpoint}'],
                ['dvc', 'remote', 'modify', remote_name, 'access_key_id', access_key],
                ['dvc', 'remote', 'modify', remote_name, 'secret_access_key', secret_key],
            ]
            
            for cmd in commands:
                result = subprocess.run(
                    cmd,
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0 and 'already exists' not in result.stderr:
                    print(f"Command: {' '.join(cmd)}")
                    print(f"Error: {result.stderr}")
            
            print(f"✓ DVC remote '{remote_name}' configured")
            
        except Exception as e:
            print(f"Error configuring DVC remote: {e}")
    
    def add_file(self, file_path: str):
        """
        Add file to DVC tracking
        
        Args:
            file_path: Path to file to track
        """
        try:
            result = subprocess.run(
                ['dvc', 'add', file_path],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✓ Added {file_path} to DVC")
                print(f"  Generated {file_path}.dvc")
            else:
                print(f"DVC add error: {result.stderr}")
                
        except Exception as e:
            print(f"Error adding file to DVC: {e}")
    
    def push(self):
        """Push DVC tracked files to remote storage"""
        try:
            result = subprocess.run(
                ['dvc', 'push'],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✓ DVC push successful")
                print(result.stdout)
            else:
                print(f"DVC push error: {result.stderr}")
                
        except Exception as e:
            print(f"Error pushing to DVC remote: {e}")
    
    def pull(self):
        """Pull DVC tracked files from remote storage"""
        try:
            result = subprocess.run(
                ['dvc', 'pull'],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✓ DVC pull successful")
            else:
                print(f"DVC pull error: {result.stderr}")
                
        except Exception as e:
            print(f"Error pulling from DVC remote: {e}")


def setup_storage_and_versioning(data_filepath: str):
    """
    Complete storage and versioning setup
    
    Args:
        data_filepath: Path to processed data file
    """
    print("\n" + "="*50)
    print("SETTING UP STORAGE AND VERSIONING")
    print("="*50)
    
    # Initialize MinIO storage
    print("\n[1/5] Initializing MinIO storage...")
    minio_storage = MinIOStorage()
    
    # Upload file to MinIO
    print("\n[2/5] Uploading file to MinIO...")
    object_name = f"processed_data/{os.path.basename(data_filepath)}"
    minio_storage.upload_file(data_filepath, object_name)
    
    # Initialize DVC
    print("\n[3/5] Initializing DVC...")
    dvc_manager = DVCManager()
    dvc_manager.init_dvc()
    
    # Configure DVC remote
    print("\n[4/5] Configuring DVC remote...")
    dvc_manager.configure_remote()
    
    # Add file to DVC and push
    print("\n[5/5] Adding file to DVC and pushing...")
    dvc_manager.add_file(data_filepath)
    dvc_manager.push()
    
    print("\n" + "="*50)
    print("✓ STORAGE AND VERSIONING SETUP COMPLETE")
    print("="*50)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        data_path = sys.argv[1]
        setup_storage_and_versioning(data_path)
    else:
        print("Usage: python storage_versioning.py <data_filepath>")

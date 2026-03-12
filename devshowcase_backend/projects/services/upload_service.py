import os
import zipfile
import tempfile
import shutil
import subprocess
from pathlib import Path
from django.conf import settings


class UploadService:
    """Service for handling file uploads and GitHub repository cloning."""
    
    MAX_ZIP_SIZE = 100 * 1024 * 1024  # 100MB
    MAX_GITHUB_SIZE = 500 * 1024 * 1024  # 500MB
    
    def __init__(self, upload_instance):
        """Initialize with a ProjectUpload instance."""
        self.upload = upload_instance
    
    def handle_files_upload(self, files_data):
        """
        Handle multiple files upload (folder or multi-file selection).
        
        Args:
            files_data: List of dictionaries with 'file' and 'path' keys
            
        Returns:
            str: Path to organized directory
            
        Raises:
            ValueError: If files are invalid or too large
        """
        # Calculate total size
        total_size = sum(file_info['file'].size for file_info in files_data)
        
        # Validate total file size
        if total_size > 50 * 1024 * 1024:  # 50MB limit for files upload
            raise ValueError(f"Total file size ({total_size} bytes) exceeds 50MB limit")
        
        # Update upload record
        self.upload.file_size = total_size
        self.upload.status = 'extracting'
        self.upload.current_message = 'Organizing files...'
        self.upload.progress_percentage = 10
        self.upload.save()
        
        # Create secure temporary directory
        temp_dir = tempfile.mkdtemp(prefix='files_upload_')
        self.upload.temp_directory = temp_dir
        self.upload.save()
        
        try:
            # Organize files maintaining directory structure
            for file_info in files_data:
                file_obj = file_info['file']
                file_path = file_info['path']
                
                # Create full path in temp directory
                full_path = Path(temp_dir) / file_path
                
                # Ensure directory exists
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write file content
                with open(full_path, 'wb') as f:
                    for chunk in file_obj.chunks():
                        f.write(chunk)
            
            self.upload.progress_percentage = 20
            self.upload.current_message = 'Files organized successfully'
            self.upload.save()
            
            return temp_dir
            
        except Exception as e:
            # Cleanup on error
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
            raise ValueError(f"Failed to organize files: {str(e)}")

    def handle_zip_upload(self, zip_file):
        """
        Extract and validate a zip file upload.
        
        Args:
            zip_file: Django UploadedFile object
            
        Returns:
            str: Path to extracted directory
            
        Raises:
            ValueError: If file is too large or invalid
        """
        # Validate file size
        if zip_file.size > self.MAX_ZIP_SIZE:
            raise ValueError(f"File size ({zip_file.size} bytes) exceeds 100MB limit")
        
        # Update upload record
        self.upload.file_size = zip_file.size
        self.upload.status = 'extracting'
        self.upload.current_message = 'Extracting files...'
        self.upload.progress_percentage = 10
        self.upload.save()
        
        # Create secure temporary directory
        temp_dir = tempfile.mkdtemp(prefix='project_upload_')
        self.upload.temp_directory = temp_dir
        self.upload.save()

        
        try:
            # Extract zip file
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                # Validate zip file
                if zip_ref.testzip() is not None:
                    raise ValueError("Corrupted zip file")
                
                # Extract with path traversal protection
                for member in zip_ref.namelist():
                    # Prevent path traversal attacks
                    member_path = Path(temp_dir) / member
                    if not str(member_path.resolve()).startswith(str(Path(temp_dir).resolve())):
                        raise ValueError("Invalid file path in zip")
                
                zip_ref.extractall(temp_dir)
            
            self.upload.progress_percentage = 20
            self.upload.current_message = 'Files extracted successfully'
            self.upload.save()
            
            return temp_dir
            
        except Exception as e:
            # Cleanup on error
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
            raise ValueError(f"Failed to extract zip file: {str(e)}")
    
    def handle_github_url(self, github_url, access_token=None):
        """
        Clone a GitHub repository.
        
        Args:
            github_url: GitHub repository URL
            access_token: Optional GitHub access token for private repos
            
        Returns:
            str: Path to cloned directory
            
        Raises:
            ValueError: If cloning fails or repo is too large
        """
        # Update upload record
        self.upload.status = 'extracting'
        self.upload.current_message = 'Cloning repository...'
        self.upload.progress_percentage = 10
        self.upload.save()
        
        # Create secure temporary directory
        temp_dir = tempfile.mkdtemp(prefix='github_clone_')
        self.upload.temp_directory = temp_dir
        self.upload.save()

        
        try:
            # Build git clone command
            if access_token:
                # Insert token into URL for private repos
                if 'github.com/' in github_url:
                    github_url = github_url.replace('github.com/', f'{access_token}@github.com/')
            
            # Clone with depth 1 for faster cloning
            result = subprocess.run(
                ['git', 'clone', '--depth', '1', github_url, temp_dir],
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
            
            if result.returncode != 0:
                raise ValueError(f"Git clone failed: {result.stderr}")
            
            # Check directory size
            total_size = sum(
                f.stat().st_size for f in Path(temp_dir).rglob('*') if f.is_file()
            )
            
            if total_size > self.MAX_GITHUB_SIZE:
                raise ValueError(f"Repository size ({total_size} bytes) exceeds 500MB limit")
            
            self.upload.file_size = total_size
            self.upload.progress_percentage = 20
            self.upload.current_message = 'Repository cloned successfully'
            self.upload.save()
            
            return temp_dir
            
        except subprocess.TimeoutExpired:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
            raise ValueError("Git clone timed out after 2 minutes")
        except Exception as e:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
            raise ValueError(f"Failed to clone repository: {str(e)}")
    
    def get_upload_status(self):
        """
        Get current upload status.
        
        Returns:
            dict: Status information
        """
        return {
            'id': str(self.upload.id),
            'status': self.upload.status,
            'progress_percentage': self.upload.progress_percentage,
            'current_message': self.upload.current_message,
            'detected_language': self.upload.detected_language,
            'detected_framework': self.upload.detected_framework,
            'endpoints_found': self.upload.endpoints_found,
            'error_message': self.upload.error_message,
        }
    
    @staticmethod
    def cleanup_temp_directory(temp_dir):
        """Clean up temporary directory."""
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)

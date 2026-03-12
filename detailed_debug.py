#!/usr/bin/env python3
"""
Detailed debug to understand why endpoints aren't being found.
"""

import os
import sys
import django
import tempfile
import shutil
from pathlib import Path

# Add the Django project to the path
sys.path.append('devshowcase_backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from projects.models import ProjectUpload, Project
from projects.services.analysis_engine import AnalysisEngine
from django.contrib.auth.models import User

def analyze_github_project():
    """Re-analyze the GitHub project to see what's happening."""
    
    # Get the latest upload
    latest_upload = ProjectUpload.objects.filter(upload_method='github').order_by('-created_at').first()
    
    if not latest_upload:
        print("No GitHub uploads found.")
        return
    
    github_url = latest_upload.github_url
    print(f"=== Re-analyzing GitHub Project ===")
    print(f"GitHub URL: {github_url}")
    print(f"Original detection: {latest_upload.detected_language} / {latest_upload.detected_framework}")
    
    # Clone the repo again to a temp directory
    from projects.services.upload_service import UploadService
    
    # Create a new upload instance for testing
    test_upload = ProjectUpload.objects.create(
        project=latest_upload.project,
        user=latest_upload.user,
        upload_method='github',
        github_url=github_url,
        status='analyzing'
    )
    
    try:
        upload_service = UploadService(test_upload)
        temp_dir = upload_service.handle_github_url(github_url)
        
        print(f"Cloned to: {temp_dir}")
        
        # List all files in the project
        temp_path = Path(temp_dir)
        all_files = list(temp_path.rglob('*'))
        code_files = []
        
        print(f"\n=== Project Structure ===")
        print(f"Total files: {len(all_files)}")
        
        # Show directory structure
        for file_path in sorted(all_files)[:20]:  # Show first 20 files
            if file_path.is_file():
                rel_path = file_path.relative_to(temp_path)
                size = file_path.stat().st_size
                print(f"  📄 {rel_path} ({size} bytes)")
                
                # Check if it looks like a code file
                if file_path.suffix in ['.js', '.jsx', '.ts', '.tsx', '.py', '.java', '.cs', '.php', '.rb', '.go']:
                    code_files.append(file_path)
            else:
                rel_path = file_path.relative_to(temp_path)
                print(f"  📁 {rel_path}/")
        
        if len(all_files) > 20:
            print(f"  ... and {len(all_files) - 20} more files")
        
        print(f"\n=== Code Files Found ===")
        print(f"Potential code files: {len(code_files)}")
        for code_file in code_files[:10]:  # Show first 10 code files
            rel_path = code_file.relative_to(temp_path)
            print(f"  🔧 {rel_path}")
        
        # Check for common framework indicators
        print(f"\n=== Framework Indicators ===")
        package_json = temp_path / 'package.json'
        requirements_txt = temp_path / 'requirements.txt'
        pom_xml = temp_path / 'pom.xml'
        
        if package_json.exists():
            print("✅ package.json found")
            try:
                import json
                content = json.loads(package_json.read_text())
                deps = {**content.get('dependencies', {}), **content.get('devDependencies', {})}
                print(f"   Dependencies: {list(deps.keys())[:10]}")
            except:
                print("   Could not parse package.json")
        
        if requirements_txt.exists():
            print("✅ requirements.txt found")
            content = requirements_txt.read_text()[:200]
            print(f"   Content preview: {content}")
        
        if pom_xml.exists():
            print("✅ pom.xml found")
        
        # Now run the analysis engine
        print(f"\n=== Running Analysis Engine ===")
        analyzer = AnalysisEngine(test_upload)
        
        try:
            result = analyzer.analyze_project(temp_dir)
            print(f"✅ Analysis successful!")
            print(f"   Language: {result['detected_language']}")
            print(f"   Framework: {result['detected_framework']}")
            print(f"   Endpoints: {len(result['endpoints'])}")
            print(f"   Base URL: {result['base_url']}")
            
            if result['endpoints']:
                print(f"\n=== Endpoints Found ===")
                for i, endpoint in enumerate(result['endpoints'][:5]):
                    print(f"   {i+1}. {endpoint.get('method', 'GET')} {endpoint.get('path', 'unknown')}")
                    print(f"      File: {endpoint.get('file', 'unknown')}")
                    print(f"      Description: {endpoint.get('description', 'No description')}")
            else:
                print(f"\n❌ No endpoints found - this is the issue!")
                
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            import traceback
            print(traceback.format_exc())
        
        # Clean up
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            
    except Exception as e:
        print(f"❌ Failed to clone/analyze: {e}")
        import traceback
        print(traceback.format_exc())
    
    finally:
        # Clean up test upload
        test_upload.delete()

if __name__ == '__main__':
    analyze_github_project()
import threading
from datetime import datetime
from django.utils import timezone
from .services.upload_service import UploadService
from .services.security_scanner import SecurityScanner
from .services.analysis_engine import AnalysisEngine
from .services.endpoint_extractor import EndpointExtractor


def process_upload_pipeline(upload_id):
    """
    Background task to process uploaded project through the pipeline:
    extract → scan → analyze → extract endpoints
    
    Args:
        upload_id: UUID of ProjectUpload instance
    """
    from .models import ProjectUpload
    
    try:
        upload = ProjectUpload.objects.get(id=upload_id)
    except ProjectUpload.DoesNotExist:
        return
    
    temp_dir = None
    
    try:
        # Step 1: Extract/Clone
        upload_service = UploadService(upload)
        
        if upload.upload_method == 'zip':
            # Zip file should already be uploaded, path stored in temp_directory
            temp_dir = upload.temp_directory
        elif upload.upload_method == 'github':
            temp_dir = upload_service.handle_github_url(upload.github_url)
        elif upload.upload_method == 'files':
            # Files are already uploaded and organized, path stored in temp_directory
            temp_dir = upload.temp_directory
        
        # Step 2: Security Scan (DISABLED FOR PROTOTYPE - RE-ENABLE FOR PRODUCTION)
        # scanner = SecurityScanner(upload)
        # scan_result = scanner.scan_directory(temp_dir)
        
        # Skip security scan for prototype
        upload.progress_percentage = 40
        upload.current_message = 'Security scan skipped (prototype mode)'
        upload.save()
        
        # Step 3: AI Analysis
        analyzer = AnalysisEngine(upload)
        analysis_result = analyzer.analyze_project(temp_dir)
        
        # Step 4: Extract and Save Endpoints
        base_url = analysis_result.get('base_url', 'http://localhost:3000')
        extractor = EndpointExtractor(upload, base_url=base_url)
        endpoints_count = extractor.extract_endpoint_details(analysis_result['endpoints'])

        # Step 5: Generate Architecture (if requested)
        architecture_nodes_created = 0
        if upload.generate_architecture:
            try:
                upload.current_message = 'Generating architecture diagram...'
                upload.progress_percentage = 85
                upload.save()
                
                from .services.architecture_analyzer import ArchitectureAnalyzer
                from .services.architecture_node_generator import ArchitectureNodeGenerator
                
                # Analyze project architecture
                arch_analyzer = ArchitectureAnalyzer()
                arch_analysis = arch_analyzer.analyze_project_structure(temp_dir)
                
                # Generate architecture nodes
                node_generator = ArchitectureNodeGenerator()
                components = arch_analysis.get('components', [])
                
                if components:
                    nodes = node_generator.generate_nodes(components, upload.project, upload)
                    saved_nodes = node_generator.save_nodes(nodes)
                    architecture_nodes_created = len(saved_nodes)
                    
                    upload.architecture_nodes_created = architecture_nodes_created
                    upload.architecture_analysis_data = arch_analysis
                    upload.save()
                    
                    print(f"Generated {architecture_nodes_created} architecture nodes")
                else:
                    print("No architectural components detected for diagram generation")
                    
            except Exception as e:
                # Don't fail the entire upload if architecture generation fails
                print(f"Architecture generation failed: {str(e)}")
                upload.architecture_analysis_data = {'error': str(e)}
                upload.save()
        
        # Mark as completed
        upload.status = 'completed'
        upload.progress_percentage = 100
        
        # Update completion message to include architecture info
        completion_parts = [f'Found {endpoints_count} endpoints']
        if upload.generate_architecture and architecture_nodes_created > 0:
            completion_parts.append(f'{architecture_nodes_created} architecture nodes')
        
        upload.current_message = f'Analysis complete! {", ".join(completion_parts)}'
        upload.completed_at = timezone.now()
        upload.save()
        
    except ValueError as e:
        # Handle expected errors (validation, security, etc.)
        upload.status = 'failed'
        upload.error_message = str(e)
        upload.current_message = 'Analysis failed'
        upload.save()
        
    except Exception as e:
        # Handle unexpected errors
        upload.status = 'failed'
        upload.error_message = f'Unexpected error: {str(e)}'
        upload.current_message = 'Analysis failed'
        upload.save()
        
    finally:
        # Cleanup temporary files
        if temp_dir:
            UploadService.cleanup_temp_directory(temp_dir)
            upload.temp_directory = ''
            upload.save()


def start_upload_pipeline(upload_id):
    """Start the upload pipeline in a background thread."""
    thread = threading.Thread(target=process_upload_pipeline, args=(upload_id,))
    thread.daemon = True
    thread.start()

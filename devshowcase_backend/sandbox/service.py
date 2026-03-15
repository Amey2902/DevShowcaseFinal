import re
from urllib.parse import urlparse
from .models import SandboxEnvironment, SandboxCollection, SandboxRecord
from projects.services.request_body_generator import RequestBodyGenerator


class SandboxService:
    @staticmethod
    def extract_resource_name(url):
        """Extract resource name from URL: /api/expenses -> expenses"""
        path = urlparse(url).path
        segments = [s for s in path.split('/') if s]
                
        filtered = [
            s for s in segments 
            if s not in ['api', 'v1', 'v2', 'v3'] 
            and not s.isdigit()
        ]
        
        return filtered[0] if filtered else 'default'
    
    @staticmethod
    def generate_sandbox(project):
        """Generate sandbox from project endpoints"""
        env, created = SandboxEnvironment.objects.get_or_create(project=project)
        
        for endpoint in project.endpoints.all():
            # Generate realistic request body using AI
            try:
                request_body = RequestBodyGenerator.generate_request_body(endpoint)
                endpoint.sample_body = request_body
                endpoint.save()
            except:
                # If request body generation fails, use empty dict
                endpoint.sample_body = {}
                endpoint.save()
            
            resource_name = SandboxService.extract_resource_name(endpoint.url)
            if not resource_name:
                continue
            
            collection, _ = SandboxCollection.objects.get_or_create(
                environment=env,
                name=resource_name
            )
            
            # Clear existing records for this collection to avoid duplicates
            collection.records.all().delete()
            
            if endpoint.sample_response:
                if isinstance(endpoint.sample_response, list):
                    for item in endpoint.sample_response:
                        SandboxRecord.objects.create(collection=collection, data=item)
                elif isinstance(endpoint.sample_response, dict):
                    SandboxRecord.objects.create(collection=collection, data=endpoint.sample_response)
            else:
                # Generate dummy data if no sample_response
                for i in range(1, 4):
                    dummy_data = {
                        'id': i,
                        'title': f'Sample {resource_name.capitalize()} {i}',
                        'description': f'This is a sample {resource_name}',
                        'created_at': '2024-01-01T00:00:00Z'
                    }
                    SandboxRecord.objects.create(collection=collection, data=dummy_data)
        
        return env
    
    @staticmethod
    def execute_sandbox_request(endpoint, custom_body, resolved_url=None):
        """Execute request in sandbox - Always returns success in sandbox mode"""
        
        try:
            project = endpoint.project
            
            # Auto-generate sandbox if it doesn't exist
            try:
                env = project.sandbox
            except SandboxEnvironment.DoesNotExist:
                env = SandboxService.generate_sandbox(project)
            
            # Use resolved URL if provided, otherwise use original endpoint URL
            url_to_use = resolved_url or endpoint.url
            
            resource_name = SandboxService.extract_resource_name(url_to_use)
            if not resource_name:
                resource_name = 'items'  # Default fallback
            
            # Auto-create collection if it doesn't exist
            try:
                collection = env.collections.get(name=resource_name)
            except SandboxCollection.DoesNotExist:
                collection = SandboxCollection.objects.create(
                    environment=env,
                    name=resource_name
                )
                # Create some default mock data
                for i in range(1, 4):
                    dummy_data = {
                        'id': i,
                        'title': f'Sample {resource_name.capitalize()} {i}',
                        'description': f'This is a sample {resource_name} for testing',
                        'status': 'active',
                        'created_at': '2024-01-01T00:00:00Z'
                    }
                    SandboxRecord.objects.create(collection=collection, data=dummy_data)
            
            method = endpoint.method
            
            # Extract ID from URL
            record_id = None
            try:
                # Try to extract numeric ID first
                id_match = re.search(r'/(\d+)/?$', url_to_use)
                if id_match:
                    record_id = int(id_match.group(1))
                else:
                    # Check if there's a non-numeric ID at the end
                    path_match = re.search(r'/([^/]+)/?$', url_to_use)
                    if path_match:     
                        path_value = path_match.group(1)
                        # Skip if it's the resource name itself
                        if path_value != resource_name:
                            try:
                                record_id = int(path_value)
                            except ValueError:
                                # For string IDs, try to extract numeric part
                                numeric_match = re.search(r'(\d+)', path_value)
                                if numeric_match:
                                    record_id = int(numeric_match.group(1))
                                else:
                                    record_id = 1  # Default fallback
            except:
                record_id = 1  # Safe fallback
            
            # Handle different HTTP methods - Always return success in sandbox
            if method == 'GET':
                if record_id:
                    # Try to find the exact record first
                    for r in collection.records.all():
                        if r.data.get('id') == record_id:
                            return {'status_code': 200, 'data': r.data, 'error': None}
                    
                    # If not found, generate a mock response
                    mock_data = {
                        'id': record_id,
                        'title': f'Sample {resource_name.capitalize()} {record_id}',
                        'description': f'This is a mock {resource_name} for sandbox testing',
                        'status': 'active',
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_at': '2024-01-01T00:00:00Z'
                    }
                    return {'status_code': 200, 'data': mock_data, 'error': None}
                else:
                    # Return list of records
                    records = collection.records.all()
                    data = [r.data for r in records]
                    return {'status_code': 200, 'data': data, 'error': None}
            
            elif method == 'POST':
                if record_id:
                    # Action on a specific resource
                    return {
                        'status_code': 200, 
                        'data': {
                            'success': True,
                            'message': 'Action completed successfully',
                            'id': record_id,
                            **custom_body
                        }, 
                        'error': None
                    }
                else:
                    # Creating a new resource
                    next_id = collection.records.count() + 1
                    merged_data = {
                        'id': next_id, 
                        'created_at': '2024-01-01T00:00:00Z',
                        **custom_body
                    }
                    try:
                        record = SandboxRecord.objects.create(collection=collection, data=merged_data)
                        return {'status_code': 201, 'data': record.data, 'error': None}
                    except:
                        return {'status_code': 201, 'data': merged_data, 'error': None}
            
            elif method in ['PUT', 'PATCH']:
                target_id = record_id or custom_body.get('id', 1)
                
                # Always return success with mock data
                mock_data = {
                    'id': target_id,
                    'title': f'Updated {resource_name.capitalize()} {target_id}',
                    'description': f'This {resource_name} was updated in sandbox mode',
                    'status': 'updated',
                    'updated_at': '2024-01-01T12:00:00Z',
                    **custom_body
                }
                return {'status_code': 200, 'data': mock_data, 'error': None}
            
            elif method == 'DELETE':
                target_id = record_id or custom_body.get('id', 1)
                
                # Always return success
                return {
                    'status_code': 200, 
                    'data': {
                        'success': True,
                        'message': f'{resource_name.capitalize()} {target_id} deleted successfully',
                        'id': target_id
                    }, 
                    'error': None
                }
            
            # Fallback for any other method
            return {
                'status_code': 200,
                'data': {
                    'success': True,
                    'message': f'{method} request completed successfully',
                    'mock_data': True,
                    **custom_body
                },
                'error': None
            }
            
        except Exception as e:
            # Ultimate fallback - always return success in sandbox mode
            return {
                'status_code': 200,
                'data': {
                    'success': True,
                    'message': 'Sandbox request completed successfully',
                    'mock_data': True,
                    'note': 'This is a mock response for testing purposes',
                    **custom_body
                },
                'error': None
            }
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
            request_body = RequestBodyGenerator.generate_request_body(endpoint)
            endpoint.sample_body = request_body
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
        """Execute request in sandbox
        
        Args:
            endpoint: The Endpoint model instance
            custom_body: Custom request body from user
            resolved_url: URL with path parameters already resolved (optional)
        """
        project = endpoint.project
        
        try:
            env = project.sandbox
        except SandboxEnvironment.DoesNotExist:
            return None
        
        # Use resolved URL if provided, otherwise use original endpoint URL
        url_to_use = resolved_url or endpoint.url
        
        resource_name = SandboxService.extract_resource_name(url_to_use)
        if not resource_name:
            return {'status_code': 404, 'data': None, 'error': 'Resource not found'}
        
        try:
            collection = env.collections.get(name=resource_name)
        except SandboxCollection.DoesNotExist:
            return {'status_code': 404, 'data': None, 'error': f'Collection {resource_name} not found'}
        
        method = endpoint.method
        
        # Extract ID from URL - now using the resolved URL with actual values
        # Match patterns like /api/users/123 or /api/users/user123
        id_match = re.search(r'/(\d+)/?$', url_to_use)
        
        record_id = None
        if id_match:
            record_id = int(id_match.group(1))
        else:
            # Check if there's a non-numeric ID at the end (like /users/user123)
            # This handles resolved path parameters that aren't numeric
            path_match = re.search(r'/([^/]+)/?$', url_to_use)
            if path_match:
                path_value = path_match.group(1)
                # Skip if it's the resource name itself (e.g., /users)
                if path_value != resource_name:
                    # Try to convert to int, otherwise use as string ID
                    try:
                        record_id = int(path_value)
                    except ValueError:
                        # For string IDs like "user123", try to extract numeric part
                        numeric_match = re.search(r'(\d+)', path_value)
                        if numeric_match:
                            record_id = int(numeric_match.group(1))
                        else:
                            # Default to 1 if we can't extract a number
                            record_id = 1
        
        if method == 'GET':
            if record_id:
                # Find record by the 'id' field in the data JSON
                for r in collection.records.all():
                    if r.data.get('id') == record_id:
                        return {'status_code': 200, 'data': r.data, 'error': None}
                return {'status_code': 404, 'data': None, 'error': 'Record not found'}
            else:
                records = collection.records.all()
                data = [r.data for r in records]
                return {'status_code': 200, 'data': data, 'error': None}
        
        elif method == 'POST':
            # For POST requests, we don't need to find existing records
            # Just return success with the request body (simulating creation/action)
            
            # If there's a record_id (from path parameter like /users/:userId/reset-password),
            # just simulate success without needing an existing record
            if record_id:
                # Action on a specific resource (e.g., reset password, send email)
                return {
                    'status_code': 200, 
                    'data': {
                        'success': True,
                        'message': 'Action completed successfully',
                        **custom_body
                    }, 
                    'error': None
                }
            else:
                # Creating a new resource
                next_id = collection.records.count() + 1
                merged_data = {'id': next_id, **custom_body}
                record = SandboxRecord.objects.create(collection=collection, data=merged_data)
                return {'status_code': 201, 'data': record.data, 'error': None}
        
        elif method in ['PUT', 'PATCH']:
            # Get ID from URL or request body
            target_id = record_id or custom_body.get('id')
            
            if not target_id:
                return {'status_code': 400, 'data': None, 'error': 'ID required for update'}
            
            # Find record by the 'id' field in the data JSON
            record = None
            for r in collection.records.all():
                if r.data.get('id') == target_id:
                    record = r
                    break
            
            if not record:
                # In sandbox mode, be forgiving - create the record if it doesn't exist
                new_data = {'id': target_id, **custom_body}
                record = SandboxRecord.objects.create(collection=collection, data=new_data)
                return {'status_code': 200, 'data': record.data, 'error': None}
            
            if method == 'PUT':
                record.data = {'id': target_id, **custom_body}
            else:
                record.data.update(custom_body)
            record.save()
            return {'status_code': 200, 'data': record.data, 'error': None}
        
        elif method == 'DELETE':
            # Get ID from URL or request body
            target_id = record_id or custom_body.get('id')
            
            if not target_id:
                return {'status_code': 400, 'data': None, 'error': 'ID required for delete'}
            
            # Find record by the 'id' field in the data JSON
            record = None
            for r in collection.records.all():
                if r.data.get('id') == target_id:
                    record = r
                    break
            
            if not record:
                return {'status_code': 404, 'data': None, 'error': 'Record not found'}
            
            record.delete()
            return {'status_code': 204, 'data': None, 'error': None}
        
        return {'status_code': 405, 'data': None, 'error': 'Method not allowed'}

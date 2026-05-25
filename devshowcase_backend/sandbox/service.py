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
    def _generate_mock_value(field_name, field_info, record_id=1):
        """Generate a realistic mock value based on field name and type info."""
        field_type = 'string'
        if isinstance(field_info, dict):
            field_type = field_info.get('type', 'string').lower()
        elif isinstance(field_info, str):
            field_type = field_info.lower()
        
        name = field_name.lower()
        
        # ID fields
        if name in ('id', '_id'):
            return record_id
        
        # Type & name-based mock values
        if field_type in ('integer', 'number', 'int', 'float'):
            if 'price' in name or 'cost' in name or 'amount' in name:
                return round(19.99 + record_id * 10, 2)
            if 'age' in name:
                return 25 + record_id
            if 'quantity' in name or 'count' in name or 'stock' in name:
                return 10 * record_id
            return record_id
        
        if field_type == 'boolean' or field_type == 'bool':
            return True
        
        if field_type == 'array' or field_type == 'list':
            return []
        
        if field_type == 'object' or field_type == 'dict':
            return {}
        
        # String type - pick realistic value based on field name
        if 'email' in name:
            return f"user{record_id}@example.com"
        if 'password' in name:
            return "SecurePass123!"
        if name in ('username', 'user_name'):
            return f"user_{record_id}"
        if name in ('name', 'first_name', 'firstname', 'fname'):
            names = ['Alice', 'Bob', 'Charlie']
            return names[(record_id - 1) % len(names)]
        if name in ('last_name', 'lastname', 'lname', 'surname'):
            return 'Smith'
        if 'title' in name:
            return f"Sample Title {record_id}"
        if 'description' in name or 'desc' in name:
            return f"This is a sample description for item {record_id}"
        if 'content' in name or 'body' in name or 'text' in name:
            return f"Sample content for record {record_id}"
        if 'url' in name or 'link' in name:
            return f"https://example.com/resource/{record_id}"
        if 'phone' in name:
            return f"+1-555-010{record_id}"
        if 'address' in name:
            return f"{100 + record_id} Main Street, City, ST 12345"
        if 'status' in name:
            return 'active'
        if 'category' in name or 'type' in name:
            return 'general'
        if 'date' in name or 'created' in name or 'updated' in name or 'timestamp' in name:
            return f"2024-01-0{min(record_id, 9)}T12:00:00Z"
        if 'token' in name:
            return f"tok_sample_{record_id}"
        
        return f"sample_{field_name}_{record_id}"
    
    @staticmethod
    def _generate_record_from_schema(schema, record_id):
        """Generate a complete mock record from a response_schema."""
        record = {}
        for field_name, field_info in schema.items():
            record[field_name] = SandboxService._generate_mock_value(field_name, field_info, record_id)
        # Always include an id if not in schema
        if 'id' not in record and '_id' not in record:
            record['id'] = record_id
        return record
    
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
            elif endpoint.response_schema and isinstance(endpoint.response_schema, dict) and len(endpoint.response_schema) > 0:
                # Use response_schema to generate accurate mock records
                for i in range(1, 4):
                    mock_data = SandboxService._generate_record_from_schema(endpoint.response_schema, i)
                    SandboxRecord.objects.create(collection=collection, data=mock_data)
            else:
                # Fallback: generate context-aware dummy data from endpoint info
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
                # Create schema-aware mock data if available
                if endpoint.response_schema and isinstance(endpoint.response_schema, dict) and len(endpoint.response_schema) > 0:
                    for i in range(1, 4):
                        mock_data = SandboxService._generate_record_from_schema(endpoint.response_schema, i)
                        SandboxRecord.objects.create(collection=collection, data=mock_data)
                else:
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
                    
                    # If not found, generate a schema-aware mock response
                    if endpoint.response_schema and isinstance(endpoint.response_schema, dict) and len(endpoint.response_schema) > 0:
                        mock_data = SandboxService._generate_record_from_schema(endpoint.response_schema, record_id)
                    else:
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
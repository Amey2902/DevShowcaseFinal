import json
import re
from urllib.parse import urlparse
from sandbox.service import SandboxService


class TranslationExecutor:
    """Execute translated API endpoints in different framework contexts."""
    
    # Framework-specific response formats
    FRAMEWORK_RESPONSES = {
        'express': {
            'success_wrapper': lambda data: {'success': True, 'data': data},
            'error_wrapper': lambda error: {'error': error},
            'status_codes': {'success': 200, 'created': 201, 'error': 500, 'not_found': 404}
        },
        'fastapi': {
            'success_wrapper': lambda data: {'success': True, 'data': data},
            'error_wrapper': lambda error: {'detail': error},
            'status_codes': {'success': 200, 'created': 201, 'error': 422, 'not_found': 404}
        },
        'flask': {
            'success_wrapper': lambda data: {'success': True, 'data': data},
            'error_wrapper': lambda error: {'error': error},
            'status_codes': {'success': 200, 'created': 201, 'error': 500, 'not_found': 404}
        },
        'django': {
            'success_wrapper': lambda data: {'success': True, 'data': data},
            'error_wrapper': lambda error: {'error': error},
            'status_codes': {'success': 200, 'created': 201, 'error': 500, 'not_found': 404}
        },
        'spring': {
            'success_wrapper': lambda data: {'success': True, 'result': data},
            'error_wrapper': lambda error: {'success': False, 'message': error},
            'status_codes': {'success': 200, 'created': 201, 'error': 500, 'not_found': 404}
        }
    }
    
    @staticmethod
    def execute_translated_endpoint(endpoint, target_framework, custom_body, custom_path_params=None):
        """
        Execute an endpoint as if it were implemented in the target framework.
        
        Args:
            endpoint: The original Endpoint model instance
            target_framework: Target framework ('express', 'fastapi', 'flask', 'django', 'spring')
            custom_body: Custom request body from user
            custom_path_params: Custom path parameter values
            
        Returns:
            dict: Execution result with framework-specific formatting
        """
        if target_framework not in TranslationExecutor.FRAMEWORK_RESPONSES:
            return {
                'status_code': 400,
                'data': None,
                'error': f'Unsupported framework: {target_framework}',
                'framework': target_framework
            }
        
        framework_config = TranslationExecutor.FRAMEWORK_RESPONSES[target_framework]
        
        # Resolve path parameters
        resolved_url = TranslationExecutor._resolve_path_parameters(
            endpoint.url, endpoint.path_parameters, custom_path_params
        )
        
        # Execute the request using sandbox service (same business logic)
        sandbox_result = SandboxService.execute_sandbox_request(endpoint, custom_body, resolved_url)
        
        if not sandbox_result:
            return {
                'status_code': framework_config['status_codes']['error'],
                'data': framework_config['error_wrapper']('Sandbox execution failed'),
                'error': 'Sandbox execution failed',
                'framework': target_framework
            }
        
        # Transform response to match target framework format
        transformed_result = TranslationExecutor._transform_response(
            sandbox_result, target_framework, framework_config
        )
        
        # Add framework metadata
        transformed_result['framework'] = target_framework
        transformed_result['translation_mode'] = True
        
        return transformed_result
    
    @staticmethod
    def _resolve_path_parameters(url, path_parameters, custom_values=None):
        """Same as execution/views.py but extracted for reuse."""
        if not path_parameters:
            return url
        
        resolved_url = url
        custom_values = custom_values or {}
        
        # Sample values for common parameter names
        sample_values = {
            'id': '1',
            'user_id': 'user123',
            'userId': 'user123',
            'post_id': 'post456',
            'postId': 'post456',
            'comment_id': 'comment789',
            'commentId': 'comment789',
            'product_id': 'prod123',
            'productId': 'prod123',
            'order_id': 'order456',
            'orderId': 'order456',
            'category_id': 'cat123',
            'categoryId': 'cat123',
        }
        
        for param in path_parameters:
            # Handle both object and string parameters
            param_name = param if isinstance(param, str) else (param.get('name') if isinstance(param, dict) else str(param))
            
            # Use custom value if provided, otherwise use sample value
            value = custom_values.get(param_name) or sample_values.get(param_name, '123')
            
            # Replace both :param and {param} formats
            resolved_url = re.sub(f':{param_name}\\b', str(value), resolved_url)
            resolved_url = re.sub(f'\\{{{param_name}\\}}', str(value), resolved_url)
        
        return resolved_url
    
    @staticmethod
    def _transform_response(sandbox_result, target_framework, framework_config):
        """Transform sandbox response to match target framework format."""
        original_status = sandbox_result['status_code']
        original_data = sandbox_result['data']
        original_error = sandbox_result['error']
        
        # Map status codes to framework-specific ones
        if original_error:
            if original_status == 404:
                status_code = framework_config['status_codes']['not_found']
            else:
                status_code = framework_config['status_codes']['error']
            
            return {
                'status_code': status_code,
                'data': framework_config['error_wrapper'](original_error),
                'error': original_error
            }
        
        # Success response
        if original_status == 201:
            status_code = framework_config['status_codes']['created']
        else:
            status_code = framework_config['status_codes']['success']
        
        # Apply framework-specific wrapping
        wrapped_data = framework_config['success_wrapper'](original_data)
        
        # Add framework-specific metadata
        if target_framework == 'fastapi':
            # FastAPI often includes request metadata
            try:
                # Convert data to string first to avoid unhashable type errors
                data_str = json.dumps(original_data, sort_keys=True) if original_data else "empty"
                wrapped_data['request_id'] = f"req_{hash(data_str) % 10000:04d}"
            except (TypeError, ValueError):
                # Fallback if JSON serialization fails
                wrapped_data['request_id'] = f"req_{abs(id(original_data)) % 10000:04d}"
        elif target_framework == 'spring':
            # Spring Boot often includes timestamp
            import datetime
            wrapped_data['timestamp'] = datetime.datetime.now().isoformat()
        elif target_framework == 'django':
            # Django REST Framework pagination-like structure for lists
            if isinstance(original_data, list):
                wrapped_data = {
                    'count': len(original_data),
                    'results': original_data
                }
        
        return {
            'status_code': status_code,
            'data': wrapped_data,
            'error': None
        }
    
    @staticmethod
    def get_framework_info(target_framework):
        """Get information about a framework's response format."""
        if target_framework not in TranslationExecutor.FRAMEWORK_RESPONSES:
            return None
        
        framework_names = {
            'express': 'Express.js',
            'fastapi': 'FastAPI',
            'flask': 'Flask',
            'django': 'Django REST Framework',
            'spring': 'Spring Boot'
        }
        
        return {
            'name': framework_names.get(target_framework, target_framework),
            'id': target_framework,
            'response_format': 'Framework-specific response wrapping',
            'status_codes': TranslationExecutor.FRAMEWORK_RESPONSES[target_framework]['status_codes']
        }
import re
import requests
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django_ratelimit.decorators import ratelimit
from projects.models import Endpoint
from sandbox.service import SandboxService


def _resolve_path_parameters(url, path_parameters, custom_values=None):
    """
    Replace path parameter placeholders with sample values.
    
    Args:
        url: URL with placeholders like /users/:userId or /users/{userId}
        path_parameters: List of parameter names like ['userId', 'postId']
        custom_values: Dict of custom values provided by user (optional)
    
    Returns:
        URL with placeholders replaced with sample values
    """
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
        # Use custom value if provided, otherwise use sample value
        value = custom_values.get(param) or sample_values.get(param, '123')
        
        # Replace both :param and {param} formats
        resolved_url = re.sub(f':{param}\\b', value, resolved_url)
        resolved_url = re.sub(f'\\{{{param}\\}}', value, resolved_url)
    
    return resolved_url


@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='10/m', method='POST')
def execute_endpoint(request):
    endpoint_id = request.data.get('endpoint_id')
    custom_body = request.data.get('custom_body', {})
    custom_path_params = request.data.get('custom_path_params', {})  # New: custom path parameter values
    
    if not endpoint_id:
        return Response({'error': 'endpoint_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        endpoint = Endpoint.objects.select_related('project').get(id=endpoint_id)
    except Endpoint.DoesNotExist:
        return Response({'error': 'Endpoint not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if not endpoint.project.is_published:
        return Response({'error': 'Project is not published'}, status=status.HTTP_403_FORBIDDEN)
    
    # Check if sandbox exists
    has_sandbox = hasattr(endpoint.project, 'sandbox')
    
    # Check if user is the project owner (for live testing)
    is_owner = request.user.is_authenticated and endpoint.project.owner == request.user
    
    # Allow owner to test live API with ?mode=live query parameter
    force_live = request.GET.get('mode') == 'live' and is_owner
    
    # Replace path parameters in URL with custom values or sample values
    resolved_url = _resolve_path_parameters(endpoint.url, endpoint.path_parameters, custom_path_params)
    
    if force_live:
        # LIVE MODE - Only for project owners to test their real API
        # This calls the actual external API (use with caution)
        merged_body = {**endpoint.sample_body, **custom_body}
        
        try:
            response = requests.request(
                method=endpoint.method,
                url=resolved_url,
                headers=endpoint.headers,
                json=merged_body if endpoint.method in ['POST', 'PUT', 'PATCH'] else None,
                timeout=10
            )
            
            try:
                response_data = response.json()
            except:
                response_data = response.text
            
            return Response({
                'mode': 'live',
                'status_code': response.status_code,
                'data': response_data,
                'error': None
            })
        
        except requests.exceptions.Timeout:
            return Response({
                'mode': 'live',
                'status_code': 408,
                'data': None,
                'error': 'Request timeout'
            })
        except requests.exceptions.RequestException as e:
            return Response({
                'mode': 'live',
                'status_code': 500,
                'data': None,
                'error': str(e)
            })
    
    # SANDBOX MODE - Default for everyone (safe testing)
    if not has_sandbox:
        return Response({
            'mode': 'error',
            'status_code': 400,
            'data': None,
            'error': 'Sandbox not available. Please generate a sandbox first to test this API.'
        })
    
    sandbox_result = SandboxService.execute_sandbox_request(endpoint, custom_body, resolved_url)
    
    if sandbox_result:
        return Response({
            'mode': 'sandbox',
            'status_code': sandbox_result['status_code'],
            'data': sandbox_result['data'],
            'error': sandbox_result['error']
        })
    
    return Response({
        'mode': 'error',
        'status_code': 500,
        'data': None,
        'error': 'Sandbox execution failed'
    })

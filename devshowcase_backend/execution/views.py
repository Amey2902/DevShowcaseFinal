import re
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django_ratelimit.decorators import ratelimit
from projects.models import Endpoint
from sandbox.service import SandboxService


def _resolve_path_parameters(url, path_parameters, custom_values=None):
    if not path_parameters:
        return url

    resolved_url = url
    custom_values = custom_values or {}

    sample_values = {
        'id': '1', 'user_id': 'user123', 'userId': 'user123',
        'post_id': 'post456', 'postId': 'post456',
        'comment_id': 'comment789', 'commentId': 'comment789',
        'product_id': 'prod123', 'productId': 'prod123',
        'order_id': 'order456', 'orderId': 'order456',
        'category_id': 'cat123', 'categoryId': 'cat123',
    }

    for param in path_parameters:
        param_name = param if isinstance(param, str) else (param.get('name') if isinstance(param, dict) else str(param))
        value = custom_values.get(param_name) or sample_values.get(param_name, '123')
        resolved_url = re.sub(f':{param_name}\\b', str(value), resolved_url)
        resolved_url = re.sub(f'\\{{{param_name}\\}}', str(value), resolved_url)

    return resolved_url


@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='60/m', method='POST')
def execute_endpoint(request):
    endpoint_id = request.data.get('endpoint_id')
    custom_body = request.data.get('custom_body', {})
    custom_path_params = request.data.get('custom_path_params', {})

    if not endpoint_id:
        return Response({'error': 'endpoint_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        endpoint = Endpoint.objects.select_related('project').get(id=endpoint_id)
    except Endpoint.DoesNotExist:
        return Response({'error': 'Endpoint not found'}, status=status.HTTP_404_NOT_FOUND)

    resolved_url = _resolve_path_parameters(endpoint.url, endpoint.path_parameters, custom_path_params)

    # SANDBOX MODE - safe mock testing for everyone
    try:
        sandbox_result = SandboxService.execute_sandbox_request(endpoint, custom_body, resolved_url)

        if sandbox_result:
            return Response({
                'mode': 'sandbox',
                'status_code': sandbox_result['status_code'],
                'data': sandbox_result['data'],
                'error': sandbox_result['error']
            })
        else:
            return Response({
                'mode': 'sandbox',
                'status_code': 200,
                'data': {'success': True, 'message': 'Sandbox request completed', 'mock_data': True, **custom_body},
                'error': None
            })

    except Exception:
        return Response({
            'mode': 'sandbox',
            'status_code': 200,
            'data': {'success': True, 'message': 'Sandbox request completed (fallback)', 'mock_data': True, **custom_body},
            'error': None
        })

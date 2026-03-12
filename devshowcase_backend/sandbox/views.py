from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from projects.models import Project
from .service import SandboxService
from .serializers import SandboxEnvironmentSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_sandbox(request, project_id):
    try:
        project = Project.objects.get(id=project_id, owner=request.user)
    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    env = SandboxService.generate_sandbox(project)
    serializer = SandboxEnvironmentSerializer(env)
    
    return Response({
        'message': 'Sandbox generated successfully',
        'sandbox': serializer.data
    }, status=status.HTTP_201_CREATED)

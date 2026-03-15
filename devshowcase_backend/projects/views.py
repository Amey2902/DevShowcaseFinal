from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db.models import Q, Count
from django_ratelimit.decorators import ratelimit
from .models import Project, TechStack, ArchitectureNode, Endpoint, TimelineEvent
from .serializers import (
    ProjectSerializer, ProjectFullSerializer, TechStackSerializer,
    ArchitectureNodeSerializer, EndpointSerializer, TimelineEventSerializer
)


@api_view(['GET'])
@permission_classes([AllowAny])
def project_list(request):
    projects = Project.objects.filter(is_published=True)
    
    # Search by title or description
    search = request.GET.get('search', '')
    if search:
        projects = projects.filter(
            Q(title__icontains=search) | 
            Q(short_description__icontains=search) |
            Q(problem_statement__icontains=search)
        )
    
    # Filter by category
    category = request.GET.get('category', '')
    if category:
        projects = projects.filter(category__iexact=category)
    
    # Filter by tech stack
    tech = request.GET.get('tech', '')
    if tech:
        projects = projects.filter(tech_stack__name__icontains=tech).distinct()
    
    # Filter by owner
    owner = request.GET.get('owner', '')
    if owner:
        projects = projects.filter(owner__username=owner)
    
    # Sort
    sort = request.GET.get('sort', '-created_at')
    if sort == 'popular':
        # For now, sort by number of endpoints as a proxy for popularity
        projects = projects.annotate(endpoint_count=Count('endpoints')).order_by('-endpoint_count')
    elif sort == 'oldest':
        projects = projects.order_by('created_at')
    else:  # newest (default)
        projects = projects.order_by('-created_at')
    
    serializer = ProjectSerializer(projects, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def project_detail(request, slug):
    try:
        project = Project.objects.get(slug=slug, is_published=True)
        serializer = ProjectSerializer(project)
        return Response(serializer.data)
    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def project_full(request, slug):
    try:
        if request.user.is_authenticated:
            # Authenticated users can see their own unpublished projects
            project = Project.objects.get(slug=slug)
            if project.owner != request.user and not project.is_published:
                return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Anonymous users can only see published projects
            project = Project.objects.get(slug=slug, is_published=True)
        
        serializer = ProjectFullSerializer(project)
        return Response(serializer.data)
    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def project_create(request):
    serializer = ProjectSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(owner=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    print("Validation errors:", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def project_update(request, slug):
    try:
        project = Project.objects.get(slug=slug, owner=request.user)
        serializer = ProjectSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()   
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def project_delete(request, slug):
    try:
        project = Project.objects.get(slug=slug, owner=request.user)
        project.delete()
        return Response({'message': 'Project deleted'}, status=status.HTTP_204_NO_CONTENT)
    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def techstack_create(request):
    serializer = TechStackSerializer(data=request.data)
    if serializer.is_valid():
        project = serializer.validated_data['project']
        if project.owner != request.user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def architecture_create(request):
    serializer = ArchitectureNodeSerializer(data=request.data)
    if serializer.is_valid():
        project = serializer.validated_data['project']
        if project.owner != request.user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def endpoint_create(request):
    serializer = EndpointSerializer(data=request.data)
    if serializer.is_valid():
        project = serializer.validated_data['project']
        if project.owner != request.user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def timeline_create(request):
    serializer = TimelineEventSerializer(data=request.data)
    if serializer.is_valid():
        project = serializer.validated_data['project']
        if project.owner != request.user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def endpoint_delete(request, endpoint_id):
    try:
        endpoint = Endpoint.objects.get(id=endpoint_id)
        if endpoint.project.owner != request.user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        endpoint.delete()
        return Response({'message': 'Endpoint deleted'}, status=status.HTTP_204_NO_CONTENT)
    except Endpoint.DoesNotExist:
        return Response({'error': 'Endpoint not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='3/h', method='POST')  # Only 3 requests per hour per IP
def project_explain(request, slug):
    try:
        from groq import Groq
        from django.conf import settings
        import traceback
        
        project = Project.objects.get(slug=slug, is_published=True)
        
        tech_stack = ', '.join([tech.name for tech in project.tech_stack.all()])
        endpoints = '\n'.join([f"- {ep.method} {ep.url}: {ep.description}" for ep in project.endpoints.all()])
        
        prompt = f"""Explain this software project in a clear, engaging way for developers and recruiters:

Project: {project.title}
Description: {project.short_description}
Problem: {project.problem_statement}
Tech Stack: {tech_stack}
API Endpoints:
{endpoints}

Provide a comprehensive explanation covering:
1. What problem it solves
2. How it works technically
3. Key features and capabilities
4. Technology choices and why they matter

Keep it professional but conversational. Around 200-300 words."""

        api_key = settings.GROQ_API_KEY
        if not api_key:
            return Response({'error': 'AI service not configured'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        
        explanation = completion.choices[0].message.content
        
        return Response({'explanation': explanation})
        
    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"AI Explain Error: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='5/h', method='POST')  # Only 5 searches per hour per IP
def project_search_ai(request):
    try:
        from groq import Groq
        from django.conf import settings
        import json
        
        query = request.data.get('query', '')
        if not query:
            return Response({'error': 'Query is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        projects = Project.objects.filter(is_published=True)
        
        if not projects.exists():
            return Response({'results': []})
        
        projects_data = []
        for project in projects:
            tech_stack = ', '.join([tech.name for tech in project.tech_stack.all()])
            projects_data.append({
                'id': project.id,
                'slug': project.slug,
                'title': project.title,
                'description': project.short_description,
                'problem': project.problem_statement,
                'tech_stack': tech_stack,
                'category': project.category
            })
        
        prompt = f"""You are a project matching AI. Given a user search query and a list of projects, calculate how well each project matches the query.

User Query: "{query}"

Projects:
{json.dumps(projects_data, indent=2)}

For each project, analyze:
1. Title relevance
2. Description match
3. Technology stack alignment
4. Problem domain fit
5. Category relevance

Return ONLY a JSON array with this exact format (no markdown, no explanation):
[
  {{"id": 1, "match_percentage": 95, "reason": "Brief reason"}},
  {{"id": 2, "match_percentage": 78, "reason": "Brief reason"}}
]

Sort by match_percentage descending. Only include projects with match >= 30%."""

        api_key = settings.GROQ_API_KEY
        if not api_key:
            return Response({'error': 'AI service not configured'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000
        )
        
        response_text = completion.choices[0].message.content.strip()
        
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]
            response_text = response_text.strip()
        
        matches = json.loads(response_text)
        
        results = []
        for match in matches:
            try:
                project = projects.get(id=match['id'])
                results.append({
                    'project': ProjectSerializer(project).data,
                    'match_percentage': match['match_percentage'],
                    'reason': match['reason']
                })
            except Project.DoesNotExist:
                continue
        
        return Response({'results': results})
        
    except json.JSONDecodeError as e:
        print(f"JSON Parse Error: {str(e)}")
        print(f"Response: {response_text}")
        return Response({'error': 'Failed to parse AI response'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        print(f"AI Search Error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# Auto-Endpoint Detection Views

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_files(request, project_id):
    """Upload multiple files or a folder for endpoint detection."""
    from .models import ProjectUpload
    from .services.upload_service import UploadService
    from .tasks import start_upload_pipeline
    import tempfile
    import os
    
    try:
        project = Project.objects.get(id=project_id, owner=request.user)
    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if 'files' not in request.FILES:
        return Response({'error': 'No files provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    files = request.FILES.getlist('files')
    file_paths = request.POST.getlist('file_paths[]')
    generate_architecture = request.POST.get('generate_architecture', 'false').lower() == 'true'
    
    # Validate total size
    total_size = sum(f.size for f in files)
    if total_size > 50 * 1024 * 1024:  # 50MB
        return Response({'error': 'Total file size exceeds 50MB limit'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create upload record
    upload = ProjectUpload.objects.create(
        project=project,
        user=request.user,
        upload_method='files',
        file_size=total_size,
        status='uploading',
        current_message='Uploading files...',
        progress_percentage=5,
        generate_architecture=generate_architecture
    )
    
    try:
        # Save files to temp directory
        temp_dir = tempfile.mkdtemp(prefix='files_upload_')
        
        for i, file in enumerate(files):
            # Get relative path if provided, otherwise use filename
            rel_path = file_paths[i] if i < len(file_paths) else file.name
            
            # Create subdirectories if needed
            file_path = os.path.join(temp_dir, rel_path)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Save file
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
        
        # Store temp directory path
        upload.temp_directory = temp_dir
        upload.save()
        
        # Start background processing
        start_upload_pipeline(upload.id)
        
        return Response({
            'upload_id': str(upload.id),
            'message': 'Upload started. Check status for progress.'
        }, status=status.HTTP_202_ACCEPTED)
        
    except Exception as e:
        upload.status = 'failed'
        upload.error_message = f'Upload failed: {str(e)}'
        upload.save()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_zip(request, project_id):
    """Upload a zip file for endpoint detection."""
    from .models import ProjectUpload
    from .services.upload_service import UploadService
    from .tasks import start_upload_pipeline
    import tempfile
    
    try:
        project = Project.objects.get(id=project_id, owner=request.user)
    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if 'file' not in request.FILES:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    zip_file = request.FILES['file']
    generate_architecture = request.POST.get('generate_architecture', 'false').lower() == 'true'
    
    # Validate file size
    if zip_file.size > 100 * 1024 * 1024:  # 100MB
        return Response({'error': 'File size exceeds 100MB limit'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create upload record
    upload = ProjectUpload.objects.create(
        project=project,
        user=request.user,
        upload_method='zip',
        file_size=zip_file.size,
        status='uploading',
        current_message='Uploading file...',
        progress_percentage=5,
        generate_architecture=generate_architecture
    )
    
    try:
        # Save zip file to temp directory
        temp_dir = tempfile.mkdtemp(prefix='zip_upload_')
        zip_path = f"{temp_dir}/upload.zip"
        
        with open(zip_path, 'wb+') as destination:
            for chunk in zip_file.chunks():
                destination.write(chunk)
        
        # Extract zip
        upload_service = UploadService(upload)
        extracted_dir = upload_service.handle_zip_upload(open(zip_path, 'rb'))
        
        # Start background processing
        start_upload_pipeline(upload.id)
        
        return Response({
            'upload_id': str(upload.id),
            'message': 'Upload started. Check status for progress.'
        }, status=status.HTTP_202_ACCEPTED)
        
    except ValueError as e:
        upload.status = 'failed'
        upload.error_message = str(e)
        upload.save()
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        upload.status = 'failed'
        upload.error_message = f'Upload failed: {str(e)}'
        upload.save()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_github(request, project_id):
    """Upload a GitHub repository URL for endpoint detection."""
    from .models import ProjectUpload
    from .tasks import start_upload_pipeline
    
    try:
        project = Project.objects.get(id=project_id, owner=request.user)
    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    github_url = request.data.get('github_url')
    generate_architecture = request.data.get('generate_architecture', False)
    if not github_url:
        return Response({'error': 'GitHub URL is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create upload record
    upload = ProjectUpload.objects.create(
        project=project,
        user=request.user,
        upload_method='github',
        github_url=github_url,
        status='uploading',
        current_message='Preparing to clone repository...',
        progress_percentage=5,
        generate_architecture=generate_architecture
    )
    
    # Start background processing
    start_upload_pipeline(upload.id)
    
    return Response({
        'upload_id': str(upload.id),
        'message': 'GitHub clone started. Check status for progress.'
    }, status=status.HTTP_202_ACCEPTED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def upload_status(request, upload_id):
    """Get status of an upload/analysis job."""
    from .models import ProjectUpload
    from .serializers import ProjectUploadSerializer
    
    try:
        upload = ProjectUpload.objects.get(id=upload_id)
        
        # Check ownership
        if upload.project.owner != request.user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ProjectUploadSerializer(upload)
        return Response(serializer.data)
        
    except ProjectUpload.DoesNotExist:
        return Response({'error': 'Upload not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_retry(request, upload_id):
    """Retry a failed upload."""
    from .models import ProjectUpload
    from .tasks import start_upload_pipeline
    
    try:
        upload = ProjectUpload.objects.get(id=upload_id)
        
        # Check ownership
        if upload.project.owner != request.user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        if upload.status != 'failed':
            return Response({'error': 'Can only retry failed uploads'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Reset upload status
        upload.status = 'uploading'
        upload.progress_percentage = 5
        upload.current_message = 'Retrying...'
        upload.error_message = ''
        upload.save()
        
        # Start background processing
        start_upload_pipeline(upload.id)
        
        return Response({'message': 'Retry started'}, status=status.HTTP_202_ACCEPTED)
        
    except ProjectUpload.DoesNotExist:
        return Response({'error': 'Upload not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def translate_api(request, project_id):
    """Translate detected API endpoints to a different framework."""
    from .services.api_translator import APITranslator
    
    try:
        project = Project.objects.get(id=project_id, owner=request.user)
    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    target_framework = request.data.get('target_framework')
    if not target_framework:
        return Response({'error': 'target_framework is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get project endpoints
    endpoints = project.endpoints.all()
    if not endpoints:
        return Response({'error': 'No endpoints found for this project'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Convert endpoints to dictionary format
    endpoints_data = []
    for endpoint in endpoints:
        endpoint_data = {
            'method': endpoint.method,
            'path': endpoint.url,
            'name': endpoint.name,
            'description': endpoint.description,
            'auth_required': endpoint.auth_required,
            'path_parameters': endpoint.path_parameters or [],
            'query_parameters': endpoint.query_parameters or [],
            'request_schema': endpoint.request_schema or {},
            'response_schema': endpoint.response_schema or {}
        }
        endpoints_data.append(endpoint_data)
    
    try:
        # Translate the API
        translator = APITranslator()
        generated_code = translator.translate_endpoints(endpoints_data, target_framework)
        
        return Response({
            'success': True,
            'target_framework': target_framework,
            'generated_files': generated_code,
            'endpoints_count': len(endpoints_data)
        })
        
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': f'Translation failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='20/m', method='POST')
def execute_translated_endpoint(request):
    """Execute an endpoint as if it were implemented in a different framework."""
    from .services.translation_executor import TranslationExecutor
    
    endpoint_id = request.data.get('endpoint_id')
    target_framework = request.data.get('target_framework')
    custom_body = request.data.get('custom_body', {})
    custom_path_params = request.data.get('custom_path_params', {})
    
    if not endpoint_id:
        return Response({'error': 'endpoint_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not target_framework:
        return Response({'error': 'target_framework is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        endpoint = Endpoint.objects.select_related('project').get(id=endpoint_id)
    except Endpoint.DoesNotExist:
        return Response({'error': 'Endpoint not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # For translated endpoint testing, allow even unpublished projects
    # This is sandbox mode, so it's safe to test
    # if not endpoint.project.is_published:
    #     return Response({'error': 'Project is not published'}, status=status.HTTP_403_FORBIDDEN)
    
    # Check if sandbox exists
    has_sandbox = hasattr(endpoint.project, 'sandbox')
    if not has_sandbox:
        return Response({
            'mode': 'error',
            'status_code': 400,
            'data': None,
            'error': 'Sandbox not available. Please generate a sandbox first to test this API.',
            'framework': target_framework
        })
    
    # Execute the translated endpoint
    result = TranslationExecutor.execute_translated_endpoint(
        endpoint, target_framework, custom_body, custom_path_params
    )
    
    # Add execution mode
    result['mode'] = 'translated_sandbox'
    
    return Response(result)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def upload_delete(request, upload_id):
    """Delete an upload record."""
    from .models import ProjectUpload
    
    try:
        upload = ProjectUpload.objects.get(id=upload_id)
        
        # Check ownership
        if upload.project.owner != request.user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        upload.delete()
        return Response({'message': 'Upload deleted'}, status=status.HTTP_204_NO_CONTENT)
        
    except ProjectUpload.DoesNotExist:
        return Response({'error': 'Upload not found'}, status=status.HTTP_404_NOT_FOUND)



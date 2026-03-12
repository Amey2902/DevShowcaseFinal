from django.db import models
from django.contrib.auth.models import User
from slugify import slugify
import uuid


class Project(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    short_description = models.TextField(blank=True)
    problem_statement = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)
    github_url = models.URLField(blank=True)
    demo_url = models.URLField(blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Project.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']


class TechStack(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tech_stack')
    name = models.CharField(max_length=100)
    purpose = models.CharField(max_length=255)
    reason = models.TextField()
    alternative = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return f"{self.project.title} - {self.name}"


class ArchitectureNode(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='architecture_nodes')
    name = models.CharField(max_length=100)
    technology = models.CharField(max_length=100)
    description = models.TextField()
    x_position = models.FloatField(default=0)
    y_position = models.FloatField(default=0)
    
    # AI generation tracking fields
    is_ai_generated = models.BooleanField(default=False)
    ai_generation_source = models.CharField(max_length=100, blank=True)  # e.g., "package.json", "requirements.txt"
    created_by_upload = models.ForeignKey('ProjectUpload', on_delete=models.SET_NULL, null=True, blank=True)
    ai_confidence_score = models.FloatField(null=True, blank=True)  # 0.0-1.0 confidence in detection
    
    def __str__(self):
        project_title = self.project.title if self.project_id else "Unsaved Project"
        return f"{project_title} - {self.name}"


class Endpoint(models.Model):
    METHOD_CHOICES = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH'),
        ('DELETE', 'DELETE'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='endpoints')
    name = models.CharField(max_length=255)
    method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    url = models.URLField()
    headers = models.JSONField(default=dict, blank=True)
    sample_body = models.JSONField(default=dict, blank=True)
    description = models.TextField(blank=True)
    sample_response = models.JSONField(default=dict, blank=True, null=True)
    
    # Auto-detection fields
    detected_from_file = models.CharField(max_length=500, blank=True)
    detected_at_line = models.IntegerField(null=True, blank=True)
    path_parameters = models.JSONField(default=list, blank=True)
    query_parameters = models.JSONField(default=list, blank=True)
    auth_required = models.BooleanField(default=False)
    auth_type = models.CharField(max_length=50, blank=True)
    request_schema = models.JSONField(default=dict, blank=True)
    response_schema = models.JSONField(default=dict, blank=True)
    auto_detected = models.BooleanField(default=False)
    
    # Code samples for different languages
    code_samples = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"{self.method} {self.name}"


class TimelineEvent(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='timeline_events')
    title = models.CharField(max_length=255)
    description = models.TextField()
    event_date = models.DateField()
    
    def __str__(self):
        return f"{self.project.title} - {self.title}"
    
    class Meta:
        ordering = ['event_date']


class ProjectUpload(models.Model):
    """Track upload and analysis jobs for auto-endpoint detection."""
    
    STATUS_CHOICES = [
        ('uploading', 'Uploading'),
        ('extracting', 'Extracting Files'),
        ('scanning', 'Security Scanning'),
        ('analyzing', 'AI Analysis'),
        ('extracting_endpoints', 'Extracting Endpoints'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    UPLOAD_METHOD_CHOICES = [
        ('files', 'Multiple Files'),
        ('zip', 'Zip File'),
        ('github', 'GitHub URL'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='uploads')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Upload details
    upload_method = models.CharField(max_length=20, choices=UPLOAD_METHOD_CHOICES)
    github_url = models.URLField(blank=True, null=True)
    file_size = models.BigIntegerField(null=True)  # in bytes
    
    # Progress tracking
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='uploading')
    progress_percentage = models.IntegerField(default=0)
    current_message = models.TextField(blank=True)
    
    # Analysis results
    detected_language = models.CharField(max_length=50, blank=True)
    detected_framework = models.CharField(max_length=50, blank=True)
    endpoints_found = models.IntegerField(default=0)
    
    # Error handling
    error_message = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # File storage
    temp_directory = models.CharField(max_length=500, blank=True)
    
    # Architecture generation fields
    generate_architecture = models.BooleanField(default=False)
    architecture_nodes_created = models.IntegerField(default=0)
    architecture_analysis_data = models.JSONField(default=dict, blank=True)  # Store raw analysis for debugging
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.project.title} - {self.get_status_display()}"

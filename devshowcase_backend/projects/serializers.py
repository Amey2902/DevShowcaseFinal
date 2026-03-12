from rest_framework import serializers
from .models import Project, TechStack, ArchitectureNode, Endpoint, TimelineEvent, ProjectUpload
import re


class TechStackSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechStack
        fields = ['id', 'project', 'name', 'purpose', 'reason', 'alternative']


class ArchitectureNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArchitectureNode
        fields = ['id', 'project', 'name', 'technology', 'description', 'x_position', 'y_position']


class EndpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endpoint
        fields = ['id', 'project', 'name', 'method', 'url', 'headers', 'sample_body', 'description', 'sample_response',
                  'detected_from_file', 'detected_at_line', 'path_parameters', 'query_parameters', 
                  'auth_required', 'auth_type', 'request_schema', 'response_schema', 'auto_detected', 'code_samples']
    
    def validate_url(self, value):
        forbidden_patterns = [
            'admin', 'payment', 'stripe', 'razorpay', 'internal'
        ]
        value_lower = value.lower()
        for pattern in forbidden_patterns:
            if pattern in value_lower:
                raise serializers.ValidationError(f"URL contains forbidden pattern: {pattern}")
        
        return value
    
    def validate_headers(self, value):
        if not isinstance(value, dict):
            return value

        forbidden_keys = ['api-key', 'secret', 'bearer sk_']
        
        for key, val in value.items():
            key_lower = key.lower()
            val_str = str(val).lower()
            for forbidden in forbidden_keys:
                if forbidden in key_lower or forbidden in val_str:
                    raise serializers.ValidationError(f"Headers contain forbidden pattern: {forbidden}")
            
        return value


class TimelineEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimelineEvent
        fields = ['id', 'project', 'title', 'description', 'event_date']


class ProjectSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    sandbox_available = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = ['id', 'owner', 'owner_username', 'title', 'slug', 'short_description', 
                  'problem_statement', 'category', 'github_url', 'demo_url', 
                  'is_published', 'created_at', 'sandbox_available']
        read_only_fields = ['owner', 'slug', 'created_at', 'sandbox_available']
    
    def get_sandbox_available(self, obj):
        return hasattr(obj, 'sandbox')


class ProjectFullSerializer(serializers.ModelSerializer):
    tech_stack = TechStackSerializer(many=True, read_only=True)
    architecture_nodes = ArchitectureNodeSerializer(many=True, read_only=True)
    endpoints = EndpointSerializer(many=True, read_only=True)
    timeline_events = TimelineEventSerializer(many=True, read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    sandbox_available = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = ['id', 'owner', 'owner_username', 'title', 'slug', 'short_description',
                  'problem_statement', 'category', 'github_url', 'demo_url',
                  'is_published', 'created_at', 'tech_stack', 'architecture_nodes',
                  'endpoints', 'timeline_events', 'sandbox_available']
    
    def get_sandbox_available(self, obj):
        return hasattr(obj, 'sandbox')


class ProjectUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectUpload
        fields = ['id', 'project', 'user', 'upload_method', 'github_url', 'file_size',
                  'status', 'progress_percentage', 'current_message', 'detected_language',
                  'detected_framework', 'endpoints_found', 'error_message', 'created_at', 'completed_at']
        read_only_fields = ['id', 'status', 'progress_percentage', 'current_message', 
                            'detected_language', 'detected_framework', 'endpoints_found', 
                            'error_message', 'created_at', 'completed_at']
from rest_framework import serializers
from .models import SandboxEnvironment, SandboxCollection, SandboxRecord


class SandboxRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = SandboxRecord
        fields = ['id', 'data', 'created_at', 'updated_at']


class SandboxCollectionSerializer(serializers.ModelSerializer):
    records = SandboxRecordSerializer(many=True, read_only=True)
    
    class Meta:
        model = SandboxCollection
        fields = ['id', 'name', 'records']


class SandboxEnvironmentSerializer(serializers.ModelSerializer):
    collections = SandboxCollectionSerializer(many=True, read_only=True)
    
    class Meta:
        model = SandboxEnvironment
        fields = ['id', 'project', 'created_at', 'collections']

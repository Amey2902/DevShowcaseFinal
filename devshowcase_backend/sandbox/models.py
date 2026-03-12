from django.db import models
from projects.models import Project


class SandboxEnvironment(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='sandbox')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Sandbox for {self.project.title}"


class SandboxCollection(models.Model):
    environment = models.ForeignKey(SandboxEnvironment, on_delete=models.CASCADE, related_name='collections')
    name = models.CharField(max_length=100)
    
    class Meta:
        unique_together = ['environment', 'name']
    
    def __str__(self):
        return f"{self.environment.project.title} - {self.name}"


class SandboxRecord(models.Model):
    collection = models.ForeignKey(SandboxCollection, on_delete=models.CASCADE, related_name='records')
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.collection.name} - Record {self.id}"

from django.contrib import admin
from .models import Project, TechStack, ArchitectureNode, Endpoint, TimelineEvent

admin.site.register(Project)
admin.site.register(TechStack)
admin.site.register(ArchitectureNode)
admin.site.register(Endpoint)
admin.site.register(TimelineEvent)

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from projects.models import Project, TechStack, ArchitectureNode, Endpoint, TimelineEvent

print("\n=== USERS ===")
for user in User.objects.all():
    print(f"- {user.username} ({user.email})")

print("\n=== PROJECTS ===")
for project in Project.objects.all():
    print(f"- {project.title} by {project.owner.username} [{'Published' if project.is_published else 'Draft'}]")
    print(f"  Slug: {project.slug}")
    print(f"  Category: {project.category}")

print("\n=== TECH STACK ===")
for tech in TechStack.objects.all():
    print(f"- {tech.name} ({tech.project.title}): {tech.purpose}")

print("\n=== ARCHITECTURE NODES ===")
for node in ArchitectureNode.objects.all():
    print(f"- {node.name} ({node.technology}) in {node.project.title}")

print("\n=== ENDPOINTS ===")
for endpoint in Endpoint.objects.all():
    print(f"- {endpoint.method} {endpoint.name} ({endpoint.project.title})")
    print(f"  URL: {endpoint.url}")

print("\n=== TIMELINE EVENTS ===")
for event in TimelineEvent.objects.all():
    print(f"- {event.title} ({event.project.title}) - {event.event_date}")

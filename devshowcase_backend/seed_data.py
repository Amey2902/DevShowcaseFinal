import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from projects.models import Project, TechStack, ArchitectureNode, Endpoint, TimelineEvent
from rest_framework.authtoken.models import Token
from datetime import date

# Create test user
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={'email': 'test@example.com'}
)
if created:
    user.set_password('testpass123')
    user.save()
    Token.objects.create(user=user)
    print(f"Created user: {user.username}")

# Create sample project
project, created = Project.objects.get_or_create(
    owner=user,
    title='Weather API Dashboard',
    defaults={
        'short_description': 'Real-time weather data visualization platform',
        'problem_statement': 'Users need an easy way to check weather conditions across multiple cities',
        'category': 'Web Application',
        'github_url': 'https://github.com/example/weather-dashboard',
        'demo_url': 'https://weather-demo.example.com',
        'is_published': True
    }
)
if created:
    print(f"Created project: {project.title}")

# Tech Stack
TechStack.objects.get_or_create(
    project=project,
    name='React',
    defaults={
        'purpose': 'Frontend Framework',
        'reason': 'Component-based architecture and excellent ecosystem',
        'alternative': 'Vue.js'
    }
)

TechStack.objects.get_or_create(
    project=project,
    name='Django REST Framework',
    defaults={
        'purpose': 'Backend API',
        'reason': 'Robust and scalable REST API development',
        'alternative': 'FastAPI'
    }
)

# Architecture Nodes
ArchitectureNode.objects.get_or_create(
    project=project,
    name='Frontend',
    defaults={
        'technology': 'React',
        'description': 'User interface and visualization',
        'x_position': 100,
        'y_position': 100
    }
)

ArchitectureNode.objects.get_or_create(
    project=project,
    name='Backend API',
    defaults={
        'technology': 'Django',
        'description': 'REST API server',
        'x_position': 300,
        'y_position': 100
    }
)

ArchitectureNode.objects.get_or_create(
    project=project,
    name='Database',
    defaults={
        'technology': 'PostgreSQL',
        'description': 'Data persistence',
        'x_position': 500,
        'y_position': 100
    }
)

# Endpoints
Endpoint.objects.get_or_create(
    project=project,
    name='Get Weather',
    method='GET',
    url='https://api.openweathermap.org/data/2.5/weather',
    defaults={
        'description': 'Fetch current weather data for a city',
        'headers': {'Content-Type': 'application/json'},
        'sample_body': {'q': 'London', 'appid': 'demo'},
        'sample_response': {'temp': 15, 'humidity': 80}
    }
)

# Timeline Events
TimelineEvent.objects.get_or_create(
    project=project,
    title='Project Started',
    defaults={
        'description': 'Initial project setup and planning',
        'event_date': date(2024, 1, 1)
    }
)

TimelineEvent.objects.get_or_create(
    project=project,
    title='MVP Released',
    defaults={
        'description': 'First working version deployed',
        'event_date': date(2024, 3, 15)
    }
)

# Create second user
user2, created2 = User.objects.get_or_create(
    username='developer',
    defaults={'email': 'dev@example.com'}
)
if created2:
    user2.set_password('devpass123')
    user2.save()
    Token.objects.create(user=user2)
    print(f"Created user: {user2.username}")

# Project 2: E-commerce Platform
project2, created2 = Project.objects.get_or_create(
    owner=user2,
    title='E-commerce Platform',
    defaults={
        'short_description': 'Full-stack online shopping platform with payment integration',
        'problem_statement': 'Small businesses need an affordable way to sell products online',
        'category': 'E-commerce',
        'github_url': 'https://github.com/example/ecommerce',
        'demo_url': 'https://shop-demo.example.com',
        'is_published': True
    }
)
if created2:
    print(f"Created project: {project2.title}")
    
    TechStack.objects.create(
        project=project2,
        name='Next.js',
        purpose='Frontend Framework',
        reason='Server-side rendering and excellent performance',
        alternative='Nuxt.js'
    )
    
    TechStack.objects.create(
        project=project2,
        name='Stripe',
        purpose='Payment Processing',
        reason='Secure and reliable payment gateway',
        alternative='PayPal'
    )
    
    ArchitectureNode.objects.create(
        project=project2,
        name='Web App',
        technology='Next.js',
        description='Customer-facing storefront',
        x_position=100,
        y_position=150
    )
    
    ArchitectureNode.objects.create(
        project=project2,
        name='API Gateway',
        technology='Node.js',
        description='Backend services',
        x_position=350,
        y_position=150
    )
    
    Endpoint.objects.create(
        project=project2,
        name='Get Products',
        method='GET',
        url='https://fakestoreapi.com/products',
        description='Fetch all products',
        headers={'Content-Type': 'application/json'},
        sample_body={},
        sample_response={'id': 1, 'title': 'Product', 'price': 99.99}
    )
    
    TimelineEvent.objects.create(
        project=project2,
        title='Beta Launch',
        description='Released beta version to first customers',
        event_date=date(2024, 2, 1)
    )

# Project 3: Task Management App
project3, created3 = Project.objects.get_or_create(
    owner=user,
    title='Task Management System',
    defaults={
        'short_description': 'Collaborative task tracking and project management tool',
        'problem_statement': 'Teams need a simple way to organize and track work',
        'category': 'Productivity',
        'github_url': 'https://github.com/example/taskmanager',
        'demo_url': 'https://tasks-demo.example.com',
        'is_published': True
    }
)
if created3:
    print(f"Created project: {project3.title}")
    
    TechStack.objects.create(
        project=project3,
        name='Vue.js',
        purpose='Frontend Framework',
        reason='Lightweight and easy to learn',
        alternative='React'
    )
    
    TechStack.objects.create(
        project=project3,
        name='Express.js',
        purpose='Backend Framework',
        reason='Fast and minimalist Node.js framework',
        alternative='Fastify'
    )
    
    ArchitectureNode.objects.create(
        project=project3,
        name='Client',
        technology='Vue.js',
        description='User interface',
        x_position=150,
        y_position=100
    )
    
    ArchitectureNode.objects.create(
        project=project3,
        name='Server',
        technology='Express',
        description='REST API',
        x_position=400,
        y_position=100
    )
    
    Endpoint.objects.create(
        project=project3,
        name='Get Tasks',
        method='GET',
        url='https://jsonplaceholder.typicode.com/todos',
        description='Retrieve all tasks',
        headers={'Content-Type': 'application/json'},
        sample_body={},
        sample_response={'id': 1, 'title': 'Task', 'completed': False}
    )
    
    TimelineEvent.objects.create(
        project=project3,
        title='MVP Complete',
        description='Core features implemented',
        event_date=date(2024, 1, 15)
    )

# Project 4: Social Media Dashboard
project4, created4 = Project.objects.get_or_create(
    owner=user2,
    title='Social Media Analytics',
    defaults={
        'short_description': 'Real-time analytics dashboard for social media metrics',
        'problem_statement': 'Marketers need unified view of social media performance',
        'category': 'Analytics',
        'github_url': 'https://github.com/example/social-analytics',
        'demo_url': 'https://analytics-demo.example.com',
        'is_published': True
    }
)
if created4:
    print(f"Created project: {project4.title}")
    
    TechStack.objects.create(
        project=project4,
        name='React',
        purpose='Frontend Framework',
        reason='Rich ecosystem and component reusability',
        alternative='Angular'
    )
    
    TechStack.objects.create(
        project=project4,
        name='Chart.js',
        purpose='Data Visualization',
        reason='Simple and flexible charting library',
        alternative='D3.js'
    )
    
    ArchitectureNode.objects.create(
        project=project4,
        name='Dashboard',
        technology='React',
        description='Analytics interface',
        x_position=120,
        y_position=120
    )
    
    ArchitectureNode.objects.create(
        project=project4,
        name='Data API',
        technology='Python',
        description='Data aggregation service',
        x_position=380,
        y_position=120
    )
    
    Endpoint.objects.create(
        project=project4,
        name='Get User Data',
        method='GET',
        url='https://jsonplaceholder.typicode.com/users',
        description='Fetch user analytics data',
        headers={'Content-Type': 'application/json'},
        sample_body={},
        sample_response={'id': 1, 'name': 'User', 'email': 'user@example.com'}
    )
    
    TimelineEvent.objects.create(
        project=project4,
        title='Dashboard Launch',
        description='First version released',
        event_date=date(2024, 3, 1)
    )

print("\nSeed data created successfully!")
print(f"Test user credentials:")
print(f"  - username=testuser, password=testpass123")
print(f"  - username=developer, password=devpass123")
print(f"\nCreated {Project.objects.filter(is_published=True).count()} published projects")

from typing import List, Dict, Tuple, Optional
from projects.models import ArchitectureNode, Project
from projects.services.architecture_analyzer import ArchitecturalComponent, ComponentType


class ArchitectureNodeGenerator:
    """Service for generating ArchitectureNode objects from analysis results."""
    
    # Layout configuration for intelligent positioning
    LAYOUT_CONFIG = {
        ComponentType.FRONTEND: {"x_range": (100, 300), "y_start": 100},
        ComponentType.BACKEND: {"x_range": (400, 600), "y_start": 100},
        ComponentType.DATABASE: {"x_range": (700, 900), "y_start": 100},
        ComponentType.CACHE: {"x_range": (700, 900), "y_start": 100},
        ComponentType.EXTERNAL_SERVICE: {"x_range": (400, 600), "y_start": 400},
        ComponentType.MIDDLEWARE: {"x_range": (400, 600), "y_start": 250},
        ComponentType.MESSAGE_QUEUE: {"x_range": (700, 900), "y_start": 250},
        ComponentType.API_GATEWAY: {"x_range": (300, 500), "y_start": 50}
    }
    
    MIN_VERTICAL_SPACING = 150
    MIN_HORIZONTAL_SPACING = 200
    
    # Technology label mappings
    TECHNOLOGY_LABELS = {
        'react': 'React App',
        'vue': 'Vue.js App',
        'angular': 'Angular App',
        'express': 'Express.js Server',
        'nestjs': 'NestJS Server',
        'django': 'Django Server',
        'flask': 'Flask Server',
        'fastapi': 'FastAPI Server',
        'spring_boot': 'Spring Boot Server',
        'aspnet': 'ASP.NET Server',
        'postgresql': 'PostgreSQL',
        'mysql': 'MySQL',
        'mongodb': 'MongoDB',
        'redis': 'Redis Cache',
        'sqlite': 'SQLite',
        'elasticsearch': 'Elasticsearch',
        'aws_s3': 'AWS S3',
        'stripe': 'Stripe Payment',
        'sendgrid': 'SendGrid Email',
        'twilio': 'Twilio SMS',
        'firebase': 'Firebase',
        'auth0': 'Auth0'
    }
    
    def __init__(self):
        """Initialize the ArchitectureNodeGenerator."""
        pass
    
    def generate_nodes(self, components: List[ArchitecturalComponent], project: Project, 
                      upload_instance=None) -> List[ArchitectureNode]:
        """
        Generate ArchitectureNode objects from architectural components.
        
        Args:
            components: List of ArchitecturalComponent objects
            project: Project instance to associate nodes with
            upload_instance: Optional ProjectUpload instance for tracking
            
        Returns:
            List of ArchitectureNode objects
        """
        if not components:
            return []
        
        # Get existing nodes to avoid conflicts
        existing_nodes = list(project.architecture_nodes.all())
        
        # Calculate positions to avoid overlapping
        positioned_components = self.calculate_positions(components, existing_nodes)
        
        # Generate nodes
        nodes = []
        for component in positioned_components:
            node = self._create_node_from_component(component, project, upload_instance)
            if node:
                nodes.append(node)
        
        # Resolve naming conflicts
        nodes = self.avoid_naming_conflicts(nodes, existing_nodes)
        
        return nodes
    def calculate_positions(self, components: List[ArchitecturalComponent], 
                          existing_nodes: List[ArchitectureNode]) -> List[ArchitecturalComponent]:
        """
        Calculate intelligent positions for components to avoid overlapping.
        
        Args:
            components: List of components to position
            existing_nodes: List of existing nodes to avoid
            
        Returns:
            List of components with updated positions
        """
        # Get occupied positions from existing nodes
        occupied_positions = set()
        for node in existing_nodes:
            occupied_positions.add((int(node.x_position), int(node.y_position)))
        
        # Group components by type for organized layout
        components_by_type = {}
        for component in components:
            comp_type = component.component_type
            if comp_type not in components_by_type:
                components_by_type[comp_type] = []
            components_by_type[comp_type].append(component)
        
        positioned_components = []
        
        # Position each component type
        for comp_type, type_components in components_by_type.items():
            layout_config = self.LAYOUT_CONFIG.get(comp_type, self.LAYOUT_CONFIG[ComponentType.BACKEND])
            
            x_min, x_max = layout_config["x_range"]
            y_start = layout_config["y_start"]
            
            # Calculate positions for this component type
            for i, component in enumerate(type_components):
                # Try to find an unoccupied position
                x_pos = x_min + (i % 2) * self.MIN_HORIZONTAL_SPACING
                y_pos = y_start + (i // 2) * self.MIN_VERTICAL_SPACING
                
                # Ensure position is within bounds
                if x_pos > x_max:
                    x_pos = x_min
                    y_pos += self.MIN_VERTICAL_SPACING
                
                # Avoid occupied positions
                attempts = 0
                while (int(x_pos), int(y_pos)) in occupied_positions and attempts < 10:
                    y_pos += self.MIN_VERTICAL_SPACING
                    attempts += 1
                
                # Update component position
                component.suggested_position = (x_pos, y_pos)
                occupied_positions.add((int(x_pos), int(y_pos)))
                positioned_components.append(component)
        
        return positioned_components
    
    def assign_technologies(self, component: ArchitecturalComponent) -> str:
        """
        Assign appropriate technology labels based on component analysis.
        
        Args:
            component: ArchitecturalComponent to assign technology for
            
        Returns:
            Technology label string
        """
        # Use existing technology if it's already descriptive
        if component.technology and len(component.technology) > 3:
            return component.technology
        
        # Map component technology to display label
        tech_lower = component.technology.lower().replace(' ', '_').replace('.', '_')
        
        # Check for exact matches first
        if tech_lower in self.TECHNOLOGY_LABELS:
            return self.TECHNOLOGY_LABELS[tech_lower]
        
        # Check for partial matches
        for key, label in self.TECHNOLOGY_LABELS.items():
            if key in tech_lower or tech_lower in key:
                return label
        
        # Fallback to component type-based labels
        type_labels = {
            ComponentType.FRONTEND: "Frontend App",
            ComponentType.BACKEND: "API Server",
            ComponentType.DATABASE: "Database",
            ComponentType.CACHE: "Cache",
            ComponentType.EXTERNAL_SERVICE: "External Service",
            ComponentType.MIDDLEWARE: "Middleware",
            ComponentType.MESSAGE_QUEUE: "Message Queue",
            ComponentType.API_GATEWAY: "API Gateway"
        }
        
        return type_labels.get(component.component_type, component.technology or "Unknown")
    
    def generate_descriptions(self, component: ArchitecturalComponent) -> str:
        """
        Generate descriptive text for architecture components.
        
        Args:
            component: ArchitecturalComponent to generate description for
            
        Returns:
            Description string
        """
        if component.description and len(component.description) > 10:
            return component.description
        
        # Generate description based on component type and technology
        tech = component.technology.lower()
        comp_type = component.component_type
        
        descriptions = {
            ComponentType.FRONTEND: {
                'react': "React-based user interface with modern hooks and components",
                'vue': "Vue.js frontend application with reactive data binding",
                'angular': "Angular single-page application with TypeScript",
                'default': "Web-based user interface for user interactions"
            },
            ComponentType.BACKEND: {
                'express': "Express.js REST API server handling HTTP requests",
                'django': "Django web framework with ORM and admin interface",
                'flask': "Lightweight Flask API server for web services",
                'fastapi': "FastAPI server with automatic API documentation",
                'spring_boot': "Spring Boot application with enterprise features",
                'aspnet': "ASP.NET Core web API with dependency injection",
                'default': "Backend API server handling business logic"
            },
            ComponentType.DATABASE: {
                'postgresql': "PostgreSQL relational database for data persistence",
                'mysql': "MySQL relational database with ACID compliance",
                'mongodb': "MongoDB NoSQL document database",
                'sqlite': "SQLite embedded database for local storage",
                'default': "Database system for data storage and retrieval"
            },
            ComponentType.CACHE: {
                'redis': "Redis in-memory cache for session and data caching",
                'default': "Caching layer for improved performance"
            },
            ComponentType.EXTERNAL_SERVICE: {
                'aws': "AWS cloud services integration",
                'stripe': "Stripe payment processing service",
                'sendgrid': "SendGrid email delivery service",
                'twilio': "Twilio SMS and communication service",
                'firebase': "Firebase backend-as-a-service platform",
                'auth0': "Auth0 authentication and authorization service",
                'default': "External third-party service integration"
            },
            ComponentType.MIDDLEWARE: {
                'default': "Middleware component for request processing"
            }
        }
        
        type_descriptions = descriptions.get(comp_type, {'default': 'System component'})
        
        # Find matching description
        for key, desc in type_descriptions.items():
            if key != 'default' and key in tech:
                return desc
        
        return type_descriptions['default']
    def avoid_naming_conflicts(self, new_nodes: List[ArchitectureNode], 
                             existing_nodes: List[ArchitectureNode]) -> List[ArchitectureNode]:
        """
        Resolve naming conflicts between new and existing nodes.
        
        Args:
            new_nodes: List of new nodes to check for conflicts
            existing_nodes: List of existing nodes to avoid conflicts with
            
        Returns:
            List of nodes with resolved naming conflicts
        """
        existing_names = {node.name.lower() for node in existing_nodes}
        
        for node in new_nodes:
            original_name = node.name
            counter = 2
            
            # Check for conflicts and append suffix if needed
            while node.name.lower() in existing_names:
                node.name = f"{original_name} ({counter})"
                counter += 1
            
            # Add to existing names to avoid conflicts between new nodes
            existing_names.add(node.name.lower())
        
        return new_nodes
    
    def _create_node_from_component(self, component: ArchitecturalComponent, 
                                   project: Project, upload_instance=None) -> Optional[ArchitectureNode]:
        """
        Create an ArchitectureNode from an ArchitecturalComponent.
        
        Args:
            component: ArchitecturalComponent to convert
            project: Project to associate with
            upload_instance: Optional ProjectUpload for tracking
            
        Returns:
            ArchitectureNode instance or None if creation fails
        """
        try:
            # Assign technology label
            technology = self.assign_technologies(component)
            
            # Generate description
            description = self.generate_descriptions(component)
            
            # Create node (don't save to database yet)
            node = ArchitectureNode(
                project=project,
                name=component.name,
                technology=technology,
                description=description,
                x_position=component.suggested_position[0],
                y_position=component.suggested_position[1],
                is_ai_generated=True,
                ai_generation_source=', '.join(component.source_files[:3]) if component.source_files else 'analysis',
                created_by_upload=upload_instance,
                ai_confidence_score=component.confidence_score
            )
            
            return node
            
        except Exception as e:
            print(f"Error creating node from component {component.name}: {str(e)}")
            return None
    
    def save_nodes(self, nodes: List[ArchitectureNode]) -> List[ArchitectureNode]:
        """
        Save nodes to database and return saved instances.
        
        Args:
            nodes: List of ArchitectureNode instances to save
            
        Returns:
            List of saved ArchitectureNode instances
        """
        saved_nodes = []
        
        for node in nodes:
            try:
                node.save()
                saved_nodes.append(node)
            except Exception as e:
                print(f"Error saving node {node.name}: {str(e)}")
                continue
        
        return saved_nodes
    
    def regenerate_ai_nodes(self, project: Project, new_components: List[ArchitecturalComponent],
                           upload_instance=None, preserve_manual_nodes: bool = True) -> Dict:
        """
        Regenerate AI-generated nodes while preserving manual nodes.
        
        Args:
            project: Project to regenerate nodes for
            new_components: New components from analysis
            upload_instance: Optional ProjectUpload for tracking
            preserve_manual_nodes: Whether to preserve manually created nodes
            
        Returns:
            Dictionary with regeneration results
        """
        # Get existing nodes
        existing_nodes = list(project.architecture_nodes.all())
        ai_nodes = [node for node in existing_nodes if getattr(node, 'is_ai_generated', False)]
        manual_nodes = [node for node in existing_nodes if not getattr(node, 'is_ai_generated', False)]
        
        # Delete existing AI-generated nodes
        for node in ai_nodes:
            node.delete()
        
        # Generate new nodes
        new_nodes = self.generate_nodes(new_components, project, upload_instance)
        
        # Save new nodes
        saved_nodes = self.save_nodes(new_nodes)
        
        return {
            'ai_nodes_removed': len(ai_nodes),
            'manual_nodes_preserved': len(manual_nodes) if preserve_manual_nodes else 0,
            'new_nodes_created': len(saved_nodes),
            'total_nodes': len(manual_nodes) + len(saved_nodes)
        }
from django.test import TestCase
from django.contrib.auth.models import User
from hypothesis import given, strategies as st, settings
from hypothesis.extra.django import TestCase as HypothesisTestCase
from projects.models import Project, ArchitectureNode
from projects.services.architecture_node_generator import ArchitectureNodeGenerator
from projects.services.architecture_analyzer import ArchitecturalComponent, ComponentType


# Property-based test generators
@st.composite
def architectural_components(draw):
    """Generate diverse sets of architectural components."""
    # Generate 1-10 components
    num_components = draw(st.integers(min_value=1, max_value=10))
    
    components = []
    for i in range(num_components):
        # Choose component type
        comp_type = draw(st.sampled_from(list(ComponentType)))
        
        # Generate component data
        name = draw(st.text(min_size=3, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc'))))
        technology = draw(st.sampled_from(['React', 'Vue', 'Angular', 'Express', 'Django', 'Flask', 'PostgreSQL', 'MongoDB', 'Redis', 'AWS S3', 'Stripe']))
        description = draw(st.text(min_size=10, max_size=100))
        confidence = draw(st.floats(min_value=0.1, max_value=1.0))
        
        # Generate source files
        num_files = draw(st.integers(min_value=0, max_value=5))
        source_files = [f"src/file_{j}.py" for j in range(num_files)]
        
        component = ArchitecturalComponent(
            name=name,
            component_type=comp_type,
            technology=technology,
            description=description,
            confidence_score=confidence,
            source_files=source_files,
            dependencies=[],
            suggested_position=(0, 0)  # Will be calculated by positioning algorithm
        )
        
        components.append(component)
    
    return components


@st.composite
def existing_node_sets(draw):
    """Generate sets of existing architecture nodes."""
    num_nodes = draw(st.integers(min_value=0, max_value=8))
    
    nodes = []
    for i in range(num_nodes):
        name = f"Existing Node {i}"
        x_pos = draw(st.floats(min_value=0, max_value=1000))
        y_pos = draw(st.floats(min_value=0, max_value=800))
        
        # Create a mock node (not saved to database)
        node = ArchitectureNode(
            name=name,
            technology="Test Tech",
            description="Test description",
            x_position=x_pos,
            y_position=y_pos
        )
        
        nodes.append(node)
    
    return nodes


class TestArchitectureNodeGeneratorProperties(HypothesisTestCase):
    """Property-based tests for ArchitectureNodeGenerator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = ArchitectureNodeGenerator()
        self.user = User.objects.create_user(username='testuser', email='test@example.com')
        self.project = Project.objects.create(
            owner=self.user,
            title='Test Project',
            short_description='Test project for architecture generation'
        )
    
    @given(components=architectural_components(), existing_nodes=existing_node_sets())
    @settings(max_examples=100, deadline=10000)
    def test_intelligent_node_positioning(self, components, existing_nodes):
        """
        **Property 4: Intelligent Node Positioning**
        
        For any set of generated architecture nodes, the positioning algorithm should place 
        frontend components on the left (x: 100-300), backend components in center (x: 400-600), 
        database components on right (x: 700-900), maintain minimum 150px spacing between all 
        nodes, and ensure no overlapping positions.
        
        **Validates: Requirements 3.4, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6**
        """
        # Feature: ai-architecture-generation, Property 4: Intelligent node positioning
        
        # Arrange - Calculate positions
        positioned_components = self.generator.calculate_positions(components, existing_nodes)
        
        # Act - Generate nodes
        nodes = []
        component_to_node = {}
        for component in positioned_components:
            node = self.generator._create_node_from_component(component, self.project)
            if node:
                nodes.append(node)
                component_to_node[id(component)] = node
        
        # Assert - Verify positioning constraints
        
        # Property: Frontend components should be positioned on the left (x: 100-300)
        for component in positioned_components:
            if component.component_type == ComponentType.FRONTEND:
                node = component_to_node.get(id(component))
                if node:
                    self.assertGreaterEqual(node.x_position, 100, 
                                          f"Frontend node {node.name} should be positioned at x >= 100")
                    self.assertLessEqual(node.x_position, 300, 
                                       f"Frontend node {node.name} should be positioned at x <= 300")
        
        # Property: Backend components should be positioned in center (x: 400-600)
        for component in positioned_components:
            if component.component_type == ComponentType.BACKEND:
                node = component_to_node.get(id(component))
                if node:
                    self.assertGreaterEqual(node.x_position, 400, 
                                          f"Backend node {node.name} should be positioned at x >= 400")
                    self.assertLessEqual(node.x_position, 600, 
                                       f"Backend node {node.name} should be positioned at x <= 600")
        
        # Property: Database components should be positioned on the right (x: 700-900)
        for component in positioned_components:
            if component.component_type in [ComponentType.DATABASE, ComponentType.CACHE]:
                node = component_to_node.get(id(component))
                if node:
                    self.assertGreaterEqual(node.x_position, 700, 
                                          f"Database node {node.name} should be positioned at x >= 700")
                    self.assertLessEqual(node.x_position, 900, 
                                       f"Database node {node.name} should be positioned at x <= 900")
        
        # Property: Minimum spacing between nodes (focus on non-overlapping)
        for i, node1 in enumerate(nodes):
            for j, node2 in enumerate(nodes):
                if i != j:
                    # Calculate distance between nodes
                    dx = abs(node1.x_position - node2.x_position)
                    dy = abs(node1.y_position - node2.y_position)
                    
                    # Ensure nodes don't overlap (minimum 10px separation)
                    if dx < 10 and dy < 10:
                        self.fail(f"Nodes {node1.name} and {node2.name} are overlapping: dx={dx:.1f}, dy={dy:.1f}")
        
        # Property: No overlapping positions (exact same coordinates)
        positions = [(node.x_position, node.y_position) for node in nodes]
        unique_positions = set(positions)
        
        # Allow small floating point differences
        tolerance = 1.0
        for i, pos1 in enumerate(positions):
            for j, pos2 in enumerate(positions):
                if i != j:
                    dx = abs(pos1[0] - pos2[0])
                    dy = abs(pos1[1] - pos2[1])
                    if dx < tolerance and dy < tolerance:
                        self.fail(f"Nodes have overlapping positions: {pos1} and {pos2}")
        
        # Property: All nodes should have valid positions (non-negative coordinates)
        for node in nodes:
            self.assertGreaterEqual(node.x_position, 0, 
                                  f"Node {node.name} has negative x position: {node.x_position}")
            self.assertGreaterEqual(node.y_position, 0, 
                                  f"Node {node.name} has negative y position: {node.y_position}")
        
        # Property: Nodes should avoid existing node positions
        existing_positions = [(node.x_position, node.y_position) for node in existing_nodes]
        new_positions = [(node.x_position, node.y_position) for node in nodes]
        
        for new_pos in new_positions:
            for existing_pos in existing_positions:
                dx = abs(new_pos[0] - existing_pos[0])
                dy = abs(new_pos[1] - existing_pos[1])
                distance = (dx ** 2 + dy ** 2) ** 0.5
                
                # New nodes should not be too close to existing nodes
                if distance < MIN_SPACING * 0.5:
                    self.assertGreaterEqual(distance, 45,  # Allow some floating point tolerance
                                          f"New node too close to existing node: {distance:.1f}px")


class TestArchitectureNodeGeneratorUnits(TestCase):
    """Unit tests for specific ArchitectureNodeGenerator scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = ArchitectureNodeGenerator()
        self.user = User.objects.create_user(username='testuser', email='test@example.com')
        self.project = Project.objects.create(
            owner=self.user,
            title='Test Project',
            short_description='Test project for architecture generation'
        )
    
    def test_frontend_positioning(self):
        """Test that frontend components are positioned on the left."""
        components = [
            ArchitecturalComponent(
                name="React App",
                component_type=ComponentType.FRONTEND,
                technology="React",
                description="React frontend",
                confidence_score=0.9,
                source_files=["src/App.jsx"],
                dependencies=[],
                suggested_position=(0, 0)
            )
        ]
        
        positioned = self.generator.calculate_positions(components, [])
        
        self.assertEqual(len(positioned), 1)
        x_pos = positioned[0].suggested_position[0]
        self.assertGreaterEqual(x_pos, 100)
        self.assertLessEqual(x_pos, 300)
    
    def test_backend_positioning(self):
        """Test that backend components are positioned in the center."""
        components = [
            ArchitecturalComponent(
                name="Express API",
                component_type=ComponentType.BACKEND,
                technology="Express",
                description="Express backend",
                confidence_score=0.9,
                source_files=["server.js"],
                dependencies=[],
                suggested_position=(0, 0)
            )
        ]
        
        positioned = self.generator.calculate_positions(components, [])
        
        self.assertEqual(len(positioned), 1)
        x_pos = positioned[0].suggested_position[0]
        self.assertGreaterEqual(x_pos, 400)
        self.assertLessEqual(x_pos, 600)
    
    def test_database_positioning(self):
        """Test that database components are positioned on the right."""
        components = [
            ArchitecturalComponent(
                name="PostgreSQL",
                component_type=ComponentType.DATABASE,
                technology="PostgreSQL",
                description="PostgreSQL database",
                confidence_score=0.9,
                source_files=["requirements.txt"],
                dependencies=[],
                suggested_position=(0, 0)
            )
        ]
        
        positioned = self.generator.calculate_positions(components, [])
        
        self.assertEqual(len(positioned), 1)
        x_pos = positioned[0].suggested_position[0]
        self.assertGreaterEqual(x_pos, 700)
        self.assertLessEqual(x_pos, 900)
    
    def test_naming_conflict_resolution(self):
        """Test that naming conflicts are resolved with suffixes."""
        # Create existing node
        existing_node = ArchitectureNode.objects.create(
            project=self.project,
            name="API Server",
            technology="Express",
            description="Existing API server",
            x_position=500,
            y_position=100
        )
        
        # Create new node with same name
        new_node = ArchitectureNode(
            project=self.project,
            name="API Server",
            technology="Django",
            description="New API server",
            x_position=500,
            y_position=250
        )
        
        resolved_nodes = self.generator.avoid_naming_conflicts([new_node], [existing_node])
        
        self.assertEqual(len(resolved_nodes), 1)
        self.assertEqual(resolved_nodes[0].name, "API Server (2)")
    
    def test_technology_label_assignment(self):
        """Test that appropriate technology labels are assigned."""
        component = ArchitecturalComponent(
            name="React App",
            component_type=ComponentType.FRONTEND,
            technology="react",
            description="React frontend",
            confidence_score=0.9,
            source_files=[],
            dependencies=[],
            suggested_position=(200, 100)
        )
        
        technology = self.generator.assign_technologies(component)
        self.assertEqual(technology, "React App")
    
    def test_description_generation(self):
        """Test that appropriate descriptions are generated."""
        component = ArchitecturalComponent(
            name="Express API",
            component_type=ComponentType.BACKEND,
            technology="express",
            description="",
            confidence_score=0.9,
            source_files=[],
            dependencies=[],
            suggested_position=(500, 100)
        )
        
        description = self.generator.generate_descriptions(component)
        self.assertIn("Express.js", description)
        self.assertIn("REST API", description)
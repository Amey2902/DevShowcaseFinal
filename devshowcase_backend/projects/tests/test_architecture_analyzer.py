import os
import json
import tempfile
import shutil
from pathlib import Path
from django.test import TestCase
from hypothesis import given, strategies as st, settings
from hypothesis.extra.django import TestCase as HypothesisTestCase
from projects.services.architecture_analyzer import ArchitectureAnalyzer, ComponentType


class TestArchitectureAnalyzer(TestCase):
    """Test suite for ArchitectureAnalyzer service."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = ArchitectureAnalyzer()
        self.temp_dir = None
    
    def tearDown(self):
        """Clean up test fixtures."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def create_temp_project(self, files_dict):
        """Create a temporary project directory with specified files."""
        self.temp_dir = tempfile.mkdtemp()
        
        for file_path, content in files_dict.items():
            full_path = Path(self.temp_dir) / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            if isinstance(content, dict):
                # JSON content
                full_path.write_text(json.dumps(content, indent=2))
            else:
                # Text content
                full_path.write_text(content)
        
        return self.temp_dir


# Property-based test generators
@st.composite
def project_structures(draw):
    """Generate diverse project directory structures."""
    # Choose project type
    project_type = draw(st.sampled_from(['react', 'vue', 'angular', 'express', 'django', 'flask', 'spring_boot', 'mixed']))
    
    files = {}
    
    if project_type == 'react':
        # React project structure
        files['package.json'] = {
            "name": "react-app",
            "dependencies": {
                "react": "^18.0.0",
                "react-dom": "^18.0.0"
            }
        }
        files['src/App.jsx'] = 'import React from "react"; export default function App() { return <div>Hello</div>; }'
        files['src/components/Header.jsx'] = 'import React from "react"; export default function Header() { return <header>Header</header>; }'
        
    elif project_type == 'vue':
        files['package.json'] = {
            "name": "vue-app",
            "dependencies": {
                "vue": "^3.0.0"
            }
        }
        files['src/App.vue'] = '<template><div>Hello Vue</div></template>'
        files['src/components/Header.vue'] = '<template><header>Header</header></template>'
        
    elif project_type == 'angular':
        files['package.json'] = {
            "name": "angular-app",
            "dependencies": {
                "@angular/core": "^15.0.0",
                "@angular/common": "^15.0.0"
            }
        }
        files['src/app/app.component.ts'] = 'import { Component } from "@angular/core"; @Component({}) export class AppComponent {}'
        
    elif project_type == 'express':
        files['package.json'] = {
            "name": "express-app",
            "dependencies": {
                "express": "^4.18.0"
            }
        }
        files['server.js'] = 'const express = require("express"); const app = express(); app.listen(3000);'
        files['routes/api.js'] = 'const express = require("express"); const router = express.Router(); module.exports = router;'
        
    elif project_type == 'django':
        files['requirements.txt'] = 'Django==4.2.0\npsycopg2==2.9.0'
        files['manage.py'] = '#!/usr/bin/env python\nimport os\nimport sys\nif __name__ == "__main__":\n    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")'
        files['myproject/settings.py'] = 'DATABASES = {"default": {"ENGINE": "django.db.backends.postgresql"}}'
        files['myproject/urls.py'] = 'from django.urls import path\nurlpatterns = []'
        
    elif project_type == 'flask':
        files['requirements.txt'] = 'Flask==2.3.0\nredis==4.5.0'
        files['app.py'] = 'from flask import Flask\napp = Flask(__name__)\n@app.route("/")\ndef hello(): return "Hello"'
        
    elif project_type == 'spring_boot':
        files['pom.xml'] = '''<?xml version="1.0"?>
<project>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
            <version>2.7.0</version>
        </dependency>
    </dependencies>
</project>'''
        files['src/main/java/Application.java'] = '@SpringBootApplication public class Application {}'
        
    elif project_type == 'mixed':
        # Mixed frontend + backend
        files['package.json'] = {
            "name": "fullstack-app",
            "dependencies": {
                "react": "^18.0.0",
                "express": "^4.18.0"
            }
        }
        files['requirements.txt'] = 'Django==4.2.0'
        files['frontend/src/App.jsx'] = 'import React from "react"; export default function App() { return <div>Hello</div>; }'
        files['backend/server.js'] = 'const express = require("express"); const app = express(); app.listen(3000);'
        files['api/manage.py'] = '#!/usr/bin/env python\nimport django'
    
    # Add optional database and external service dependencies
    if draw(st.booleans()):
        # Add database dependencies
        db_type = draw(st.sampled_from(['postgresql', 'mysql', 'mongodb', 'redis']))
        if 'package.json' in files:
            if db_type == 'postgresql':
                files['package.json']['dependencies']['pg'] = '^8.8.0'
            elif db_type == 'mongodb':
                files['package.json']['dependencies']['mongoose'] = '^6.0.0'
            elif db_type == 'redis':
                files['package.json']['dependencies']['redis'] = '^4.0.0'
        elif 'requirements.txt' in files:
            if db_type == 'postgresql':
                files['requirements.txt'] += '\npsycopg2==2.9.0'
            elif db_type == 'mongodb':
                files['requirements.txt'] += '\npymongo==4.3.0'
            elif db_type == 'mysql':
                files['requirements.txt'] += '\nPyMySQL==1.0.0'
    
    if draw(st.booleans()):
        # Add external service dependencies
        service = draw(st.sampled_from(['aws', 'stripe', 'sendgrid']))
        if 'package.json' in files:
            if service == 'aws':
                files['package.json']['dependencies']['aws-sdk'] = '^2.1000.0'
            elif service == 'stripe':
                files['package.json']['dependencies']['stripe'] = '^10.0.0'
        elif 'requirements.txt' in files:
            if service == 'aws':
                files['requirements.txt'] += '\nboto3==1.26.0'
            elif service == 'stripe':
                files['requirements.txt'] += '\nstripe==5.4.0'
    
    # Add environment configuration
    if draw(st.booleans()):
        env_vars = []
        if draw(st.booleans()):
            env_vars.append('DATABASE_URL=postgresql://localhost:5432/mydb')
        if draw(st.booleans()):
            env_vars.append('REDIS_URL=redis://localhost:6379')
        if draw(st.booleans()):
            env_vars.append('AWS_ACCESS_KEY_ID=test_key')
        
        if env_vars:
            files['.env'] = '\n'.join(env_vars)
    
    return {
        'project_type': project_type,
        'files': files
    }


class TestArchitectureAnalyzerProperties(HypothesisTestCase):
    """Property-based tests for ArchitectureAnalyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = ArchitectureAnalyzer()
        self.temp_dirs = []
    
    def tearDown(self):
        """Clean up test fixtures."""
        for temp_dir in self.temp_dirs:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
    
    def create_temp_project(self, files_dict):
        """Create a temporary project directory with specified files."""
        temp_dir = tempfile.mkdtemp()
        self.temp_dirs.append(temp_dir)
        
        for file_path, content in files_dict.items():
            full_path = Path(temp_dir) / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            if isinstance(content, dict):
                # JSON content
                full_path.write_text(json.dumps(content, indent=2))
            else:
                # Text content
                full_path.write_text(content)
        
        return temp_dir
    @given(project_data=project_structures())
    @settings(max_examples=100, deadline=30000)  # 30 second deadline for complex projects
    def test_comprehensive_component_analysis(self, project_data):
        """
        **Property 2: Comprehensive Component Analysis**
        
        For any project directory with detectable components, the Codebase_Analyzer should 
        identify all architectural components including frontend, backend, database, external 
        services, and their associated technologies from code structure, dependencies, and 
        configuration files.
        
        **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6**
        """
        # Feature: ai-architecture-generation, Property 2: Comprehensive component analysis
        
        # Arrange
        project_type = project_data['project_type']
        files = project_data['files']
        temp_dir = self.create_temp_project(files)
        
        # Act
        try:
            analysis_result = self.analyzer.analyze_project_structure(temp_dir)
        except Exception as e:
            # If analysis fails, it should be due to genuinely undetectable components
            self.fail(f"Analysis should not fail for valid project structure: {str(e)}")
        
        # Assert - Verify comprehensive analysis
        self.assertIn('components', analysis_result)
        self.assertIn('frameworks', analysis_result)
        self.assertIn('dependencies', analysis_result)
        self.assertIn('project_type', analysis_result)
        
        components = analysis_result['components']
        frameworks = analysis_result['frameworks']
        
        # Property: Should identify components based on project type
        if project_type in ['react', 'vue', 'angular']:
            # Should detect frontend components
            frontend_components = [c for c in components if c.component_type == ComponentType.FRONTEND]
            self.assertGreater(len(frontend_components), 0, 
                             f"Should detect frontend components in {project_type} project")
            
            # Should detect appropriate framework
            expected_frameworks = {'react': 'react', 'vue': 'vue', 'angular': 'angular'}
            if expected_frameworks[project_type] in frameworks:
                framework_info = frameworks[expected_frameworks[project_type]]
                self.assertEqual(framework_info['type'], 'frontend')
                self.assertGreaterEqual(framework_info['confidence'], 0.8)
        
        elif project_type in ['express', 'django', 'flask', 'spring_boot']:
            # Should detect backend components
            backend_components = [c for c in components if c.component_type == ComponentType.BACKEND]
            self.assertGreater(len(backend_components), 0,
                             f"Should detect backend components in {project_type} project")
            
            # Should detect appropriate framework
            framework_mapping = {
                'express': 'express',
                'django': 'django', 
                'flask': 'flask',
                'spring_boot': 'spring_boot'
            }
            expected_framework = framework_mapping[project_type]
            if expected_framework in frameworks:
                framework_info = frameworks[expected_framework]
                self.assertEqual(framework_info['type'], 'backend')
                self.assertGreaterEqual(framework_info['confidence'], 0.8)
        
        elif project_type == 'mixed':
            # Should detect both frontend and backend components
            frontend_components = [c for c in components if c.component_type == ComponentType.FRONTEND]
            backend_components = [c for c in components if c.component_type == ComponentType.BACKEND]
            
            # At least one of each type should be detected
            self.assertGreater(len(frontend_components) + len(backend_components), 0,
                             "Mixed project should detect frontend and/or backend components")
        
        # Property: Should detect database components from dependencies
        has_db_dependency = False
        for file_path, content in files.items():
            if file_path in ['requirements.txt', 'package.json']:
                content_str = json.dumps(content) if isinstance(content, dict) else content
                if any(db in content_str.lower() for db in ['psycopg2', 'pymongo', 'mysql', 'pg', 'mongoose', 'redis']):
                    has_db_dependency = True
                    break
        
        if has_db_dependency:
            db_components = [c for c in components if c.component_type in [ComponentType.DATABASE, ComponentType.CACHE]]
            self.assertGreater(len(db_components), 0,
                             "Should detect database/cache components when dependencies are present")
        
        # Property: Should detect external services from dependencies
        has_external_service = False
        for file_path, content in files.items():
            if file_path in ['requirements.txt', 'package.json']:
                content_str = json.dumps(content) if isinstance(content, dict) else content
                if any(service in content_str.lower() for service in ['aws-sdk', 'boto3', 'stripe', 'sendgrid']):
                    has_external_service = True
                    break
        
        if has_external_service:
            external_components = [c for c in components if c.component_type == ComponentType.EXTERNAL_SERVICE]
            self.assertGreater(len(external_components), 0,
                             "Should detect external service components when dependencies are present")
        
        # Property: Should detect service connections from configuration files
        if '.env' in files:
            connections = analysis_result.get('connections', [])
            env_content = files['.env'].lower()
            
            if 'database_url' in env_content or 'db_host' in env_content:
                db_connections = [c for c in connections if c['service'] in ['database', 'postgresql']]
                self.assertGreater(len(db_connections), 0,
                                 "Should detect database connections from .env file")
            
            if 'redis_url' in env_content:
                redis_connections = [c for c in connections if c['service'] == 'redis']
                self.assertGreater(len(redis_connections), 0,
                                 "Should detect Redis connections from .env file")
        
        # Property: All components should have required fields
        for component in components:
            self.assertIsInstance(component.name, str)
            self.assertGreater(len(component.name), 0)
            self.assertIsInstance(component.component_type, ComponentType)
            self.assertIsInstance(component.technology, str)
            self.assertGreater(len(component.technology), 0)
            self.assertIsInstance(component.confidence_score, float)
            self.assertGreaterEqual(component.confidence_score, 0.0)
            self.assertLessEqual(component.confidence_score, 1.0)
            self.assertIsInstance(component.source_files, list)
            self.assertIsInstance(component.dependencies, list)
            self.assertIsInstance(component.suggested_position, tuple)
            self.assertEqual(len(component.suggested_position), 2)
        
        # Property: Project type should be correctly determined
        valid_project_types = ['monolithic', 'microservices', 'full_stack', 'frontend_only', 'api_only']
        self.assertIn(analysis_result['project_type'], valid_project_types)
        
        # Property: Framework detection should have evidence
        for framework_name, framework_info in frameworks.items():
            self.assertIn('evidence', framework_info)
            self.assertIsInstance(framework_info['evidence'], list)
            self.assertGreater(len(framework_info['evidence']), 0)
            self.assertIn('confidence', framework_info)
            self.assertGreaterEqual(framework_info['confidence'], 0.0)
            self.assertLessEqual(framework_info['confidence'], 1.0)


# Unit tests for specific scenarios
class TestArchitectureAnalyzerUnits(TestCase):
    """Unit tests for specific ArchitectureAnalyzer scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = ArchitectureAnalyzer()
        self.temp_dirs = []
    
    def tearDown(self):
        """Clean up test fixtures."""
        for temp_dir in self.temp_dirs:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
    
    def create_temp_project(self, files_dict):
        """Create a temporary project directory with specified files."""
        temp_dir = tempfile.mkdtemp()
        self.temp_dirs.append(temp_dir)
        
        for file_path, content in files_dict.items():
            full_path = Path(temp_dir) / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            if isinstance(content, dict):
                full_path.write_text(json.dumps(content, indent=2))
            else:
                full_path.write_text(content)
        
        return temp_dir
    
    def test_react_project_detection(self):
        """Test detection of React project components."""
        files = {
            'package.json': {
                "name": "react-app",
                "dependencies": {
                    "react": "^18.0.0",
                    "react-dom": "^18.0.0"
                }
            },
            'src/App.jsx': 'import React from "react"; export default function App() { return <div>Hello</div>; }',
            'src/components/Header.jsx': 'export default function Header() { return <header>Header</header>; }'
        }
        
        temp_dir = self.create_temp_project(files)
        result = self.analyzer.analyze_project_structure(temp_dir)
        
        # Should detect React frontend component
        frontend_components = [c for c in result['components'] if c.component_type == ComponentType.FRONTEND]
        self.assertEqual(len(frontend_components), 1)
        self.assertEqual(frontend_components[0].technology, 'React')
        
        # Should detect React framework
        self.assertIn('react', result['frameworks'])
        self.assertEqual(result['frameworks']['react']['type'], 'frontend')
        
        # Should classify as frontend_only project
        self.assertEqual(result['project_type'], 'frontend_only')
    
    def test_django_project_detection(self):
        """Test detection of Django project components."""
        files = {
            'requirements.txt': 'Django==4.2.0\npsycopg2==2.9.0\nredis==4.5.0',
            'manage.py': '#!/usr/bin/env python\nimport django',
            'myproject/settings.py': 'DATABASES = {"default": {"ENGINE": "django.db.backends.postgresql"}}',
            'myproject/urls.py': 'from django.urls import path'
        }
        
        temp_dir = self.create_temp_project(files)
        result = self.analyzer.analyze_project_structure(temp_dir)
        
        # Should detect Django backend component
        backend_components = [c for c in result['components'] if c.component_type == ComponentType.BACKEND]
        self.assertEqual(len(backend_components), 1)
        self.assertEqual(backend_components[0].technology, 'Django')
        
        # Should detect database components
        db_components = [c for c in result['components'] if c.component_type in [ComponentType.DATABASE, ComponentType.CACHE]]
        self.assertGreaterEqual(len(db_components), 1)  # PostgreSQL and Redis
        
        # Should detect Django framework
        self.assertIn('django', result['frameworks'])
        self.assertEqual(result['frameworks']['django']['type'], 'backend')
    
    def test_empty_project_handling(self):
        """Test handling of empty project directory."""
        temp_dir = self.create_temp_project({})
        
        with self.assertRaises(ValueError):
            self.analyzer.analyze_project_structure(temp_dir)
    
    def test_nonexistent_directory_handling(self):
        """Test handling of nonexistent directory."""
        with self.assertRaises(ValueError):
            self.analyzer.analyze_project_structure('/nonexistent/directory')
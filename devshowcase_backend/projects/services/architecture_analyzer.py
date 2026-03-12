import os
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ComponentType(Enum):
    FRONTEND = "frontend"
    BACKEND = "backend"
    DATABASE = "database"
    EXTERNAL_SERVICE = "external_service"
    MIDDLEWARE = "middleware"
    MESSAGE_QUEUE = "message_queue"
    CACHE = "cache"
    API_GATEWAY = "api_gateway"


@dataclass
class ArchitecturalComponent:
    name: str
    component_type: ComponentType
    technology: str
    description: str
    confidence_score: float
    source_files: List[str]
    dependencies: List[str]
    suggested_position: Tuple[float, float]


class ArchitectureAnalyzer:
    """Service for analyzing project structure and identifying architectural components."""
    
    FRAMEWORK_PATTERNS = {
        'react': ['react', 'jsx', 'tsx', 'create-react-app'],
        'vue': ['vue', '@vue/', 'vue-cli'],
        'angular': ['@angular/', 'angular', 'ng-'],
        'express': ['express', 'express.js'],
        'nestjs': ['@nestjs/', 'nestjs'],
        'django': ['django', 'Django'],
        'flask': ['flask', 'Flask'],
        'fastapi': ['fastapi', 'FastAPI'],
        'spring_boot': ['spring-boot', 'springframework'],
        'aspnet': ['Microsoft.AspNetCore', 'ASP.NET']
    }
    
    DATABASE_PATTERNS = {
        'postgresql': ['psycopg2', 'pg', 'postgresql', 'postgres'],
        'mysql': ['mysql', 'pymysql', 'mysql2'],
        'mongodb': ['mongodb', 'mongoose', 'pymongo'],
        'redis': ['redis', 'ioredis'],
        'sqlite': ['sqlite3', 'sqlite'],
        'elasticsearch': ['elasticsearch', '@elastic/'],
    }
    
    EXTERNAL_SERVICE_PATTERNS = {
        'aws_s3': ['aws-sdk', 'boto3', '@aws-sdk/client-s3'],
        'stripe': ['stripe'],
        'sendgrid': ['sendgrid', '@sendgrid/'],
        'twilio': ['twilio'],
        'firebase': ['firebase', 'firebase-admin'],
        'auth0': ['auth0'],
    }
    def __init__(self):
        """Initialize the ArchitectureAnalyzer."""
        pass
    
    def analyze_project_structure(self, directory_path: str) -> Dict:
        """
        Analyze project directory structure to identify architectural components.
        
        Args:
            directory_path: Path to project directory
            
        Returns:
            dict: Analysis results with components, frameworks, and project type
        """
        path = Path(directory_path)
        
        if not path.exists():
            raise ValueError(f"Directory does not exist: {directory_path}")
        
        # Get file structure
        file_structure = self._get_file_structure(path)
        
        # Identify components
        components = self.identify_components(file_structure)
        
        # Detect frameworks and technologies
        frameworks = self.detect_frameworks_and_technologies(file_structure['files'])
        
        # Analyze dependencies
        dependencies = self.analyze_dependencies(file_structure['dependency_files'])
        
        # Detect service connections
        connections = self.detect_service_connections(file_structure['config_files'])
        
        # Determine project type
        project_type = self._determine_project_type(components, frameworks)
        
        return {
            'project_type': project_type,
            'components': components,
            'frameworks': frameworks,
            'dependencies': dependencies,
            'connections': connections,
            'file_structure': file_structure
        }
    
    def identify_components(self, file_structure: Dict) -> List[ArchitecturalComponent]:
        """
        Identify architectural components from file structure.
        
        Args:
            file_structure: Dictionary containing file structure information
            
        Returns:
            List of ArchitecturalComponent objects
        """
        components = []
        files = file_structure['files']
        
        # Identify frontend components
        frontend_components = self._identify_frontend_components(files)
        components.extend(frontend_components)
        
        # Identify backend components
        backend_components = self._identify_backend_components(files)
        components.extend(backend_components)
        
        # Identify database components
        database_components = self._identify_database_components(files, file_structure['dependency_files'])
        components.extend(database_components)
        
        # Identify external services
        external_components = self._identify_external_services(files, file_structure['dependency_files'])
        components.extend(external_components)
        
        # Identify middleware components
        middleware_components = self._identify_middleware_components(files)
        components.extend(middleware_components)
        
        return components
    def detect_frameworks_and_technologies(self, files: List[Path]) -> Dict:
        """
        Detect frameworks and technologies from project files.
        
        Args:
            files: List of file paths
            
        Returns:
            Dictionary of detected frameworks with confidence scores
        """
        detected_frameworks = {}
        
        for file_path in files:
            if not file_path.is_file():
                continue
                
            try:
                # Check package.json for JavaScript/TypeScript frameworks
                if file_path.name == 'package.json':
                    frameworks = self._analyze_package_json(file_path)
                    detected_frameworks.update(frameworks)
                
                # Check requirements.txt for Python frameworks
                elif file_path.name == 'requirements.txt':
                    frameworks = self._analyze_requirements_txt(file_path)
                    detected_frameworks.update(frameworks)
                
                # Check pom.xml for Java frameworks
                elif file_path.name == 'pom.xml':
                    frameworks = self._analyze_pom_xml(file_path)
                    detected_frameworks.update(frameworks)
                
                # Check .csproj for C# frameworks
                elif file_path.suffix == '.csproj':
                    frameworks = self._analyze_csproj(file_path)
                    detected_frameworks.update(frameworks)
                
                # Check composer.json for PHP frameworks
                elif file_path.name == 'composer.json':
                    frameworks = self._analyze_composer_json(file_path)
                    detected_frameworks.update(frameworks)
                
                # Check Gemfile for Ruby frameworks
                elif file_path.name == 'Gemfile':
                    frameworks = self._analyze_gemfile(file_path)
                    detected_frameworks.update(frameworks)
                
            except Exception as e:
                # Log error but continue analysis
                print(f"Error analyzing file {file_path}: {str(e)}")
                continue
        
        return detected_frameworks
    
    def analyze_dependencies(self, dependency_files: List[Path]) -> List[Dict]:
        """
        Analyze dependency files to identify external services and databases.
        
        Args:
            dependency_files: List of dependency file paths
            
        Returns:
            List of dependency information dictionaries
        """
        dependencies = []
        
        for file_path in dependency_files:
            try:
                if file_path.name == 'package.json':
                    deps = self._extract_npm_dependencies(file_path)
                    dependencies.extend(deps)
                elif file_path.name == 'requirements.txt':
                    deps = self._extract_python_dependencies(file_path)
                    dependencies.extend(deps)
                elif file_path.name == 'pom.xml':
                    deps = self._extract_maven_dependencies(file_path)
                    dependencies.extend(deps)
                elif file_path.suffix == '.csproj':
                    deps = self._extract_nuget_dependencies(file_path)
                    dependencies.extend(deps)
            except Exception as e:
                print(f"Error analyzing dependencies in {file_path}: {str(e)}")
                continue
        
        return dependencies
    def detect_service_connections(self, config_files: List[Path]) -> List[Dict]:
        """
        Detect service connections from configuration files.
        
        Args:
            config_files: List of configuration file paths
            
        Returns:
            List of service connection information
        """
        connections = []
        
        for file_path in config_files:
            try:
                if file_path.suffix in ['.env', '.env.example']:
                    conns = self._analyze_env_file(file_path)
                    connections.extend(conns)
                elif file_path.name in ['docker-compose.yml', 'docker-compose.yaml']:
                    conns = self._analyze_docker_compose(file_path)
                    connections.extend(conns)
                elif file_path.name in ['config.json', 'app.json']:
                    conns = self._analyze_json_config(file_path)
                    connections.extend(conns)
            except Exception as e:
                print(f"Error analyzing config file {file_path}: {str(e)}")
                continue
        
        return connections
    
    def _get_file_structure(self, path: Path) -> Dict:
        """Get comprehensive file structure information."""
        files = []
        dependency_files = []
        config_files = []
        
        # Dependency file patterns
        dependency_patterns = [
            'package.json', 'requirements.txt', 'pom.xml', '*.csproj', 
            'composer.json', 'Gemfile', 'go.mod', 'Cargo.toml'
        ]
        
        # Config file patterns
        config_patterns = [
            '.env', '.env.example', 'docker-compose.yml', 'docker-compose.yaml',
            'config.json', 'app.json', 'settings.py', 'application.properties',
            'appsettings.json', 'web.config'
        ]
        
        for file_path in path.rglob('*'):
            if file_path.is_file():
                files.append(file_path)
                
                # Check if it's a dependency file
                if any(file_path.match(pattern) for pattern in dependency_patterns):
                    dependency_files.append(file_path)
                
                # Check if it's a config file
                if any(file_path.match(pattern) or file_path.name == pattern for pattern in config_patterns):
                    config_files.append(file_path)
        
        return {
            'files': files,
            'dependency_files': dependency_files,
            'config_files': config_files,
            'total_files': len(files)
        }
    
    def _determine_project_type(self, components: List[ArchitecturalComponent], frameworks: Dict) -> str:
        """Determine the overall project type based on components and frameworks."""
        has_frontend = any(comp.component_type == ComponentType.FRONTEND for comp in components)
        has_backend = any(comp.component_type == ComponentType.BACKEND for comp in components)
        has_database = any(comp.component_type == ComponentType.DATABASE for comp in components)
        
        # Check for microservices indicators
        backend_count = sum(1 for comp in components if comp.component_type == ComponentType.BACKEND)
        
        if backend_count > 2:
            return "microservices"
        elif has_frontend and has_backend:
            return "full_stack"
        elif has_frontend and not has_backend:
            return "frontend_only"
        elif has_backend and not has_frontend:
            return "api_only"
        else:
            return "monolithic"
    def _identify_frontend_components(self, files: List[Path]) -> List[ArchitecturalComponent]:
        """Identify frontend components from files."""
        components = []
        
        # Look for React components
        react_files = [f for f in files if f.suffix in ['.jsx', '.tsx'] and 'component' in str(f).lower()]
        if react_files:
            components.append(ArchitecturalComponent(
                name="React Frontend",
                component_type=ComponentType.FRONTEND,
                technology="React",
                description="React-based user interface",
                confidence_score=0.9,
                source_files=[str(f) for f in react_files[:5]],
                dependencies=[],
                suggested_position=(200, 100)
            ))
        
        # Look for Vue components
        vue_files = [f for f in files if f.suffix == '.vue']
        if vue_files:
            components.append(ArchitecturalComponent(
                name="Vue Frontend",
                component_type=ComponentType.FRONTEND,
                technology="Vue.js",
                description="Vue.js-based user interface",
                confidence_score=0.9,
                source_files=[str(f) for f in vue_files[:5]],
                dependencies=[],
                suggested_position=(200, 100)
            ))
        
        # Look for Angular components
        angular_files = [f for f in files if f.suffix == '.ts' and 'component' in str(f).lower()]
        if angular_files:
            components.append(ArchitecturalComponent(
                name="Angular Frontend",
                component_type=ComponentType.FRONTEND,
                technology="Angular",
                description="Angular-based user interface",
                confidence_score=0.9,
                source_files=[str(f) for f in angular_files[:5]],
                dependencies=[],
                suggested_position=(200, 100)
            ))
        
        # Generic frontend detection
        if not components:
            frontend_files = [f for f in files if f.suffix in ['.html', '.css', '.js'] and 'static' not in str(f)]
            if frontend_files:
                components.append(ArchitecturalComponent(
                    name="Web Frontend",
                    component_type=ComponentType.FRONTEND,
                    technology="HTML/CSS/JS",
                    description="Web-based user interface",
                    confidence_score=0.7,
                    source_files=[str(f) for f in frontend_files[:5]],
                    dependencies=[],
                    suggested_position=(200, 100)
                ))
        
        return components
    
    def _identify_backend_components(self, files: List[Path]) -> List[ArchitecturalComponent]:
        """Identify backend components from files."""
        components = []
        
        # Look for Express.js servers
        express_files = [f for f in files if f.suffix in ['.js', '.ts'] and 
                        any(keyword in f.name.lower() for keyword in ['server', 'app', 'index', 'main'])]
        if express_files:
            components.append(ArchitecturalComponent(
                name="Express API Server",
                component_type=ComponentType.BACKEND,
                technology="Express.js",
                description="Express.js REST API server",
                confidence_score=0.8,
                source_files=[str(f) for f in express_files[:3]],
                dependencies=[],
                suggested_position=(500, 100)
            ))
        
        # Look for Django applications
        django_files = [f for f in files if f.name in ['manage.py', 'wsgi.py', 'asgi.py']]
        if django_files:
            components.append(ArchitecturalComponent(
                name="Django API Server",
                component_type=ComponentType.BACKEND,
                technology="Django",
                description="Django REST API server",
                confidence_score=0.9,
                source_files=[str(f) for f in django_files],
                dependencies=[],
                suggested_position=(500, 100)
            ))
        
        # Look for Flask applications
        flask_files = [f for f in files if f.suffix == '.py' and 
                      any(keyword in f.name.lower() for keyword in ['app', 'server', 'main'])]
        if flask_files and not django_files:  # Avoid double detection
            components.append(ArchitecturalComponent(
                name="Flask API Server",
                component_type=ComponentType.BACKEND,
                technology="Flask",
                description="Flask REST API server",
                confidence_score=0.8,
                source_files=[str(f) for f in flask_files[:3]],
                dependencies=[],
                suggested_position=(500, 100)
            ))
        
        return components
    def _identify_database_components(self, files: List[Path], dependency_files: List[Path]) -> List[ArchitecturalComponent]:
        """Identify database components from files and dependencies."""
        components = []
        detected_dbs = set()
        
        # Check dependency files for database indicators
        for dep_file in dependency_files:
            try:
                content = dep_file.read_text(encoding='utf-8', errors='ignore').lower()
                
                for db_type, patterns in self.DATABASE_PATTERNS.items():
                    if any(pattern.lower() in content for pattern in patterns):
                        if db_type not in detected_dbs:
                            detected_dbs.add(db_type)
                            
                            db_names = {
                                'postgresql': 'PostgreSQL Database',
                                'mysql': 'MySQL Database',
                                'mongodb': 'MongoDB Database',
                                'redis': 'Redis Cache',
                                'sqlite': 'SQLite Database',
                                'elasticsearch': 'Elasticsearch'
                            }
                            
                            components.append(ArchitecturalComponent(
                                name=db_names.get(db_type, f"{db_type.title()} Database"),
                                component_type=ComponentType.DATABASE if db_type != 'redis' else ComponentType.CACHE,
                                technology=db_type.title(),
                                description=f"{db_type.title()} database for data storage",
                                confidence_score=0.8,
                                source_files=[str(dep_file)],
                                dependencies=[],
                                suggested_position=(800, 100 + len(components) * 150)
                            ))
            except Exception as e:
                print(f"Error reading dependency file {dep_file}: {str(e)}")
                continue
        
        # Check for database configuration files
        db_config_files = [f for f in files if any(db_name in f.name.lower() 
                          for db_name in ['database', 'db', 'mongo', 'postgres', 'mysql'])]
        
        if db_config_files and not detected_dbs:
            components.append(ArchitecturalComponent(
                name="Database",
                component_type=ComponentType.DATABASE,
                technology="Database",
                description="Database for data storage",
                confidence_score=0.6,
                source_files=[str(f) for f in db_config_files[:3]],
                dependencies=[],
                suggested_position=(800, 100)
            ))
        
        return components
    
    def _identify_external_services(self, files: List[Path], dependency_files: List[Path]) -> List[ArchitecturalComponent]:
        """Identify external service components from dependencies."""
        components = []
        detected_services = set()
        
        for dep_file in dependency_files:
            try:
                content = dep_file.read_text(encoding='utf-8', errors='ignore').lower()
                
                for service_type, patterns in self.EXTERNAL_SERVICE_PATTERNS.items():
                    if any(pattern.lower() in content for pattern in patterns):
                        if service_type not in detected_services:
                            detected_services.add(service_type)
                            
                            service_names = {
                                'aws_s3': 'AWS S3',
                                'stripe': 'Stripe Payment',
                                'sendgrid': 'SendGrid Email',
                                'twilio': 'Twilio SMS',
                                'firebase': 'Firebase',
                                'auth0': 'Auth0'
                            }
                            
                            components.append(ArchitecturalComponent(
                                name=service_names.get(service_type, service_type.title()),
                                component_type=ComponentType.EXTERNAL_SERVICE,
                                technology=service_type.replace('_', ' ').title(),
                                description=f"External {service_type.replace('_', ' ')} service",
                                confidence_score=0.8,
                                source_files=[str(dep_file)],
                                dependencies=[],
                                suggested_position=(500, 400 + len(components) * 100)
                            ))
            except Exception as e:
                print(f"Error reading dependency file {dep_file}: {str(e)}")
                continue
        
        return components
    
    def _identify_middleware_components(self, files: List[Path]) -> List[ArchitecturalComponent]:
        """Identify middleware components from files."""
        components = []
        
        # Look for authentication middleware
        auth_files = [f for f in files if any(keyword in f.name.lower() 
                     for keyword in ['auth', 'middleware', 'guard', 'interceptor'])]
        
        if auth_files:
            components.append(ArchitecturalComponent(
                name="Authentication Middleware",
                component_type=ComponentType.MIDDLEWARE,
                technology="Authentication",
                description="Authentication and authorization middleware",
                confidence_score=0.7,
                source_files=[str(f) for f in auth_files[:3]],
                dependencies=[],
                suggested_position=(500, 250)
            ))
        
        return components
    def _analyze_package_json(self, file_path: Path) -> Dict:
        """Analyze package.json for JavaScript/TypeScript frameworks."""
        try:
            content = json.loads(file_path.read_text(encoding='utf-8'))
            dependencies = {**content.get('dependencies', {}), **content.get('devDependencies', {})}
            
            frameworks = {}
            
            for framework, patterns in self.FRAMEWORK_PATTERNS.items():
                for pattern in patterns:
                    if any(pattern.lower() in dep.lower() for dep in dependencies.keys()):
                        frameworks[framework] = {
                            'name': framework.replace('_', ' ').title(),
                            'type': 'frontend' if framework in ['react', 'vue', 'angular'] else 'backend',
                            'confidence': 0.9,
                            'evidence': [str(file_path)]
                        }
                        break
            
            return frameworks
        except Exception as e:
            print(f"Error analyzing package.json: {str(e)}")
            return {}
    
    def _analyze_requirements_txt(self, file_path: Path) -> Dict:
        """Analyze requirements.txt for Python frameworks."""
        try:
            content = file_path.read_text(encoding='utf-8').lower()
            frameworks = {}
            
            for framework, patterns in self.FRAMEWORK_PATTERNS.items():
                if framework in ['django', 'flask', 'fastapi']:
                    for pattern in patterns:
                        if pattern.lower() in content:
                            frameworks[framework] = {
                                'name': framework.replace('_', ' ').title(),
                                'type': 'backend',
                                'confidence': 0.9,
                                'evidence': [str(file_path)]
                            }
                            break
            
            return frameworks
        except Exception as e:
            print(f"Error analyzing requirements.txt: {str(e)}")
            return {}
    
    def _analyze_pom_xml(self, file_path: Path) -> Dict:
        """Analyze pom.xml for Java frameworks."""
        try:
            content = file_path.read_text(encoding='utf-8').lower()
            frameworks = {}
            
            if 'spring-boot' in content or 'springframework' in content:
                frameworks['spring_boot'] = {
                    'name': 'Spring Boot',
                    'type': 'backend',
                    'confidence': 0.9,
                    'evidence': [str(file_path)]
                }
            
            return frameworks
        except Exception as e:
            print(f"Error analyzing pom.xml: {str(e)}")
            return {}
    
    def _analyze_csproj(self, file_path: Path) -> Dict:
        """Analyze .csproj for C# frameworks."""
        try:
            content = file_path.read_text(encoding='utf-8').lower()
            frameworks = {}
            
            if 'microsoft.aspnetcore' in content or 'asp.net' in content:
                frameworks['aspnet'] = {
                    'name': 'ASP.NET',
                    'type': 'backend',
                    'confidence': 0.9,
                    'evidence': [str(file_path)]
                }
            
            return frameworks
        except Exception as e:
            print(f"Error analyzing .csproj: {str(e)}")
            return {}
    
    def _analyze_composer_json(self, file_path: Path) -> Dict:
        """Analyze composer.json for PHP frameworks."""
        try:
            content = json.loads(file_path.read_text(encoding='utf-8'))
            dependencies = {**content.get('require', {}), **content.get('require-dev', {})}
            frameworks = {}
            
            if any('laravel' in dep.lower() for dep in dependencies.keys()):
                frameworks['laravel'] = {
                    'name': 'Laravel',
                    'type': 'backend',
                    'confidence': 0.9,
                    'evidence': [str(file_path)]
                }
            elif any('symfony' in dep.lower() for dep in dependencies.keys()):
                frameworks['symfony'] = {
                    'name': 'Symfony',
                    'type': 'backend',
                    'confidence': 0.9,
                    'evidence': [str(file_path)]
                }
            
            return frameworks
        except Exception as e:
            print(f"Error analyzing composer.json: {str(e)}")
            return {}
    
    def _analyze_gemfile(self, file_path: Path) -> Dict:
        """Analyze Gemfile for Ruby frameworks."""
        try:
            content = file_path.read_text(encoding='utf-8').lower()
            frameworks = {}
            
            if 'rails' in content:
                frameworks['rails'] = {
                    'name': 'Ruby on Rails',
                    'type': 'backend',
                    'confidence': 0.9,
                    'evidence': [str(file_path)]
                }
            
            return frameworks
        except Exception as e:
            print(f"Error analyzing Gemfile: {str(e)}")
            return {}
    def _extract_npm_dependencies(self, file_path: Path) -> List[Dict]:
        """Extract NPM dependencies from package.json."""
        try:
            content = json.loads(file_path.read_text(encoding='utf-8'))
            dependencies = {**content.get('dependencies', {}), **content.get('devDependencies', {})}
            
            deps = []
            for name, version in dependencies.items():
                deps.append({
                    'name': name,
                    'version': version,
                    'type': 'npm',
                    'source': str(file_path)
                })
            
            return deps
        except Exception as e:
            print(f"Error extracting NPM dependencies: {str(e)}")
            return []
    
    def _extract_python_dependencies(self, file_path: Path) -> List[Dict]:
        """Extract Python dependencies from requirements.txt."""
        try:
            content = file_path.read_text(encoding='utf-8')
            deps = []
            
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Parse package==version or package>=version
                    if '==' in line:
                        name, version = line.split('==', 1)
                    elif '>=' in line:
                        name, version = line.split('>=', 1)
                    else:
                        name, version = line, 'latest'
                    
                    deps.append({
                        'name': name.strip(),
                        'version': version.strip(),
                        'type': 'python',
                        'source': str(file_path)
                    })
            
            return deps
        except Exception as e:
            print(f"Error extracting Python dependencies: {str(e)}")
            return []
    
    def _extract_maven_dependencies(self, file_path: Path) -> List[Dict]:
        """Extract Maven dependencies from pom.xml."""
        try:
            content = file_path.read_text(encoding='utf-8')
            # Simple regex-based extraction (could be improved with XML parsing)
            import re
            
            deps = []
            dependency_pattern = r'<groupId>(.*?)</groupId>.*?<artifactId>(.*?)</artifactId>.*?<version>(.*?)</version>'
            matches = re.findall(dependency_pattern, content, re.DOTALL)
            
            for group_id, artifact_id, version in matches:
                deps.append({
                    'name': f"{group_id.strip()}:{artifact_id.strip()}",
                    'version': version.strip(),
                    'type': 'maven',
                    'source': str(file_path)
                })
            
            return deps
        except Exception as e:
            print(f"Error extracting Maven dependencies: {str(e)}")
            return []
    
    def _extract_nuget_dependencies(self, file_path: Path) -> List[Dict]:
        """Extract NuGet dependencies from .csproj."""
        try:
            content = file_path.read_text(encoding='utf-8')
            import re
            
            deps = []
            package_pattern = r'<PackageReference Include="(.*?)" Version="(.*?)"'
            matches = re.findall(package_pattern, content)
            
            for name, version in matches:
                deps.append({
                    'name': name.strip(),
                    'version': version.strip(),
                    'type': 'nuget',
                    'source': str(file_path)
                })
            
            return deps
        except Exception as e:
            print(f"Error extracting NuGet dependencies: {str(e)}")
            return []
    
    def _analyze_env_file(self, file_path: Path) -> List[Dict]:
        """Analyze .env file for service connections."""
        try:
            content = file_path.read_text(encoding='utf-8')
            connections = []
            
            # Look for common service patterns
            service_patterns = {
                'database': ['DATABASE_URL', 'DB_HOST', 'POSTGRES_URL', 'MYSQL_URL'],
                'redis': ['REDIS_URL', 'REDIS_HOST'],
                'aws': ['AWS_ACCESS_KEY', 'AWS_SECRET_KEY', 'S3_BUCKET'],
                'stripe': ['STRIPE_SECRET_KEY', 'STRIPE_PUBLISHABLE_KEY'],
                'sendgrid': ['SENDGRID_API_KEY'],
                'auth0': ['AUTH0_DOMAIN', 'AUTH0_CLIENT_ID']
            }
            
            for service, patterns in service_patterns.items():
                if any(pattern in content for pattern in patterns):
                    connections.append({
                        'service': service,
                        'type': 'environment_variable',
                        'source': str(file_path),
                        'confidence': 0.8
                    })
            
            return connections
        except Exception as e:
            print(f"Error analyzing .env file: {str(e)}")
            return []
    
    def _analyze_docker_compose(self, file_path: Path) -> List[Dict]:
        """Analyze docker-compose.yml for service connections."""
        try:
            content = file_path.read_text(encoding='utf-8').lower()
            connections = []
            
            # Look for common services in docker-compose
            if 'postgres' in content or 'postgresql' in content:
                connections.append({
                    'service': 'postgresql',
                    'type': 'docker_service',
                    'source': str(file_path),
                    'confidence': 0.9
                })
            
            if 'redis' in content:
                connections.append({
                    'service': 'redis',
                    'type': 'docker_service',
                    'source': str(file_path),
                    'confidence': 0.9
                })
            
            if 'mongo' in content:
                connections.append({
                    'service': 'mongodb',
                    'type': 'docker_service',
                    'source': str(file_path),
                    'confidence': 0.9
                })
            
            return connections
        except Exception as e:
            print(f"Error analyzing docker-compose: {str(e)}")
            return []
    
    def _analyze_json_config(self, file_path: Path) -> List[Dict]:
        """Analyze JSON configuration files for service connections."""
        try:
            content = json.loads(file_path.read_text(encoding='utf-8'))
            connections = []
            
            # Look for database configurations
            if 'database' in content or 'db' in content:
                connections.append({
                    'service': 'database',
                    'type': 'json_config',
                    'source': str(file_path),
                    'confidence': 0.7
                })
            
            return connections
        except Exception as e:
            print(f"Error analyzing JSON config: {str(e)}")
            return []
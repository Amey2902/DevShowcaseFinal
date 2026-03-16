import json
from pathlib import Path
from django.conf import settings


class APITranslator:
    """Translate APIs between different frameworks automatically."""
    
    # Framework-specific code templates
    FRAMEWORK_TEMPLATES = {
        'express': {
            'route_template': '''
// {description}
app.{method}('{path}', {middleware}async (req, res) => {{
    try {{
        {auth_check}
        {validation}
        {business_logic}
        res.json({{ success: true, data: result }});
    }} catch (error) {{
        res.status(500).json({{ error: error.message }});
    }}
}});''',
            'auth_middleware': 'authenticateToken, ',
            'validation_template': '''
        // Get request data
        const {{ {params} }} = req.{param_source};''',
            'business_logic': '''
        // TODO: Implement business logic
        const result = await {service_name}Service.{method_name}({params});'''
        },
        
        'fastapi': {
            'route_template': '''
@app.{method}("{path}")
async def {function_name}({parameters}):
    """
    {description}
    """
    try:
        {auth_check}
        {business_logic}
        return {{"success": True, "data": result}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))''',
            'auth_dependency': 'current_user: User = Depends(get_current_user)',
            'pydantic_model': '''
class {model_name}(BaseModel):
{fields}''',
            'business_logic': '''
        # TODO: Implement business logic
        result = await {service_name}_service.{method_name}({params})'''
        },
        
        'flask': {
            'route_template': '''
@app.route('{path}', methods=['{method}'])
{auth_decorator}
def {function_name}():
    """
    {description}
    """
    try:
        {validation}
        {business_logic}
        return jsonify({{"success": True, "data": result}})
    except Exception as e:
        return jsonify({{"error": str(e)}}), 500''',
            'auth_decorator': '@jwt_required()',
            'validation_template': '''
        # Get request data
        data = request.get_json() or {{}}''',
            'business_logic': '''
        # TODO: Implement business logic
        result = {service_name}_service.{method_name}(data)'''
        },
        
        'django': {
            'route_template': '''
@api_view(['{method}'])
@permission_classes([IsAuthenticated])
def {function_name}(request):
    """
    {description}
    """
    try:
        {validation}
        {business_logic}
        return Response({{"success": True, "data": result}})
    except Exception as e:
        return Response({{"error": str(e)}}, status=500)''',
            'serializer_template': '''
class {serializer_name}(serializers.Serializer):
{fields}''',
            'validation_template': '''
        # Get request data
        data = request.data''',
            'business_logic': '''
        # TODO: Implement business logic
        result = {service_name}_service.{method_name}(data)'''
        },
        
        'spring': {
            'route_template': '''
@{method_annotation}("{path}")
public ResponseEntity<ApiResponse> {function_name}({parameters}) {{
    try {{
        {validation}
        {business_logic}
        return ResponseEntity.ok(new ApiResponse(true, result));
    }} catch (Exception e) {{
        return ResponseEntity.status(500).body(new ApiResponse(false, e.getMessage()));
    }}
}}''',
            'auth_annotation': '@PreAuthorize("hasRole(\'USER\')")',
            'validation_template': '''
        // Validate request data
        if ({required_param} == null) {{
            return ResponseEntity.badRequest().body(new ApiResponse(false, "Missing request data"));
        }}''',
            'business_logic': '''
        // TODO: Implement business logic
        Object result = {service_name}Service.{method_name}({params});'''
        }
    }
    
    def __init__(self):
        """Initialize the API translator."""
        pass
    
    def translate_endpoints(self, source_endpoints, target_framework):
        """
        Translate detected endpoints to target framework.
        
        Args:
            source_endpoints: List of detected endpoint objects
            target_framework: Target framework ('express', 'fastapi', 'flask', 'django', 'spring')
            
        Returns:
            dict: Generated code files for target framework
        """
        if target_framework not in self.FRAMEWORK_TEMPLATES:
            raise ValueError(f"Unsupported target framework: {target_framework}")
        
        template = self.FRAMEWORK_TEMPLATES[target_framework]
        generated_files = {}
        
        # Generate main routes file
        routes_code = self._generate_routes_file(source_endpoints, target_framework, template)
        generated_files['routes'] = routes_code
        
        # Generate additional files based on framework
        if target_framework == 'fastapi':
            generated_files['models'] = self._generate_pydantic_models(source_endpoints)
        elif target_framework == 'django':
            generated_files['serializers'] = self._generate_django_serializers(source_endpoints)
        elif target_framework == 'spring':
            generated_files['models'] = self._generate_java_models(source_endpoints)
        
        return generated_files
    
    def _generate_routes_file(self, endpoints, target_framework, template):
        """Generate the main routes file."""
        routes = []
        
        for endpoint in endpoints:
            # Convert endpoint data to framework-specific code
            route_code = self._generate_single_route(endpoint, target_framework, template)
            routes.append(route_code)
        
        # Add framework-specific imports and setup
        imports = self._get_framework_imports(target_framework)
        setup = self._get_framework_setup(target_framework)
        
        return f"{imports}\n\n{setup}\n\n" + "\n\n".join(routes)
    
    def _generate_single_route(self, endpoint, target_framework, template):
        """Generate code for a single endpoint."""
        # Extract endpoint information
        method = endpoint.get('method', 'GET').lower()
        path = endpoint.get('path', '/')
        description = endpoint.get('description', 'API endpoint')
        auth_required = endpoint.get('auth_required', False)
        path_parameters = endpoint.get('path_parameters', [])
        query_parameters = endpoint.get('query_parameters', [])
        
        # Generate function name
        function_name = self._generate_function_name(method, path)
        
        # Framework-specific adaptations
        if target_framework == 'express':
            return self._generate_express_route(
                template, method, path, description, auth_required, 
                function_name, path_parameters, query_parameters
            )
        elif target_framework == 'fastapi':
            return self._generate_fastapi_route(
                template, method, path, description, auth_required,
                function_name, path_parameters, query_parameters
            )
        elif target_framework == 'flask':
            return self._generate_flask_route(
                template, method, path, description, auth_required,
                function_name, path_parameters, query_parameters
            )
        elif target_framework == 'django':
            return self._generate_django_route(
                template, method, path, description, auth_required,
                function_name, path_parameters, query_parameters
            )
        elif target_framework == 'spring':
            return self._generate_spring_route(
                template, method, path, description, auth_required,
                function_name, path_parameters, query_parameters
            )
    
    def _generate_express_route(self, template, method, path, description, auth_required, 
                               function_name, path_params, query_params):
        """Generate Express.js route code."""
        middleware = template['auth_middleware'] if auth_required else ''
        
        # Convert path parameters from full URL to Express format
        express_path = self._convert_path_to_express(path)
        
        # Clean up function name
        clean_function_name = self._clean_function_name(function_name)
        
        # Generate validation code
        validation = ""
        if method.upper() in ['POST', 'PUT', 'PATCH']:
            validation = template['validation_template'].format(
                params="body",
                param_source="body",
                required_param="data"
            )
        
        # Generate business logic with cleaner method names
        service_name = self._extract_service_name(path)
        # Create a cleaner method name for Express (camelCase)
        endpoint_name = clean_function_name.replace(f"{method}_", "")
        method_name = f"{method}{endpoint_name.replace('_', '').title()}" if endpoint_name else f"{method}Endpoint"
        
        business_logic = template['business_logic'].format(
            service_name=service_name,
            method_name=method_name,
            params="req.body"
        )
        
        # Generate auth check
        auth_check = "// Authentication handled by middleware" if auth_required else ""
        
        return template['route_template'].format(
            method=method,
            path=express_path,
            middleware=middleware,
            description=description,
            auth_check=auth_check,
            validation=validation,
            business_logic=business_logic
        )
    
    def _generate_fastapi_route(self, template, method, path, description, auth_required,
                               function_name, path_params, query_params):
        """Generate FastAPI route code."""
        # Convert path parameters to FastAPI format
        fastapi_path = self._convert_path_to_fastapi(path)
        
        # Clean up function name
        clean_function_name = self._clean_function_name(function_name)
        
        # Generate parameters
        parameters = []
        if path_params:
            parameters.extend([f"{param}: str" for param in path_params])
        if method.upper() in ['POST', 'PUT', 'PATCH']:
            parameters.append("request_data: dict")
        if auth_required:
            parameters.append(template['auth_dependency'])
        
        parameters_str = ", ".join(parameters)
        
        # Generate business logic with cleaner method names
        service_name = self._extract_service_name(path)
        # Create a cleaner method name
        endpoint_name = clean_function_name.replace(f"{method}_", "")
        method_name = f"{method}_{endpoint_name}" if endpoint_name else f"{method}_endpoint"
        params = "request_data" if method.upper() in ['POST', 'PUT', 'PATCH'] else "{}"
        
        business_logic = template['business_logic'].format(
            service_name=service_name,
            method_name=method_name,
            params=params
        )
        
        # Generate auth check
        auth_check = "# Authentication handled by dependency injection" if auth_required else ""
        
        return template['route_template'].format(
            method=method,
            path=fastapi_path,
            function_name=clean_function_name,
            parameters=parameters_str,
            description=description,
            auth_check=auth_check,
            business_logic=business_logic
        )
    
    def _generate_flask_route(self, template, method, path, description, auth_required,
                             function_name, path_params, query_params):
        """Generate Flask route code."""
        # Convert path to Flask format (remove domain, keep only path)
        flask_path = self._convert_path_to_flask(path)
        
        # Clean up function name
        clean_function_name = self._clean_function_name(function_name)
        
        # Generate validation
        validation = ""
        if method.upper() in ['POST', 'PUT', 'PATCH']:
            validation = template['validation_template'].format(
                required_param='data'
            )
        
        # Generate business logic with cleaner method names
        service_name = self._extract_service_name(path)
        # Create a cleaner method name from the endpoint
        endpoint_name = clean_function_name.replace(f"{method}_", "")
        method_name = f"{method}_{endpoint_name}" if endpoint_name else f"{method}_endpoint"
        
        business_logic = template['business_logic'].format(
            service_name=service_name,
            method_name=method_name
        )
        
        # Auth decorator
        auth_decorator = template['auth_decorator'] if auth_required else ""
        
        return template['route_template'].format(
            path=flask_path,
            method=method.upper(),
            auth_decorator=auth_decorator,
            function_name=clean_function_name,
            description=description,
            validation=validation,
            business_logic=business_logic
        )
    
    def _generate_django_route(self, template, method, path, description, auth_required,
                              function_name, path_params, query_params):
        """Generate Django REST Framework route code."""
        # Clean up function name
        clean_function_name = self._clean_function_name(function_name)
        
        # Generate validation
        validation = ""
        if method.upper() in ['POST', 'PUT', 'PATCH']:
            validation = template['validation_template'].format(
                serializer_name=f"{clean_function_name.title()}Serializer"
            )
        
        # Generate business logic with cleaner method names
        service_name = self._extract_service_name(path)
        # Create a cleaner method name
        endpoint_name = clean_function_name.replace(f"{method}_", "")
        method_name = f"{method}_{endpoint_name}" if endpoint_name else f"{method}_endpoint"
        
        business_logic = template['business_logic'].format(
            service_name=service_name,
            method_name=method_name
        )
        
        return template['route_template'].format(
            method=method.upper(),
            function_name=clean_function_name,
            description=description,
            validation=validation,
            business_logic=business_logic
        )
    
    def _generate_spring_route(self, template, method, path, description, auth_required,
                              function_name, path_params, query_params):
        """Generate Spring Boot route code."""
        # Method annotation mapping
        method_annotations = {
            'get': 'GetMapping',
            'post': 'PostMapping', 
            'put': 'PutMapping',
            'delete': 'DeleteMapping',
            'patch': 'PatchMapping'
        }
        
        method_annotation = method_annotations.get(method, 'GetMapping')
        
        # Clean up function name and convert to Java naming convention
        clean_function_name = self._clean_function_name(function_name)
        java_function_name = self._to_camel_case(clean_function_name)
        
        # Convert path to Spring format
        spring_path = self._convert_path_to_spring(path)
        
        # Generate parameters
        parameters = []
        if path_params:
            parameters.extend([f"@PathVariable String {param}" for param in path_params])
        if method.upper() in ['POST', 'PUT', 'PATCH']:
            parameters.append("@RequestBody Map<String, Object> requestData")
        
        parameters_str = ", ".join(parameters)
        
        # Generate validation
        validation = ""
        if method.upper() in ['POST', 'PUT', 'PATCH']:
            validation = template['validation_template'].format(
                required_param="requestData"
            )
        
        # Generate business logic with cleaner method names
        service_name = self._extract_service_name(path)
        # Create a cleaner method name for Java (camelCase)
        endpoint_name = clean_function_name.replace(f"{method}_", "")
        method_name = f"{method}{self._to_camel_case(endpoint_name)}" if endpoint_name else f"{method}Endpoint"
        params = "requestData" if method.upper() in ['POST', 'PUT', 'PATCH'] else "new HashMap<>()"
        
        business_logic = template['business_logic'].format(
            service_name=service_name,
            method_name=method_name,
            params=params
        )
        
        return template['route_template'].format(
            method_annotation=method_annotation,
            path=spring_path,
            function_name=java_function_name,
            parameters=parameters_str,
            validation=validation,
            business_logic=business_logic
        )
    
    # Helper methods
    def _generate_function_name(self, method, path):
        """Generate a function name from method and path."""
        # Extract clean path from URL
        clean_path = self._extract_path_from_url(path)
        
        # Remove path parameters and clean up
        clean_path = clean_path.replace(':', '').replace('/', '_').replace('-', '_')
        clean_path = ''.join(c for c in clean_path if c.isalnum() or c == '_')
        clean_path = clean_path.strip('_')
        
        # Ensure we have a meaningful name
        if not clean_path:
            clean_path = 'endpoint'
            
        return f"{method}_{clean_path}"
    
    def _clean_function_name(self, function_name):
        """Clean up function name to be valid Python identifier."""
        # Remove invalid characters and ensure it's a valid Python identifier
        clean_name = ''.join(c for c in function_name if c.isalnum() or c == '_')
        
        # Ensure it doesn't start with a number
        if clean_name and clean_name[0].isdigit():
            clean_name = 'endpoint_' + clean_name
        
        # Ensure it's not empty
        if not clean_name:
            clean_name = 'api_endpoint'
        
        return clean_name
    
    def _extract_service_name(self, path):
        """Extract service name from path."""
        # Extract clean path from URL
        clean_path = self._extract_path_from_url(path)
        
        # Extract first meaningful path segment as service name
        parts = [p for p in clean_path.split('/') if p and not p.startswith(':')]
        service_name = parts[0] if parts else "api"
        
        # Clean service name to be a valid identifier
        service_name = ''.join(c for c in service_name if c.isalnum() or c == '_')
        return service_name or "api"
    
    def _convert_path_to_express(self, path):
        """Convert path parameters to Express.js format."""
        # Extract clean path from URL
        clean_path = self._extract_path_from_url(path)
        
        # Express uses :param format, which matches our detection
        return clean_path
    
    def _convert_path_to_fastapi(self, path):
        """Convert path parameters to FastAPI format."""
        # Extract clean path from URL
        clean_path = self._extract_path_from_url(path)
        
        # Convert :param to {param} format for FastAPI
        if ':' in clean_path:
            import re
            clean_path = re.sub(r':(\w+)', r'{\1}', clean_path)
        
        return clean_path
    
    def _convert_path_to_spring(self, path):
        """Convert path parameters to Spring Boot format."""
        # Extract clean path from URL
        clean_path = self._extract_path_from_url(path)
        
        # Convert :param to {param} format for Spring
        if ':' in clean_path:
            import re
            clean_path = re.sub(r':(\w+)', r'{\1}', clean_path)
        
        return clean_path
    
    def _extract_path_from_url(self, url):
        """Extract clean path from full URL."""
        # Handle full URLs like http://localhost:5000/api/users
        if url.startswith('http://') or url.startswith('https://'):
            try:
                from urllib.parse import urlparse
                parsed = urlparse(url)
                return parsed.path or '/'
            except:
                # Fallback to manual parsing
                if '://' in url:
                    # Remove protocol and domain
                    url_without_protocol = url.split('://', 1)[1]
                    if '/' in url_without_protocol:
                        # Get everything after the first slash (the path)
                        domain_and_path = url_without_protocol.split('/', 1)
                        if len(domain_and_path) > 1:
                            return '/' + domain_and_path[1]
                return '/'
        
        # Handle relative paths or already clean paths
        if not url.startswith('/'):
            url = '/' + url
        return url
    
    def _convert_path_to_flask(self, path):
        """Convert path parameters to Flask format."""
        # Extract clean path from URL
        clean_path = self._extract_path_from_url(path)
        
        # Convert :param to <param> format for Flask
        if ':' in clean_path:
            import re
            clean_path = re.sub(r':(\w+)', r'<\1>', clean_path)

        return clean_path
    
    def _to_camel_case(self, snake_str):
        """Convert snake_case to camelCase for Java methods."""
        components = snake_str.split('_')
        return components[0] + ''.join(word.capitalize() for word in components[1:])
    
    def _get_framework_imports(self, framework):
        """Get framework-specific imports."""
        imports = {
            'express': '''const express = require('express');
const jwt = require('jsonwebtoken');

const app = express();''',
            'fastapi': '''from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any
import asyncio

app = FastAPI()''',
            'flask': '''from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity

app = Flask(__name__)''',
            'django': '''from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers''',
            'spring': '''import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import java.util.Map;
import java.util.HashMap;

@RestController
@RequestMapping("/api")
public class ApiController {'''
        }
        return imports.get(framework, '')
    
    def _get_framework_setup(self, framework):
        """Get framework-specific setup code."""
        setup = {
            'express': '''
// Middleware
app.use(express.json());

// Authentication middleware
const authenticateToken = (req, res, next) => {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];
    
    if (!token) {
        return res.sendStatus(401);
    }
    
    jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
        if (err) return res.sendStatus(403);
        req.user = user;
        next();
    });
};''',
            'fastapi': '''
# Authentication dependency
async def get_current_user():
    # TODO: Implement authentication logic
    pass''',
            'flask': '''
# JWT Configuration
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
jwt = JWTManager(app)''',
            'django': '''
# Django REST Framework is configured in settings.py''',
            'spring': '''
    // Spring Security is configured separately'''
        }
        return setup.get(framework, '')
    
    def _generate_pydantic_models(self, endpoints):
        """Generate Pydantic models for FastAPI."""
        models = []
        for endpoint in endpoints:
            if endpoint.get('request_schema'):
                model_name = f"{endpoint.get('name', 'Api').replace(' ', '')}Request"
                fields = []
                for field, field_type in endpoint.get('request_schema', {}).items():
                    fields.append(f"    {field}: {self._python_type_mapping(field_type)}")
                
                model = self.FRAMEWORK_TEMPLATES['fastapi']['pydantic_model'].format(
                    model_name=model_name,
                    fields='\n'.join(fields)
                )
                models.append(model)
        
        return '\n\n'.join(models)
    
    def _generate_django_serializers(self, endpoints):
        """Generate Django REST Framework serializers."""
        serializers = []
        for endpoint in endpoints:
            if endpoint.get('request_schema'):
                serializer_name = f"{endpoint.get('name', 'Api').replace(' ', '')}Serializer"
                fields = []
                for field, field_type in endpoint.get('request_schema', {}).items():
                    django_field = self._django_field_mapping(field_type)
                    fields.append(f"    {field} = serializers.{django_field}")
                
                serializer = self.FRAMEWORK_TEMPLATES['django']['serializer_template'].format(
                    serializer_name=serializer_name,
                    fields='\n'.join(fields)
                )
                serializers.append(serializer)
        
        return '\n\n'.join(serializers)
    
    def _generate_java_models(self, endpoints):
        """Generate Java model classes for Spring Boot."""
        models = []
        for endpoint in endpoints:
            if endpoint.get('request_schema'):
                class_name = f"{endpoint.get('name', 'Api').replace(' ', '')}Request"
                fields = []
                for field, field_type in endpoint.get('request_schema', {}).items():
                    java_type = self._java_type_mapping(field_type)
                    fields.append(f"    private {java_type} {field};")
                
                model = f'''
public class {class_name} {{
{chr(10).join(fields)}
    
    // Getters and setters
    // TODO: Generate getters and setters
}}'''
                models.append(model)
        
        return '\n\n'.join(models)
    
    def _python_type_mapping(self, field_type):
        """Map field types to Python types."""
        # Normalize: if field_type is a list, use the first element
        if isinstance(field_type, list):
            field_type = field_type[0] if field_type else 'string'
        field_type = str(field_type).lower()
        mapping = {
            'string': 'str',
            'integer': 'int', 
            'boolean': 'bool',
            'array': 'List[str]',
            'object': 'dict'
        }
        return mapping.get(field_type, 'str')
    
    def _django_field_mapping(self, field_type):
        """Map field types to Django serializer fields."""
        if isinstance(field_type, list):
            field_type = field_type[0] if field_type else 'string'
        field_type = str(field_type).lower()
        mapping = {
            'string': 'CharField()',
            'integer': 'IntegerField()',
            'boolean': 'BooleanField()',
            'array': 'ListField()',
            'object': 'JSONField()'
        }
        return mapping.get(field_type, 'CharField()')
    
    def _java_type_mapping(self, field_type):
        """Map field types to Java types."""
        if isinstance(field_type, list):
            field_type = field_type[0] if field_type else 'string'
        field_type = str(field_type).lower()
        mapping = {
            'string': 'String',
            'integer': 'Integer',
            'boolean': 'Boolean', 
            'array': 'List<String>',
            'object': 'Object'
        }
        return mapping.get(field_type, 'String')

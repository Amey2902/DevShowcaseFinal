import ast
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum


class SecurityLevel(Enum):
    """Security classification levels for endpoints."""
    PUBLIC = "public"
    AUTH_REQUIRED = "auth_required"
    ADMIN_FUNCTIONS = "admin_functions"
    SENSITIVE_DATA = "sensitive_data"


@dataclass
class SecurityAnalysis:
    """Result of AST security analysis for an endpoint."""
    security_level: SecurityLevel
    confidence_score: float  # 0.0 to 1.0
    detected_decorators: List[str]
    security_features: List[str]
    reasoning: str
    file_path: str
    line_number: Optional[int] = None


class ASTSecurityAnalyzer:
    """
    AST-based security analyzer for Python code.
    Analyzes code structure to classify endpoint security levels.
    """
    
    # Security-related patterns and keywords
    SECURITY_DECORATORS = {
        'login_required', 'require_auth', 'authenticate', 'permission_required',
        'admin_required', 'staff_required', 'superuser_required', 'requires_auth',
        'jwt_required', 'token_required', 'api_key_required'
    }
    
    ADMIN_KEYWORDS = {
        'admin', 'superuser', 'staff', 'delete', 'remove', 'destroy',
        'create_user', 'manage', 'control', 'system', 'config'
    }
    
    SENSITIVE_DATA_KEYWORDS = {
        'password', 'token', 'secret', 'key', 'credential', 'auth',
        'payment', 'billing', 'card', 'ssn', 'social', 'personal',
        'private', 'confidential', 'secure'
    }
    
    PUBLIC_PATTERNS = {
        'health', 'status', 'ping', 'version', 'info', 'public',
        'home', 'index', 'about', 'contact', 'help'
    }
    
    def __init__(self):
        """Initialize the AST analyzer."""
        self.analysis_cache = {}
    
    def analyze_project_security(self, directory_path: str, endpoints_data: List[Dict]) -> Dict[str, SecurityAnalysis]:
        """
        Analyze security for all endpoints in a project.
        
        Args:
            directory_path: Path to project directory
            endpoints_data: List of endpoint dictionaries from AI analysis
            
        Returns:
            Dict mapping endpoint keys to SecurityAnalysis objects
        """
        print(f"=== Starting AST Security Analysis ===")
        print(f"Directory: {directory_path}")
        print(f"Endpoints to analyze: {len(endpoints_data)}")
        
        results = {}
        
        # Find all Python files in the project
        python_files = self._find_python_files(directory_path)
        print(f"Found {len(python_files)} Python files")
        
        # Parse all Python files and build AST cache
        ast_cache = self._build_ast_cache(python_files)
        print(f"Successfully parsed {len(ast_cache)} Python files")
        
        # Analyze each endpoint
        for endpoint_data in endpoints_data:
            try:
                endpoint_key = f"{endpoint_data.get('method', 'GET')}:{endpoint_data.get('path', '')}"
                analysis = self._analyze_endpoint_security(endpoint_data, ast_cache, directory_path)
                results[endpoint_key] = analysis
                
                print(f"Analyzed {endpoint_key}: {analysis.security_level.value} (confidence: {analysis.confidence_score:.2f})")
                
            except Exception as e:
                print(f"Error analyzing endpoint {endpoint_data}: {e}")
                # Provide fallback analysis
                results[endpoint_key] = SecurityAnalysis(
                    security_level=SecurityLevel.AUTH_REQUIRED,
                    confidence_score=0.3,
                    detected_decorators=[],
                    security_features=[],
                    reasoning="Analysis failed, defaulting to auth required for safety",
                    file_path=endpoint_data.get('file', ''),
                    line_number=endpoint_data.get('line')
                )
        
        print(f"=== AST Security Analysis Complete ===")
        return results
    
    def _find_python_files(self, directory_path: str) -> List[Path]:
        """Find all Python files in the project directory."""
        path = Path(directory_path)
        python_files = []
        
        # Skip common non-source directories
        skip_dirs = {'__pycache__', 'venv', 'env', '.git', 'node_modules', 'dist', 'build', '.pytest_cache'}
        
        for py_file in path.rglob('*.py'):
            # Skip if in excluded directory
            if any(skip_dir in py_file.parts for skip_dir in skip_dirs):
                continue
            python_files.append(py_file)
        
        return python_files
    
    def _build_ast_cache(self, python_files: List[Path]) -> Dict[str, ast.AST]:
        """Parse Python files and build AST cache."""
        ast_cache = {}
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Parse the AST
                tree = ast.parse(content, filename=str(py_file))
                ast_cache[str(py_file)] = tree
                
            except Exception as e:
                print(f"Failed to parse {py_file}: {e}")
                continue
        
        return ast_cache
    
    def _analyze_endpoint_security(self, endpoint_data: Dict, ast_cache: Dict[str, ast.AST], base_path: str) -> SecurityAnalysis:
        """
        Analyze security level for a single endpoint.
        
        Args:
            endpoint_data: Endpoint information from AI analysis
            ast_cache: Cached AST trees for Python files
            base_path: Base project directory path
            
        Returns:
            SecurityAnalysis object
        """
        file_path = endpoint_data.get('file', '')
        line_number = endpoint_data.get('line')
        method = endpoint_data.get('method', 'GET')
        path = endpoint_data.get('path', '')
        name = endpoint_data.get('name', '')
        description = endpoint_data.get('description', '')
        
        # Combine all text for analysis
        combined_text = f"{name} {path} {description}".lower()
        
        detected_decorators = []
        security_features = []
        confidence_factors = []
        
        # 1. AST-based analysis (if file is available)
        if file_path and line_number:
            full_file_path = os.path.join(base_path, file_path)
            if full_file_path in ast_cache:
                ast_analysis = self._analyze_ast_context(ast_cache[full_file_path], line_number)
                detected_decorators.extend(ast_analysis['decorators'])
                security_features.extend(ast_analysis['security_features'])
                confidence_factors.extend(ast_analysis['confidence_factors'])
        
        # 2. Pattern-based analysis
        pattern_analysis = self._analyze_text_patterns(combined_text, method, path)
        security_features.extend(pattern_analysis['features'])
        confidence_factors.extend(pattern_analysis['confidence_factors'])
        
        # 3. Determine security level and confidence
        security_level, confidence_score, reasoning = self._classify_security_level(
            detected_decorators, security_features, confidence_factors, method, combined_text
        )
        
        return SecurityAnalysis(
            security_level=security_level,
            confidence_score=confidence_score,
            detected_decorators=detected_decorators,
            security_features=security_features,
            reasoning=reasoning,
            file_path=file_path,
            line_number=line_number
        )
    
    def _analyze_ast_context(self, tree: ast.AST, target_line: int) -> Dict[str, List]:
        """
        Analyze AST context around a specific line number.
        
        Args:
            tree: AST tree of the file
            target_line: Line number to analyze
            
        Returns:
            Dict with decorators, security_features, and confidence_factors
        """
        decorators = []
        security_features = []
        confidence_factors = []
        
        class SecurityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.current_class = None
                self.current_function = None
            
            def visit_ClassDef(self, node):
                old_class = self.current_class
                self.current_class = node.name
                self.generic_visit(node)
                self.current_class = old_class
            
            def visit_FunctionDef(self, node):
                old_function = self.current_function
                self.current_function = node.name
                
                # Check if this function is near our target line
                if hasattr(node, 'lineno') and abs(node.lineno - target_line) <= 5:
                    # Analyze decorators
                    for decorator in node.decorator_list:
                        decorator_name = self._get_decorator_name(decorator)
                        if decorator_name:
                            decorators.append(decorator_name)
                            
                            # Check if it's a security decorator
                            if any(sec_dec in decorator_name.lower() for sec_dec in self.SECURITY_DECORATORS):
                                security_features.append(f"Security decorator: {decorator_name}")
                                confidence_factors.append(('security_decorator', 0.8))
                    
                    # Analyze function name and docstring
                    func_name_lower = node.name.lower()
                    
                    # Check for admin patterns in function name
                    if any(admin_kw in func_name_lower for admin_kw in self.ADMIN_KEYWORDS):
                        security_features.append(f"Admin function name: {node.name}")
                        confidence_factors.append(('admin_function_name', 0.6))
                    
                    # Check for sensitive data patterns
                    if any(sens_kw in func_name_lower for sens_kw in self.SENSITIVE_DATA_KEYWORDS):
                        security_features.append(f"Sensitive data function: {node.name}")
                        confidence_factors.append(('sensitive_function_name', 0.7))
                    
                    # Check for public patterns
                    if any(pub_kw in func_name_lower for pub_kw in self.PUBLIC_PATTERNS):
                        security_features.append(f"Public function: {node.name}")
                        confidence_factors.append(('public_function_name', 0.5))
                    
                    # Analyze docstring
                    docstring = ast.get_docstring(node)
                    if docstring:
                        docstring_lower = docstring.lower()
                        if any(sec_kw in docstring_lower for sec_kw in self.SECURITY_DECORATORS):
                            security_features.append("Security mentioned in docstring")
                            confidence_factors.append(('security_docstring', 0.4))
                
                self.generic_visit(node)
                self.current_function = old_function
            
            def _get_decorator_name(self, decorator):
                """Extract decorator name from AST node."""
                if isinstance(decorator, ast.Name):
                    return decorator.id
                elif isinstance(decorator, ast.Attribute):
                    return decorator.attr
                elif isinstance(decorator, ast.Call):
                    if isinstance(decorator.func, ast.Name):
                        return decorator.func.id
                    elif isinstance(decorator.func, ast.Attribute):
                        return decorator.func.attr
                return None
        
        # Visit the AST
        visitor = SecurityVisitor()
        visitor.SECURITY_DECORATORS = self.SECURITY_DECORATORS
        visitor.ADMIN_KEYWORDS = self.ADMIN_KEYWORDS
        visitor.SENSITIVE_DATA_KEYWORDS = self.SENSITIVE_DATA_KEYWORDS
        visitor.PUBLIC_PATTERNS = self.PUBLIC_PATTERNS
        visitor.visit(tree)
        
        return {
            'decorators': decorators,
            'security_features': security_features,
            'confidence_factors': confidence_factors
        }
    
    def _analyze_text_patterns(self, text: str, method: str, path: str) -> Dict[str, List]:
        """
        Analyze text patterns for security indicators.
        
        Args:
            text: Combined text (name + path + description)
            method: HTTP method
            path: URL path
            
        Returns:
            Dict with features and confidence_factors
        """
        features = []
        confidence_factors = []
        
        # Method-based analysis
        if method in ['DELETE', 'PUT', 'PATCH']:
            features.append(f"Destructive HTTP method: {method}")
            confidence_factors.append(('destructive_method', 0.6))
        elif method == 'POST':
            features.append(f"Write HTTP method: {method}")
            confidence_factors.append(('write_method', 0.4))
        elif method == 'GET':
            features.append(f"Read HTTP method: {method}")
            confidence_factors.append(('read_method', 0.2))
        
        # Path-based analysis
        path_lower = path.lower()
        
        # Admin patterns in path
        if any(admin_kw in path_lower for admin_kw in self.ADMIN_KEYWORDS):
            features.append(f"Admin path pattern: {path}")
            confidence_factors.append(('admin_path', 0.8))
        
        # Sensitive data patterns in path
        if any(sens_kw in path_lower for sens_kw in self.SENSITIVE_DATA_KEYWORDS):
            features.append(f"Sensitive data path: {path}")
            confidence_factors.append(('sensitive_path', 0.7))
        
        # Public patterns in path
        if any(pub_kw in path_lower for pub_kw in self.PUBLIC_PATTERNS):
            features.append(f"Public path pattern: {path}")
            confidence_factors.append(('public_path', 0.6))
        
        # Text content analysis
        text_lower = text.lower()
        
        # Security keywords in text
        security_mentions = sum(1 for kw in self.SECURITY_DECORATORS if kw in text_lower)
        if security_mentions > 0:
            features.append(f"Security keywords mentioned: {security_mentions}")
            confidence_factors.append(('security_keywords', min(0.7, security_mentions * 0.2)))
        
        # Admin keywords in text
        admin_mentions = sum(1 for kw in self.ADMIN_KEYWORDS if kw in text_lower)
        if admin_mentions > 0:
            features.append(f"Admin keywords mentioned: {admin_mentions}")
            confidence_factors.append(('admin_keywords', min(0.6, admin_mentions * 0.2)))
        
        # Sensitive data keywords in text
        sensitive_mentions = sum(1 for kw in self.SENSITIVE_DATA_KEYWORDS if kw in text_lower)
        if sensitive_mentions > 0:
            features.append(f"Sensitive keywords mentioned: {sensitive_mentions}")
            confidence_factors.append(('sensitive_keywords', min(0.7, sensitive_mentions * 0.2)))
        
        return {
            'features': features,
            'confidence_factors': confidence_factors
        }
    
    def _classify_security_level(self, decorators: List[str], features: List[str], 
                               confidence_factors: List[Tuple[str, float]], 
                               method: str, text: str) -> Tuple[SecurityLevel, float, str]:
        """
        Classify security level based on analysis results.
        
        Args:
            decorators: List of detected decorators
            features: List of security features
            confidence_factors: List of (factor_name, confidence_value) tuples
            method: HTTP method
            text: Combined text for analysis
            
        Returns:
            Tuple of (SecurityLevel, confidence_score, reasoning)
        """
        # Calculate weighted scores for each security level
        scores = {
            SecurityLevel.PUBLIC: 0.0,
            SecurityLevel.AUTH_REQUIRED: 0.0,
            SecurityLevel.ADMIN_FUNCTIONS: 0.0,
            SecurityLevel.SENSITIVE_DATA: 0.0
        }
        
        reasoning_parts = []
        
        # Analyze confidence factors
        for factor_name, confidence in confidence_factors:
            if factor_name in ['public_function_name', 'public_path']:
                scores[SecurityLevel.PUBLIC] += confidence
                reasoning_parts.append(f"Public pattern detected ({factor_name})")
            
            elif factor_name in ['security_decorator', 'security_keywords', 'security_docstring']:
                scores[SecurityLevel.AUTH_REQUIRED] += confidence
                reasoning_parts.append(f"Authentication indicator ({factor_name})")
            
            elif factor_name in ['admin_function_name', 'admin_path', 'admin_keywords', 'destructive_method']:
                scores[SecurityLevel.ADMIN_FUNCTIONS] += confidence
                reasoning_parts.append(f"Admin function indicator ({factor_name})")
            
            elif factor_name in ['sensitive_function_name', 'sensitive_path', 'sensitive_keywords']:
                scores[SecurityLevel.SENSITIVE_DATA] += confidence
                reasoning_parts.append(f"Sensitive data indicator ({factor_name})")
            
            elif factor_name in ['write_method']:
                scores[SecurityLevel.AUTH_REQUIRED] += confidence * 0.5
                reasoning_parts.append(f"Write operation detected")
            
            elif factor_name in ['read_method']:
                scores[SecurityLevel.PUBLIC] += confidence * 0.3
                reasoning_parts.append(f"Read operation detected")
        
        # Apply security decorator boost
        if any(dec.lower() in ' '.join(decorators).lower() for dec in self.SECURITY_DECORATORS):
            scores[SecurityLevel.AUTH_REQUIRED] += 0.8
            reasoning_parts.append("Security decorators found")
        
        # Find the highest scoring security level
        max_score = max(scores.values())
        best_level = max(scores.keys(), key=lambda k: scores[k])
        
        # Calculate overall confidence (normalize to 0-1 range)
        confidence_score = min(1.0, max_score)
        
        # Apply minimum confidence thresholds and fallback logic
        if confidence_score < 0.3:
            # Low confidence, default to AUTH_REQUIRED for safety
            best_level = SecurityLevel.AUTH_REQUIRED
            confidence_score = 0.3
            reasoning_parts.append("Low confidence, defaulting to auth required for safety")
        
        # Special case: If no strong indicators, use method-based defaults
        if max_score < 0.4:
            if method in ['DELETE', 'PUT', 'PATCH']:
                best_level = SecurityLevel.ADMIN_FUNCTIONS
                confidence_score = 0.5
                reasoning_parts.append(f"Destructive method {method} suggests admin function")
            elif method == 'POST':
                best_level = SecurityLevel.AUTH_REQUIRED
                confidence_score = 0.4
                reasoning_parts.append(f"Write method {method} suggests authentication required")
            elif method == 'GET' and any(pub in text.lower() for pub in self.PUBLIC_PATTERNS):
                best_level = SecurityLevel.PUBLIC
                confidence_score = 0.5
                reasoning_parts.append("GET method with public patterns suggests public access")
        
        reasoning = "; ".join(reasoning_parts) if reasoning_parts else "No specific security indicators found"
        
        return best_level, confidence_score, reasoning


class JavaScriptASTAnalyzer:
    """
    JavaScript/TypeScript AST analyzer for security classification.
    Uses regex patterns since full AST parsing for JS/TS is more complex.
    """
    
    def __init__(self):
        """Initialize the JavaScript analyzer."""
        self.security_patterns = {
            'auth_middleware': [
                r'authenticate', r'requireAuth', r'isAuthenticated', r'checkAuth',
                r'verifyToken', r'jwt\.verify', r'passport\.authenticate'
            ],
            'admin_patterns': [
                r'requireAdmin', r'isAdmin', r'adminOnly', r'checkAdmin',
                r'role.*admin', r'permission.*admin'
            ],
            'sensitive_patterns': [
                r'password', r'secret', r'token', r'key', r'credential',
                r'payment', r'billing', r'private'
            ]
        }
    
    def analyze_endpoint_security(self, endpoint_data: Dict, file_content: str) -> SecurityAnalysis:
        """
        Analyze JavaScript/TypeScript endpoint security.
        
        Args:
            endpoint_data: Endpoint information
            file_content: Content of the JavaScript/TypeScript file
            
        Returns:
            SecurityAnalysis object
        """
        method = endpoint_data.get('method', 'GET')
        path = endpoint_data.get('path', '')
        name = endpoint_data.get('name', '')
        line_number = endpoint_data.get('line')
        
        # Extract relevant code section around the endpoint
        code_section = self._extract_code_section(file_content, line_number)
        
        # Analyze patterns
        detected_patterns = []
        security_features = []
        confidence_factors = []
        
        # Check for authentication middleware
        for pattern in self.security_patterns['auth_middleware']:
            if re.search(pattern, code_section, re.IGNORECASE):
                detected_patterns.append(f"auth_middleware: {pattern}")
                security_features.append(f"Authentication middleware detected: {pattern}")
                confidence_factors.append(('auth_middleware', 0.8))
        
        # Check for admin patterns
        for pattern in self.security_patterns['admin_patterns']:
            if re.search(pattern, code_section, re.IGNORECASE):
                detected_patterns.append(f"admin_pattern: {pattern}")
                security_features.append(f"Admin pattern detected: {pattern}")
                confidence_factors.append(('admin_pattern', 0.7))
        
        # Check for sensitive data patterns
        for pattern in self.security_patterns['sensitive_patterns']:
            if re.search(pattern, code_section, re.IGNORECASE):
                detected_patterns.append(f"sensitive_pattern: {pattern}")
                security_features.append(f"Sensitive data pattern detected: {pattern}")
                confidence_factors.append(('sensitive_pattern', 0.6))
        
        # Classify security level
        security_level, confidence_score, reasoning = self._classify_js_security_level(
            detected_patterns, confidence_factors, method, path, name
        )
        
        return SecurityAnalysis(
            security_level=security_level,
            confidence_score=confidence_score,
            detected_decorators=detected_patterns,
            security_features=security_features,
            reasoning=reasoning,
            file_path=endpoint_data.get('file', ''),
            line_number=line_number
        )
    
    def _extract_code_section(self, content: str, line_number: Optional[int], context_lines: int = 10) -> str:
        """Extract code section around a specific line number."""
        if not line_number:
            return content[:2000]  # Return first 2000 chars if no line number
        
        lines = content.split('\n')
        start = max(0, line_number - context_lines - 1)
        end = min(len(lines), line_number + context_lines)
        
        return '\n'.join(lines[start:end])
    
    def _classify_js_security_level(self, patterns: List[str], confidence_factors: List[Tuple[str, float]], 
                                  method: str, path: str, name: str) -> Tuple[SecurityLevel, float, str]:
        """Classify security level for JavaScript/TypeScript endpoints."""
        # Similar logic to Python classifier but adapted for JS patterns
        scores = {
            SecurityLevel.PUBLIC: 0.0,
            SecurityLevel.AUTH_REQUIRED: 0.0,
            SecurityLevel.ADMIN_FUNCTIONS: 0.0,
            SecurityLevel.SENSITIVE_DATA: 0.0
        }
        
        reasoning_parts = []
        
        # Analyze confidence factors
        for factor_name, confidence in confidence_factors:
            if factor_name == 'auth_middleware':
                scores[SecurityLevel.AUTH_REQUIRED] += confidence
                reasoning_parts.append("Authentication middleware detected")
            elif factor_name == 'admin_pattern':
                scores[SecurityLevel.ADMIN_FUNCTIONS] += confidence
                reasoning_parts.append("Admin pattern detected")
            elif factor_name == 'sensitive_pattern':
                scores[SecurityLevel.SENSITIVE_DATA] += confidence
                reasoning_parts.append("Sensitive data pattern detected")
        
        # Method-based scoring
        if method in ['DELETE', 'PUT', 'PATCH']:
            scores[SecurityLevel.ADMIN_FUNCTIONS] += 0.5
            reasoning_parts.append(f"Destructive method {method}")
        elif method == 'POST':
            scores[SecurityLevel.AUTH_REQUIRED] += 0.3
            reasoning_parts.append(f"Write method {method}")
        
        # Find best level
        max_score = max(scores.values())
        best_level = max(scores.keys(), key=lambda k: scores[k])
        confidence_score = min(1.0, max_score)
        
        # Fallback logic
        if confidence_score < 0.3:
            best_level = SecurityLevel.AUTH_REQUIRED
            confidence_score = 0.3
            reasoning_parts.append("Low confidence, defaulting to auth required")
        
        reasoning = "; ".join(reasoning_parts) if reasoning_parts else "No specific security indicators found"
        
        return best_level, confidence_score, reasoning
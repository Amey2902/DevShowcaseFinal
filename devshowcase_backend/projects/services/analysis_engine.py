import os
import json
import time
from pathlib import Path
from django.conf import settings
import requests


class AnalysisEngine:
    """Service for analyzing project code using Groq AI."""
    
    SUPPORTED_FRAMEWORKS = {
        'python': ['Flask', 'Django', 'FastAPI'],
        'javascript': ['Express.js', 'NestJS'],
        'typescript': ['Express.js', 'NestJS', 'React'],
        'java': ['Spring Boot'],
        'csharp': ['ASP.NET'],
    }
    
    GROQ_API_URL = 'https://api.groq.com/openai/v1/chat/completions'
    GROQ_MODEL = 'llama-3.3-70b-versatile'
    
    def __init__(self, upload_instance):
        """Initialize with a ProjectUpload instance."""
        self.upload = upload_instance
        self.api_key = settings.GROQ_API_KEY
    
    def analyze_project(self, directory_path):
        """
        Analyze project to detect language, framework, and endpoints.
        
        Args:
            directory_path: Path to project directory
            
        Returns:
            dict: Analysis results with detected_language, detected_framework, endpoints
        """
        self.upload.status = 'analyzing'
        self.upload.current_message = 'Analyzing project structure...'
        self.upload.progress_percentage = 50
        self.upload.save()
        
        print(f"=== Starting Project Analysis ===")
        print(f"Directory path: {directory_path}")
        print(f"Directory exists: {os.path.exists(directory_path)}")
        
        try:
            # Detect language and framework
            language, framework = self._detect_language_and_framework(directory_path)
            
            print(f"Detected: {framework} ({language})")
            
            self.upload.detected_language = language
            self.upload.detected_framework = framework
            self.upload.current_message = f'Detected {framework} ({language})'
            self.upload.progress_percentage = 60
            self.upload.save()
            
            # Find relevant code files
            code_files = self._find_code_files(directory_path, language)
            
            print(f"Found {len(code_files)} code files")
            
            if not code_files:
                if language == 'unknown':
                    # For unknown projects with no analyzable files, return empty results
                    print("No analyzable files found in unknown project, returning empty results")
                    return {
                        'detected_language': language,
                        'detected_framework': framework,
                        'endpoints': [],
                        'base_url': f'http://localhost:3000'
                    }
                else:
                    raise ValueError(f"No {language} code files found in project")
            
            # Detect base URL from code
            base_url = self._detect_base_url(code_files, framework)
            
            print(f"Detected base URL: {base_url}")
            
            # Analyze code with AI
            self.upload.current_message = 'AI analyzing code for endpoints...'
            self.upload.progress_percentage = 70
            self.upload.save()
            
            endpoints_data = self._analyze_with_ai(code_files, framework, directory_path)
            
            print(f"Found {len(endpoints_data)} endpoints")
            
            # Perform AST security analysis
            self.upload.current_message = 'Analyzing endpoint security with AST...'
            self.upload.progress_percentage = 75
            self.upload.save()
            
            endpoints_with_security = self._analyze_endpoint_security(endpoints_data, directory_path, language)
            
            print(f"=== Analysis Complete ===")
            
            return {
                'detected_language': language,
                'detected_framework': framework,
                'endpoints': endpoints_with_security,
                'base_url': base_url
            }
            
        except Exception as e:
            print(f"=== Analysis Error ===")
            print(f"Error: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            print(f"=== End Error ===")
            raise
    
    def _detect_language_and_framework(self, directory_path):
        """Detect programming language and framework from project files."""
        path = Path(directory_path)
        
        print(f"=== Language Detection Debug ===")
        print(f"Directory: {directory_path}")
        
        # List all files for debugging
        all_files = list(path.rglob('*'))
        print(f"Total files found: {len(all_files)}")
        for i, file_path in enumerate(all_files[:10]):  # Show first 10 files
            print(f"  {i+1}. {file_path.name} ({'file' if file_path.is_file() else 'dir'})")
        if len(all_files) > 10:
            print(f"  ... and {len(all_files) - 10} more")
        
        # Check for Python frameworks
        python_files = list(path.rglob('*.py'))
        requirements_file = path / 'requirements.txt'
        
        print(f"Python files found: {len(python_files)}")
        print(f"Requirements.txt exists: {requirements_file.exists()}")
        
        if requirements_file.exists() or python_files:
            requirements_content = ''
            if requirements_file.exists():
                requirements_content = requirements_file.read_text().lower()
                print(f"Requirements content (first 200 chars): {requirements_content[:200]}")
            
            if 'flask' in requirements_content or any('flask' in str(f).lower() for f in python_files[:5]):
                return 'python', 'Flask'
            elif 'django' in requirements_content or any('django' in str(f).lower() for f in python_files[:5]):
                return 'python', 'Django'
            elif 'fastapi' in requirements_content or any('fastapi' in str(f).lower() for f in python_files[:5]):
                return 'python', 'FastAPI'
            elif python_files:
                return 'python', 'Flask'  # Default to Flask if Python files found
        
        # Check for JavaScript/TypeScript frameworks
        package_json_file = path / 'package.json'
        js_files = list(path.rglob('*.js')) + list(path.rglob('*.jsx'))
        ts_files = list(path.rglob('*.ts')) + list(path.rglob('*.tsx'))
        
        print(f"Package.json exists: {package_json_file.exists()}")
        print(f"JS files found: {len(js_files)}")
        print(f"TS files found: {len(ts_files)}")
        
        if package_json_file.exists():
            try:
                package_json = json.loads(package_json_file.read_text())
                dependencies = {**package_json.get('dependencies', {}), **package_json.get('devDependencies', {})}
                print(f"Dependencies found: {list(dependencies.keys())[:10]}")
                
                if 'express' in dependencies:
                    return 'javascript', 'Express.js'
                elif '@nestjs/core' in dependencies:
                    return 'typescript', 'NestJS'
                elif 'react' in dependencies:
                    return 'typescript', 'React'
                else:
                    return 'javascript', 'Express.js'  # Default
            except Exception as e:
                print(f"Error reading package.json: {e}")
        elif js_files or ts_files:
            # If we have JS/TS files but no package.json, assume Express.js
            if ts_files:
                return 'typescript', 'Express.js'
            else:
                return 'javascript', 'Express.js'
        
        # Check for Java (Spring Boot)
        java_files = list(path.rglob('*.java'))
        pom_xml = path / 'pom.xml'
        
        print(f"Java files found: {len(java_files)}")
        print(f"pom.xml exists: {pom_xml.exists()}")
        
        if pom_xml.exists() or java_files:
            return 'java', 'Spring Boot'
        
        # Check for C# (ASP.NET)
        cs_files = list(path.rglob('*.cs'))
        csproj_files = list(path.rglob('*.csproj'))
        
        print(f"C# files found: {len(cs_files)}")
        print(f"csproj files found: {len(csproj_files)}")
        
        if csproj_files or cs_files:
            return 'csharp', 'ASP.NET'
        
        # Check for PHP
        php_files = list(path.rglob('*.php'))
        composer_json = path / 'composer.json'
        
        print(f"PHP files found: {len(php_files)}")
        print(f"composer.json exists: {composer_json.exists()}")
        
        if php_files:
            if composer_json.exists():
                try:
                    composer_content = composer_json.read_text().lower()
                    if 'laravel' in composer_content:
                        return 'php', 'Laravel'
                    elif 'symfony' in composer_content:
                        return 'php', 'Symfony'
                except Exception as e:
                    print(f"Error reading composer.json: {e}")
            return 'php', 'PHP'
        
        # Check for Ruby (Rails)
        rb_files = list(path.rglob('*.rb'))
        gemfile = path / 'Gemfile'
        
        print(f"Ruby files found: {len(rb_files)}")
        print(f"Gemfile exists: {gemfile.exists()}")
        
        if rb_files or gemfile.exists():
            return 'ruby', 'Ruby on Rails'
        
        # Check for Go
        go_files = list(path.rglob('*.go'))
        go_mod = path / 'go.mod'
        
        print(f"Go files found: {len(go_files)}")
        print(f"go.mod exists: {go_mod.exists()}")
        
        if go_files or go_mod.exists():
            return 'go', 'Go'
        
        # Check for C/C++
        cpp_files = list(path.rglob('*.cpp')) + list(path.rglob('*.c')) + list(path.rglob('*.h'))
        
        print(f"C/C++ files found: {len(cpp_files)}")
        
        if cpp_files:
            return 'cpp', 'C++'
        
        # If we have any code files at all, try to make a best guess
        all_code_files = python_files + js_files + ts_files + java_files + cs_files + php_files + rb_files + go_files + cpp_files
        
        print(f"Total code files found: {len(all_code_files)}")
        print(f"=== End Language Detection Debug ===")
        
        if all_code_files:
            # Return the most common file type
            if python_files:
                return 'python', 'Flask'
            elif js_files or ts_files:
                return 'javascript', 'Express.js'
            elif java_files:
                return 'java', 'Spring Boot'
            elif cs_files:
                return 'csharp', 'ASP.NET'
            elif php_files:
                return 'php', 'PHP'
            elif rb_files:
                return 'ruby', 'Ruby on Rails'
            elif go_files:
                return 'go', 'Go'
            elif cpp_files:
                return 'cpp', 'C++'
        
        # If we can't detect anything specific, provide a generic fallback
        print("No specific language/framework detected, using generic fallback")
        
        # Check if there are any text files that might contain code
        text_files = []
        for ext in ['.txt', '.md', '.json', '.xml', '.yml', '.yaml', '.env']:
            text_files.extend(list(path.rglob(f'*{ext}')))
        
        if text_files:
            # If we have configuration files, assume it's a web project
            return 'unknown', 'Web Application'
        
        # Last resort - if there are any files at all, assume generic project
        if all_files:
            return 'unknown', 'Generic Project'
        
        # Only raise error if directory is completely empty
        raise ValueError("Project directory appears to be empty or inaccessible")
    
    def _detect_base_url(self, code_files, framework):
        """Detect the base URL (host:port) from code, .env, and server entry files."""
        import re
        from pathlib import Path

        patterns = [
            r'app\.listen\(\s*(\d+)',       # app.listen(5000)
            r'\.listen\(\s*(\d+)',           # server.listen(5000)
            r'PORT\s*[=:]\s*["\']?(\d+)',   # PORT = 5000 or PORT: "5000"
            r'port\s*[=:]\s*["\']?(\d+)',   # port = 5000
            r'localhost:(\d+)',              # localhost:5000
        ]

        detected_port = None

        # Priority 1: check .env files in the project root
        env_candidates = []
        if code_files:
            root = code_files[0].parent
            while root.name:  # walk up to find .env
                env_candidates += list(root.glob('.env')) + list(root.glob('.env.*'))
                root = root.parent
                if len(env_candidates) > 5:
                    break

        for env_file in env_candidates[:3]:
            try:
                content = env_file.read_text(encoding='utf-8', errors='ignore')
                for pattern in patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        port = matches[0]
                        if 1000 <= int(port) <= 65535:
                            detected_port = port
                            break
                if detected_port:
                    break
            except Exception:
                continue

        # Priority 2: check server entry files (server.js, app.js, index.js, main.py, etc.)
        if not detected_port and code_files:
            entry_names = {'server.js', 'app.js', 'index.js', 'main.js', 'server.ts',
                           'app.ts', 'index.ts', 'main.py', 'app.py', 'wsgi.py', 'asgi.py'}
            entry_files = [f for f in code_files if f.name.lower() in entry_names]
            other_files = [f for f in code_files if f not in entry_files]

            for file_path in (entry_files + other_files)[:15]:
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    for pattern in patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        for m in matches:
                            try:
                                port_int = int(m)
                                # Skip common frontend ports (3000 is Vite/CRA default, 5173 is Vite)
                                if port_int in (3000, 5173, 4200, 8080) and framework in ('Web Application', 'Generic Project'):
                                    continue
                                if 1000 <= port_int <= 65535:
                                    detected_port = m
                                    break
                            except ValueError:
                                continue
                        if detected_port:
                            break
                    if detected_port:
                        break
                except Exception:
                    continue

        if detected_port:
            return f'http://localhost:{detected_port}'

        # Fallback defaults by framework
        default_ports = {
            'Express.js': 5000,
            'Flask': 5000,
            'Django': 8000,
            'FastAPI': 8000,
            'NestJS': 3000,
            'Spring Boot': 8080,
            'ASP.NET': 5000,
            'Web Application': 8000,
            'Generic Project': 8000,
        }
        port = default_ports.get(framework, 8000)
        return f'http://localhost:{port}'

    
    def _find_code_files(self, directory_path, language):
        """Find relevant code files based on language."""
        path = Path(directory_path)
        code_files = []
        
        extensions = {
            'python': ['.py'],
            'javascript': ['.js', '.jsx'],
            'typescript': ['.ts', '.tsx'],
            'java': ['.java'],
            'csharp': ['.cs'],
            'php': ['.php'],
            'ruby': ['.rb'],
            'go': ['.go'],
            'cpp': ['.cpp', '.cc', '.cxx'],
            'c': ['.c', '.h'],
            'unknown': ['.js', '.jsx', '.ts', '.tsx', '.py', '.java', '.cs', '.php', '.rb', '.go', '.cpp', '.c', '.h', '.json', '.xml', '.yml', '.yaml']  # Try common file types
        }
        
        # For unknown language, be more permissive and include more file types
        if language == 'unknown':
            # For unknown projects, look for ANY files that might contain useful information
            all_files = []
            for file_path in path.rglob('*'):
                if file_path.is_file():
                    # Skip binary files and common non-code directories
                    skip_patterns = ['node_modules', '__pycache__', 'venv', 'dist', 'build', '.git', '.vscode', '.idea']
                    skip_extensions = ['.exe', '.dll', '.so', '.dylib', '.bin', '.img', '.iso', '.zip', '.tar', '.gz', '.jpg', '.png', '.gif', '.pdf']
                    
                    # Check if file should be skipped
                    should_skip = False
                    for skip_pattern in skip_patterns:
                        if skip_pattern in str(file_path):
                            should_skip = True
                            break
                    
                    if not should_skip:
                        for skip_ext in skip_extensions:
                            if file_path.suffix.lower() == skip_ext:
                                should_skip = True
                                break
                    
                    if not should_skip:
                        all_files.append(file_path)
            
            # Prioritize files that are more likely to contain useful information
            def unknown_priority_score(file_path):
                name_lower = str(file_path).lower()
                score = 0
                
                # High priority for common code files
                code_extensions = ['.js', '.jsx', '.ts', '.tsx', '.py', '.java', '.cs', '.php', '.rb', '.go', '.cpp', '.c', '.h']
                if file_path.suffix.lower() in code_extensions:
                    score += 100
                
                # Medium priority for config and documentation files
                config_extensions = ['.json', '.xml', '.yml', '.yaml', '.toml', '.ini', '.env']
                if file_path.suffix.lower() in config_extensions:
                    score += 50
                
                # Medium priority for documentation
                doc_extensions = ['.md', '.txt', '.rst']
                if file_path.suffix.lower() in doc_extensions:
                    score += 30
                
                # Boost for important filenames
                important_names = ['readme', 'package', 'requirements', 'pom', 'composer', 'gemfile', 'dockerfile', 'makefile']
                for name in important_names:
                    if name in file_path.name.lower():
                        score += 40
                
                # Boost for API/route related files
                api_keywords = ['api', 'route', 'endpoint', 'controller', 'handler', 'server', 'app']
                for keyword in api_keywords:
                    if keyword in name_lower:
                        score += 20
                
                return score
            
            all_files.sort(key=unknown_priority_score, reverse=True)
            code_files = all_files[:15]  # Take top 15 files for unknown projects
            
        else:
            # Original logic for known languages
            exts = extensions.get(language, [])
            
            for ext in exts:
                for file_path in path.rglob(f'*{ext}'):
                    # Skip test files, migrations, node_modules, etc.
                    if any(skip in str(file_path) for skip in ['test', 'spec', 'migration', 'node_modules', '__pycache__', 'venv', 'dist', 'build']):
                        continue
                    
                    code_files.append(file_path)
        
        # Enhanced prioritization for complex projects
        priority_keywords = [
            # High priority - main route files
            'route', 'router', 'api', 'endpoint', 'controller', 'handler',
            # Medium priority - framework specific
            'app', 'server', 'index', 'main',
            # Low priority - but still important
            'view', 'urls', 'middleware'
        ]
        
        def enhanced_priority_score(file_path):
            name_lower = str(file_path).lower()
            score = 0
            
            # Boost for route-related files
            for i, keyword in enumerate(priority_keywords):
                if keyword in name_lower:
                    score += (len(priority_keywords) - i) * 10
            
            # Boost for files in route/api directories
            if any(dir_name in name_lower for dir_name in ['route', 'api', 'controller', 'handler']):
                score += 50
            
            # Boost for main application files
            if any(main_file in file_path.name.lower() for main_file in ['app.js', 'server.js', 'index.js', 'main.js']):
                score += 30
                
            # Penalty for deeply nested files (likely less important)
            depth = len(file_path.parts)
            if depth > 6:
                score -= (depth - 6) * 5
            
            return score
        
        # Sort by enhanced priority
        code_files.sort(key=enhanced_priority_score, reverse=True)
        
        # For complex projects, analyze more files but in smaller batches
        max_files = 12 if len(code_files) > 20 else 8
        selected_files = code_files[:max_files]
        
        print(f"=== File Selection Debug ===")
        print(f"Total code files found: {len(code_files)}")
        print(f"Selected top {len(selected_files)} files:")
        for i, file_path in enumerate(selected_files):
            score = enhanced_priority_score(file_path)
            print(f"  {i+1}. {file_path.name} (score: {score}) - {file_path}")
        print(f"=== End File Selection ===")
        
        return selected_files
    
    def _analyze_with_ai(self, code_files, framework, base_path):
        """Use Groq AI to analyze code and find endpoints."""
        all_endpoints = []
        
        # Adaptive batch size based on project complexity
        if len(code_files) > 10:
            batch_size = 3  # Smaller batches for complex projects
        else:
            batch_size = 4  # Standard batch size
            
        total_batches = (len(code_files) + batch_size - 1) // batch_size
        
        print(f"=== AI Analysis Strategy ===")
        print(f"Total files to analyze: {len(code_files)}")
        print(f"Batch size: {batch_size}")
        print(f"Total batches: {total_batches}")
        print(f"=== Starting Analysis ===")
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(code_files))
            batch_files = code_files[start_idx:end_idx]
            
            try:
                print(f"=== Batch {batch_num + 1}/{total_batches} ===")
                print(f"Files in this batch:")
                for f in batch_files:
                    print(f"  - {f.name}")
                
                # Build prompt for this batch
                prompt = self.build_ai_prompt(batch_files, framework, base_path)
                
                # Call Groq AI with retry logic
                response = self._call_groq_ai_safely(prompt)
                
                # Parse response
                endpoints = self.parse_ai_response(response, framework)
                
                print(f"Found {len(endpoints)} endpoints in batch {batch_num + 1}")
                if endpoints:
                    print("Endpoints found:")
                    for ep in endpoints[:3]:  # Show first 3
                        print(f"  - {ep.get('method', 'GET')} {ep.get('path', 'unknown')}")
                    if len(endpoints) > 3:
                        print(f"  ... and {len(endpoints) - 3} more")
                
                all_endpoints.extend(endpoints)
                
                # Update progress
                progress = 70 + int((batch_num + 1) / total_batches * 9)
                self.upload.progress_percentage = progress
                self.upload.current_message = f'Analyzed batch {batch_num + 1}/{total_batches}, found {len(all_endpoints)} endpoints so far'
                self.upload.save()
                
                # Wait between batches to avoid rate limiting (except for last batch)
                if batch_num < total_batches - 1:
                    wait_time = 3 if len(code_files) > 10 else 2
                    print(f"Waiting {wait_time} seconds before next batch...")
                    time.sleep(wait_time)
                
            except ValueError as e:
                # Log error but continue with other batches
                print(f"Error analyzing batch {batch_num + 1}: {str(e)}")
                continue
        
        print(f"=== Analysis Complete ===")
        print(f"Total endpoints found: {len(all_endpoints)}")
        
        return all_endpoints
    
    def build_ai_prompt(self, code_files, framework, base_path):
        """Build AI prompt for endpoint detection."""
        base = Path(base_path)
        
        # Collect COMPLETE code - NO TRUNCATION
        code_snippets = []
        for file_path in code_files:
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                relative_path = file_path.relative_to(base)
                # Send FULL file content - no limits!
                code_snippets.append(f"File: {relative_path}\n```\n{content}\n```\n")
            except Exception as e:
                print(f"Error reading file {file_path}: {str(e)}")
                continue
        
        code_text = "\n\n".join(code_snippets)
        
        print(f"=== Building AI Prompt ===")
        print(f"Framework: {framework}")
        print(f"Number of files: {len(code_files)}")
        print(f"Code snippets collected: {len(code_snippets)}")
        print(f"Total code length: {len(code_text)} characters")
        if len(code_snippets) > 0:
            print(f"First file sample (200 chars): {code_text[:200]}")
        print(f"=== End Prompt Info ===")
        
        # Framework-specific instructions
        framework_hints = {
            'Express.js': '''Look for ALL route definitions including:
- app.get(), app.post(), app.put(), app.delete(), app.patch()
- router.get(), router.post(), router.put(), router.delete(), router.patch()
- app.use() with route paths
- Express Router instances
Find EVERY endpoint, even if there are many in one file.''',
            'Flask': 'Look for ALL @app.route() and @blueprint.route() decorators',
            'Django': 'Look for ALL path() or url() calls in urls.py files',
            'FastAPI': 'Look for ALL @app.get(), @app.post(), @router.get(), @router.post() decorators',
            'NestJS': 'Look for ALL @Get(), @Post(), @Put(), @Delete(), @Patch() decorators in @Controller() classes',
            'Spring Boot': 'Look for ALL @GetMapping, @PostMapping, @PutMapping, @DeleteMapping, @RequestMapping annotations',
            'ASP.NET': 'Look for ALL [HttpGet], [HttpPost], [HttpPut], [HttpDelete], [Route] attributes',
            'Web Application': '''Look for ANY HTTP endpoint definitions including:
- Express.js routes: app.get(), app.post(), router.get(), etc.
- Flask routes: @app.route(), @blueprint.route()
- Django URLs: path(), url() calls
- FastAPI routes: @app.get(), @app.post(), @router.get(), etc.
- Spring Boot: @GetMapping, @PostMapping, @RequestMapping
- ASP.NET: [HttpGet], [HttpPost], [Route] attributes
- Any other HTTP route definitions you can identify''',
            'Generic Project': '''Look for ANY HTTP endpoint definitions in any format:
- Route handlers, URL patterns, API endpoints
- HTTP method decorators or annotations
- Server route configurations
- API documentation or specifications
Find any patterns that look like web API endpoints.'''
        }
        
        hint = framework_hints.get(framework, 'Look for ALL HTTP endpoint definitions')
        
        prompt = f"""You are analyzing a {framework} project to detect BACKEND API endpoints only.

{hint}

CRITICAL RULES:
1. Find and list EVERY SINGLE backend API endpoint in the code below. Do not skip any.
2. ONLY include real HTTP API endpoints that a server handles and returns data from (like Express routes, Flask routes, Django URLs, FastAPI routes, etc.)
3. DO NOT include React Router routes, Vue Router routes, Angular routes, or any frontend client-side routing (e.g. <Route path="/home">, createBrowserRouter, useNavigate, history.push, etc.)
4. DO NOT include frontend page components or navigation links as endpoints.
5. If this is a pure frontend project (React, Vue, Angular) with NO backend server code, return {{"endpoints": []}}

Project Code:
{code_text}

Return your response in this EXACT JSON format (no markdown, no extra text):
{{
  "endpoints": [
    {{
      "file": "path/to/file.js",
      "line": 10,
      "method": "GET",
      "path": "/api/users",
      "name": "Get Users",
      "description": "Retrieves list of users",
      "auth_required": false,
      "auth_type": "",
      "path_parameters": [],
      "query_parameters": [],
      "request_schema": {{}},
      "response_schema": {{}}
    }}
  ]
}}

IMPORTANT: Include ALL backend API endpoints you find. If this is frontend-only with no server, return {{"endpoints": []}}.

Return ONLY the JSON object, nothing else."""
        
        return prompt
    
    def parse_ai_response(self, response_text, framework):
        """Parse AI response to extract endpoint data."""
        # Log the raw response for debugging
        print(f"=== AI Response (first 1000 chars) ===")
        print(response_text[:1000])
        print(f"=== End AI Response ===")
        
        try:
            # Try to extract JSON from response
            # Sometimes AI adds markdown code blocks
            if '```json' in response_text:
                json_start = response_text.find('```json') + 7
                json_end = response_text.find('```', json_start)
                response_text = response_text[json_start:json_end].strip()
            elif '```' in response_text:
                json_start = response_text.find('```') + 3
                json_end = response_text.find('```', json_start)
                response_text = response_text[json_start:json_end].strip()
            
            # Remove any leading/trailing whitespace
            response_text = response_text.strip()
            
            print(f"=== Cleaned response (first 500 chars) ===")
            print(response_text[:500])
            print(f"=== End Cleaned ===")
            
            data = json.loads(response_text)
            endpoints = data.get('endpoints', [])
            
            print(f"=== Parsed {len(endpoints)} endpoints ===")
            if len(endpoints) > 0:
                print(f"First endpoint: {endpoints[0]}")
            
            return endpoints
            
        except json.JSONDecodeError as e:
            # Log the error for debugging
            print(f"=== JSON Parse Error ===")
            print(f"Error: {str(e)}")
            print(f"Response text (first 500 chars): {response_text[:500]}")
            print(f"=== End Error ===")
            # If JSON parsing fails, return empty list
            return []

    
    def _call_groq_ai_safely(self, prompt, max_retries=5):
        """Call Groq AI with retry logic and error handling."""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        
        payload = {
            'model': self.GROQ_MODEL,
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.1,
            'max_tokens': 8000,  # Increased to handle more endpoints in response
        }
        
        for attempt in range(max_retries):
            try:
                print(f"=== Groq AI Call Attempt {attempt + 1}/{max_retries} ===")
                print(f"Prompt length: {len(prompt)} characters")
                
                response = requests.post(
                    self.GROQ_API_URL,
                    headers=headers,
                    json=payload,
                    timeout=90  # Increased timeout to 90 seconds for larger prompts
                )
                
                print(f"Response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    return data['choices'][0]['message']['content']
                elif response.status_code == 429:
                    # Rate limited, wait longer with exponential backoff
                    wait_time = min(10 * (2 ** attempt), 60)  # Cap at 60 seconds
                    print(f"Rate limited, waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                elif response.status_code == 400:
                    # Bad request - likely prompt too long
                    print(f"Bad request (400): {response.text}")
                    raise ValueError(f"Prompt might be too long. Try uploading a smaller project or fewer files.")
                else:
                    print(f"Groq API error: {response.status_code} - {response.text}")
                    raise ValueError(f"Groq API error: {response.status_code}")
                    
            except requests.Timeout:
                print(f"Request timed out on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    wait_time = 5 * (2 ** attempt)
                    print(f"Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    continue
                raise ValueError("Groq AI request timed out after 90 seconds")
            except Exception as e:
                print(f"Exception on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    wait_time = 5 * (2 ** attempt)
                    print(f"Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    continue
                raise ValueError(f"Groq AI error: {str(e)}")
        
        raise ValueError("Failed to get response from Groq AI after retries")
    
    def _analyze_endpoint_security(self, endpoints_data, directory_path, language):
        """
        Analyze endpoint security using AST analysis.
        
        Args:
            endpoints_data: List of endpoint dictionaries from AI analysis
            directory_path: Path to project directory
            language: Detected programming language
            
        Returns:
            List of endpoints with security analysis added
        """
        from .ast_analyzer import ASTSecurityAnalyzer, JavaScriptASTAnalyzer
        
        print(f"=== Starting AST Security Analysis ===")
        print(f"Language: {language}")
        print(f"Endpoints to analyze: {len(endpoints_data)}")
        
        try:
            if language == 'python':
                # Use Python AST analyzer
                analyzer = ASTSecurityAnalyzer()
                security_results = analyzer.analyze_project_security(directory_path, endpoints_data)
            
            elif language in ['javascript', 'typescript']:
                # Use JavaScript/TypeScript analyzer
                analyzer = JavaScriptASTAnalyzer()
                security_results = {}
                
                # Read file contents for JS/TS analysis
                for endpoint_data in endpoints_data:
                    file_path = endpoint_data.get('file', '')
                    if file_path:
                        try:
                            full_path = os.path.join(directory_path, file_path)
                            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                                file_content = f.read()
                            
                            endpoint_key = f"{endpoint_data.get('method', 'GET')}:{endpoint_data.get('path', '')}"
                            analysis = analyzer.analyze_endpoint_security(endpoint_data, file_content)
                            security_results[endpoint_key] = analysis
                            
                        except Exception as e:
                            print(f"Error analyzing JS/TS endpoint {endpoint_data}: {e}")
                            continue
            
            else:
                # For other languages, provide basic analysis based on patterns
                security_results = self._basic_security_analysis(endpoints_data)
            
            # Merge security analysis with endpoint data
            enhanced_endpoints = []
            for endpoint_data in endpoints_data:
                endpoint_key = f"{endpoint_data.get('method', 'GET')}:{endpoint_data.get('path', '')}"
                
                if endpoint_key in security_results:
                    analysis = security_results[endpoint_key]
                    
                    # Add security analysis to endpoint data
                    endpoint_data['ast_security_level'] = analysis.security_level.value
                    endpoint_data['ast_confidence_score'] = analysis.confidence_score
                    endpoint_data['detected_decorators'] = analysis.detected_decorators
                    endpoint_data['security_features'] = analysis.security_features
                    endpoint_data['ast_reasoning'] = analysis.reasoning
                    
                    print(f"Enhanced {endpoint_key}: {analysis.security_level.value} (confidence: {analysis.confidence_score:.2f})")
                
                enhanced_endpoints.append(endpoint_data)
            
            print(f"=== AST Security Analysis Complete ===")
            return enhanced_endpoints
            
        except Exception as e:
            print(f"AST Security Analysis failed: {e}")
            # Return original endpoints without security analysis if AST fails
            return endpoints_data
    
    def _basic_security_analysis(self, endpoints_data):
        """
        Provide basic security analysis for unsupported languages.
        
        Args:
            endpoints_data: List of endpoint dictionaries
            
        Returns:
            Dict of security analysis results
        """
        from .ast_analyzer import SecurityLevel, SecurityAnalysis
        
        results = {}
        
        for endpoint_data in endpoints_data:
            method = endpoint_data.get('method', 'GET')
            path = endpoint_data.get('path', '').lower()
            name = endpoint_data.get('name', '').lower()
            
            # Basic pattern matching
            if any(keyword in f"{path} {name}" for keyword in ['admin', 'delete', 'remove', 'destroy']):
                security_level = SecurityLevel.ADMIN_FUNCTIONS
                confidence = 0.6
                reasoning = "Admin/destructive patterns detected in path or name"
            elif any(keyword in f"{path} {name}" for keyword in ['auth', 'login', 'token', 'password']):
                security_level = SecurityLevel.SENSITIVE_DATA
                confidence = 0.5
                reasoning = "Authentication/sensitive data patterns detected"
            elif method in ['DELETE', 'PUT', 'PATCH']:
                security_level = SecurityLevel.AUTH_REQUIRED
                confidence = 0.4
                reasoning = f"Destructive HTTP method: {method}"
            elif any(keyword in f"{path} {name}" for keyword in ['public', 'health', 'status', 'info']):
                security_level = SecurityLevel.PUBLIC
                confidence = 0.5
                reasoning = "Public endpoint patterns detected"
            else:
                security_level = SecurityLevel.AUTH_REQUIRED
                confidence = 0.3
                reasoning = "Default classification for safety"
            
            endpoint_key = f"{endpoint_data.get('method', 'GET')}:{endpoint_data.get('path', '')}"
            
            results[endpoint_key] = SecurityAnalysis(
                security_level=security_level,
                confidence_score=confidence,
                detected_decorators=[],
                security_features=[f"Basic pattern analysis for {method} {path}"],
                reasoning=reasoning,
                file_path=endpoint_data.get('file', ''),
                line_number=endpoint_data.get('line')
            )
        
        return results

import os
import re
from pathlib import Path


class SecurityScanner:
    """Service for scanning uploaded files for security threats."""
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {
        # Python
        '.py', '.pyi', '.pyx',
        # JavaScript/TypeScript
        '.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs',
        # Java
        '.java',
        # C#
        '.cs', '.csx',
        # Config files
        '.json', '.yaml', '.yml', '.toml', '.ini', '.env.example', '.xml',
        '.yarnrc', '.npmrc', '.babelrc', '.eslintrc', '.prettierrc',
        # Documentation
        '.md', '.txt', '.rst', '.pdf',
        # Web & Templates
        '.html', '.css', '.scss', '.sass', '.less',
        '.pug', '.jade', '.ejs', '.hbs', '.handlebars', '.mustache',
        # Package files
        'requirements.txt', 'package.json', 'pom.xml', '.csproj', 'package-lock.json',
        'yarn.lock', 'Pipfile', 'Pipfile.lock', 'setup.py', 'setup.cfg', 'pyproject.toml',
        # Git and version control
        '.gitignore', '.gitattributes', '.dockerignore',
        # Docker (explicitly allow)
        '.dockerfile',
        # Shell scripts (for legitimate build/test scripts)
        '.sh', '.bash', '.zsh',
        # CI/CD
        '.travis.yml', '.gitlab-ci.yml', 'Jenkinsfile',
        # Editor configs
        '.editorconfig',
        # License and readme (case-insensitive check below)
    }
    
    # Files allowed by name (case-insensitive)
    ALLOWED_FILENAMES = {
        'dockerfile', 'license', 'readme', 'changelog', 'contributing', 'notice',
        'makefile', 'rakefile', 'gemfile', 'procfile'
    }
    
    # Forbidden patterns that indicate malicious code
    FORBIDDEN_PATTERNS = [
        # Command execution (dangerous ones only)
        r'os\.system\s*\(',
        r'subprocess\.call\s*\(',
        r'subprocess\.run\s*\(',
        r'subprocess\.Popen\s*\(',
        # eval is dangerous
        r'eval\s*\(',
        r'__import__\s*\(',
        # File system manipulation (dangerous)
        r'os\.remove\s*\(',
        r'os\.rmdir\s*\(',
        r'shutil\.rmtree\s*\(',
        r'os\.unlink\s*\(',
        # Network operations (very suspicious)
        r'socket\.socket\s*\(',
        # JavaScript dangerous functions
        r'Function\s*\(',
        r'fs\.unlink',
        r'fs\.rmdir',
    ]

    
    def __init__(self, upload_instance):
        """Initialize with a ProjectUpload instance."""
        self.upload = upload_instance
    
    def scan_directory(self, directory_path):
        """
        Scan a directory for security threats.
        
        Args:
            directory_path: Path to directory to scan
            
        Returns:
            dict: Scan results with 'safe' boolean and 'issues' list
            
        Raises:
            ValueError: If security threats are detected
        """
        self.upload.status = 'scanning'
        self.upload.current_message = 'Scanning for security threats...'
        self.upload.progress_percentage = 30
        self.upload.save()
        
        issues = []
        scanned_files = 0
        
        # Scan all files in directory
        for root, dirs, files in os.walk(directory_path):
            # Skip hidden directories and common ignore patterns
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', 'env']]
            
            for file in files:
                file_path = Path(root) / file
                
                # Validate file type
                if not self.validate_file_type(file_path):
                    issues.append(f"Disallowed file type: {file_path.relative_to(directory_path)}")
                    continue
                
                # Scan file content for forbidden patterns
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        for pattern in self.FORBIDDEN_PATTERNS:
                            matches = re.finditer(pattern, content, re.IGNORECASE)
                            for match in matches:
                                line_num = content[:match.start()].count('\n') + 1
                                issues.append(
                                    f"Suspicious pattern '{pattern}' in {file_path.relative_to(directory_path)}:{line_num}"
                                )
                except Exception:
                    # Skip files that can't be read as text
                    pass
                
                scanned_files += 1
        
        # Update progress
        self.upload.progress_percentage = 40
        self.upload.current_message = f'Scanned {scanned_files} files'
        self.upload.save()
        
        # If issues found, raise error
        if issues:
            error_msg = "Security scan failed:\n" + "\n".join(issues[:10])  # Limit to first 10 issues
            raise ValueError(error_msg)
        
        return {
            'safe': True,
            'scanned_files': scanned_files,
            'issues': []
        }

    
    def validate_file_type(self, file_path):
        """
        Validate if a file type is allowed.
        
        Args:
            file_path: Path object for the file
            
        Returns:
            bool: True if file type is allowed
        """
        file_name = file_path.name.lower()
        file_ext = file_path.suffix.lower()
        
        # Check if extension is allowed
        if file_ext in self.ALLOWED_EXTENSIONS:
            return True
        
        # Check if filename is allowed (case-insensitive)
        if file_name in self.ALLOWED_FILENAMES:
            return True
        
        # Check filename without extension
        file_stem = file_path.stem.lower()
        if file_stem in self.ALLOWED_FILENAMES:
            return True
        
        return False

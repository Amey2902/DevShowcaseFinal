#!/usr/bin/env python3
"""
Demo script showing how AST security analysis works.
This demonstrates the key concept: AST provides intelligent suggestions, users have full control.
"""

import sys
import os
sys.path.append('devshowcase_backend')

# Mock Django setup for testing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

def demo_ast_analysis():
    """Demonstrate AST security analysis with sample endpoints."""
    
    print("🧠 AST Security Analysis Demo")
    print("=" * 50)
    print()
    
    # Sample endpoints that would be detected by AI
    sample_endpoints = [
        {
            'method': 'GET',
            'path': '/api/users',
            'name': 'Get Users',
            'description': 'Retrieve list of users',
            'file': 'api/users.py',
            'line': 15
        },
        {
            'method': 'DELETE',
            'path': '/api/admin/users/{id}',
            'name': 'Delete User',
            'description': 'Admin function to delete user account',
            'file': 'api/admin.py',
            'line': 42
        },
        {
            'method': 'POST',
            'path': '/api/auth/login',
            'name': 'User Login',
            'description': 'Authenticate user with credentials',
            'file': 'api/auth.py',
            'line': 28
        },
        {
            'method': 'GET',
            'path': '/api/health',
            'name': 'Health Check',
            'description': 'Public health status endpoint',
            'file': 'api/health.py',
            'line': 10
        }
    ]
    
    # Import our AST analyzer
    try:
        from devshowcase_backend.projects.services.ast_analyzer import ASTSecurityAnalyzer, SecurityLevel
        analyzer = ASTSecurityAnalyzer()
        
        print("📊 AST Analysis Results:")
        print("-" * 30)
        
        for endpoint in sample_endpoints:
            # Simulate basic analysis (without actual AST parsing for demo)
            method = endpoint['method']
            path = endpoint['path'].lower()
            name = endpoint['name'].lower()
            description = endpoint['description'].lower()
            
            # Determine security level based on patterns
            if 'admin' in path or 'delete' in method or 'delete' in name:
                security_level = SecurityLevel.ADMIN_FUNCTIONS
                confidence = 0.8
                reasoning = "Admin/destructive patterns detected"
            elif 'auth' in path or 'login' in name or 'password' in description:
                security_level = SecurityLevel.SENSITIVE_DATA
                confidence = 0.7
                reasoning = "Authentication/sensitive data patterns"
            elif 'health' in path or 'status' in path or 'public' in description:
                security_level = SecurityLevel.PUBLIC
                confidence = 0.6
                reasoning = "Public endpoint patterns detected"
            else:
                security_level = SecurityLevel.AUTH_REQUIRED
                confidence = 0.4
                reasoning = "Default classification for safety"
            
            print(f"🔍 {method} {endpoint['path']}")
            print(f"   📋 Name: {endpoint['name']}")
            print(f"   🛡️  AST Suggests: {security_level.value.upper()}")
            print(f"   📊 Confidence: {confidence:.0%}")
            print(f"   💭 Reasoning: {reasoning}")
            print(f"   👤 User Control: Can override to any level")
            print()
        
        print("✅ Key Benefits of AST + User Control:")
        print("   • AST provides intelligent security suggestions")
        print("   • AI analyzes code structure and patterns")
        print("   • Users can override any classification")
        print("   • No endpoints are hidden or blocked")
        print("   • Graduated security levels (not just show/hide)")
        print("   • Confidence scores help users make decisions")
        print()
        
        print("🎯 User Experience:")
        print("   1. Upload project → AST analyzes code")
        print("   2. See endpoints with security suggestions")
        print("   3. Review AST reasoning and confidence")
        print("   4. Override any classification if needed")
        print("   5. All endpoints remain visible and editable")
        
    except ImportError as e:
        print(f"❌ Could not import AST analyzer: {e}")
        print("   This is expected in demo mode without full Django setup")

if __name__ == "__main__":
    demo_ast_analysis()
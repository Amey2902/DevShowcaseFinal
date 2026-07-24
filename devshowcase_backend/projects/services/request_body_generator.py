import json
import requests
from django.conf import settings


class RequestBodyGenerator:
    """Generate realistic request bodies for API endpoints using AI or schema."""
    
    GROQ_API_URL = 'https://api.groq.com/openai/v1/chat/completions'
    GROQ_MODEL = 'llama-3.3-70b-versatile'
    
    @staticmethod
    def generate_from_schema(schema):
        """Generate a clean JSON request body strictly from request_schema."""
        if not schema or not isinstance(schema, dict):
            return None
            
        # 1. If schema has a direct example dict, use it!
        if 'example' in schema and isinstance(schema['example'], dict) and len(schema['example']) > 0:
            return schema['example']
            
        # 2. Extract properties
        properties = schema.get('properties', {})
        if not properties and 'type' not in schema:
            properties = {k: v for k, v in schema.items() if k not in ['type', 'required', 'description', 'example']}
            
        if not properties:
            return None
            
        body = {}
        for field_name, info in properties.items():
            if isinstance(info, str):
                info = {'type': info}
            elif not isinstance(info, dict):
                info = {'type': 'string'}
                
            ftype = info.get('type', 'string').lower()
            fname_lower = field_name.lower()
            
            if 'example' in info:
                body[field_name] = info['example']
                continue
            if 'default' in info:
                body[field_name] = info['default']
                continue
            if 'enum' in info and isinstance(info['enum'], list) and info['enum']:
                body[field_name] = info['enum'][0]
                continue
                
            if ftype in ('string', 'str'):
                if 'email' in fname_lower or info.get('format') == 'email':
                    body[field_name] = 'user@example.com'
                elif 'password' in fname_lower or info.get('format') == 'password':
                    body[field_name] = 'Password123!'
                elif 'role' in fname_lower:
                    body[field_name] = 'user'
                elif 'name' in fname_lower:
                    body[field_name] = 'John Doe'
                else:
                    body[field_name] = f"sample_{field_name}"
            elif ftype in ('integer', 'number', 'int', 'float'):
                body[field_name] = 10 if 'age' in fname_lower else 1
            elif ftype in ('boolean', 'bool'):
                body[field_name] = True
            elif ftype in ('array', 'list'):
                body[field_name] = []
            elif ftype in ('object', 'dict'):
                body[field_name] = {}
            else:
                body[field_name] = f"sample_{field_name}"
                
        return body

    @staticmethod
    def generate_request_body(endpoint):
        """Generate a realistic request body for an endpoint using schema or AI."""
        
        # GET and DELETE typically don't need request bodies
        if endpoint.method in ['GET', 'DELETE']:
            return {}
        
        # If we already have a good sample body, keep it
        if endpoint.sample_body and len(endpoint.sample_body) > 0:
            if not all(v in ['', 'string', 'demo', 'test'] for v in endpoint.sample_body.values()):
                return endpoint.sample_body
                
        # 1. Try generating strictly from request_schema FIRST (no assumptions!)
        if endpoint.request_schema:
            schema_body = RequestBodyGenerator.generate_from_schema(endpoint.request_schema)
            if schema_body and len(schema_body) > 0:
                return schema_body

            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            }
            
            payload = {
                'model': RequestBodyGenerator.GROQ_MODEL,
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': 0.3,
                'max_tokens': 1000,
            }
            
            response = requests.post(
                RequestBodyGenerator.GROQ_API_URL,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data['choices'][0]['message']['content']
                
                # Clean up response (remove markdown if present)
                if '```json' in ai_response:
                    json_start = ai_response.find('```json') + 7
                    json_end = ai_response.find('```', json_start)
                    ai_response = ai_response[json_start:json_end].strip()
                elif '```' in ai_response:
                    json_start = ai_response.find('```') + 3
                    json_end = ai_response.find('```', json_start)
                    ai_response = ai_response[json_start:json_end].strip()
                
                # Parse and return
                request_body = json.loads(ai_response.strip())
                return request_body
            else:
                print(f"Groq API error: {response.status_code}")
                return RequestBodyGenerator._generate_fallback_body(endpoint)
                
        except Exception as e:
            print(f"Error generating request body: {str(e)}")
            return RequestBodyGenerator._generate_fallback_body(endpoint)
    
    @staticmethod
    def _generate_fallback_body(endpoint):
        """Generate a basic fallback request body if AI fails."""
        
        # Analyze endpoint name and URL to guess fields
        name_lower = endpoint.name.lower()
        url_lower = endpoint.url.lower()
        
        # Common patterns
        if 'user' in name_lower or 'user' in url_lower:
            return {
                "username": "john_doe",
                "email": "john.doe@example.com",
                "password": "SecurePass123!",
                "firstName": "John",
                "lastName": "Doe"
            }
        elif 'login' in name_lower or 'auth' in name_lower:
            return {
                "email": "user@example.com",
                "password": "password123"
            }
        elif 'post' in name_lower or 'article' in name_lower or 'blog' in name_lower:
            return {
                "title": "Sample Post Title",
                "content": "This is sample content for the post.",
                "author": "John Doe",
                "published": True
            }
        elif 'product' in name_lower or 'item' in name_lower:
            return {
                "name": "Sample Product",
                "description": "A great product",
                "price": 29.99,
                "quantity": 100,
                "category": "Electronics"
            }
        elif 'order' in name_lower or 'purchase' in name_lower:
            return {
                "productId": 1,
                "quantity": 2,
                "shippingAddress": "123 Main St, City, State 12345",
                "paymentMethod": "credit_card"
            }
        elif 'comment' in name_lower or 'review' in name_lower:
            return {
                "text": "This is a sample comment",
                "rating": 5,
                "author": "John Doe"
            }
        elif 'message' in name_lower or 'chat' in name_lower:
            return {
                "message": "Hello, this is a test message",
                "sender": "user123",
                "timestamp": "2024-01-01T12:00:00Z"
            }
        else:
            # Generic fallback
            return {
                "title": "Sample Title",
                "description": "Sample description",
                "data": "Sample data"
            }

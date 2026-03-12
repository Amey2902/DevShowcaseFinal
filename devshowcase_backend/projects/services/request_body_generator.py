import json
import requests
from django.conf import settings


class RequestBodyGenerator:
    """Generate realistic request bodies for API endpoints using AI."""
    
    GROQ_API_URL = 'https://api.groq.com/openai/v1/chat/completions'
    GROQ_MODEL = 'llama-3.3-70b-versatile'
    
    @staticmethod
    def generate_request_body(endpoint):
        """Generate a realistic request body for an endpoint using AI."""
        
        # GET and DELETE typically don't need request bodies
        if endpoint.method in ['GET', 'DELETE']:
            return {}
        
        # If we already have a good sample body, keep it
        if endpoint.sample_body and len(endpoint.sample_body) > 0:
            # Check if it looks like a real sample (not just empty or placeholder)
            if not all(v in ['', 'string', 'demo', 'test'] for v in endpoint.sample_body.values()):
                return endpoint.sample_body
        
        # Use AI to generate a realistic request body
        try:
            api_key = settings.GROQ_API_KEY
            
            prompt = f"""Generate a realistic JSON request body for this API endpoint:

Endpoint: {endpoint.name}
Method: {endpoint.method}
URL: {endpoint.url}
Description: {endpoint.description or 'No description'}

Requirements:
1. Create realistic sample data that makes sense for this endpoint
2. Use appropriate data types (strings, numbers, booleans, arrays, objects)
3. Include all likely required fields
4. Use realistic values (real names, emails, dates, etc.)
5. Return ONLY valid JSON, no markdown, no explanations

Example for a "Create User" endpoint:
{{
  "username": "john_doe",
  "email": "john.doe@example.com",
  "password": "SecurePass123!",
  "firstName": "John",
  "lastName": "Doe",
  "age": 28
}}

Now generate the request body for the endpoint above:"""

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

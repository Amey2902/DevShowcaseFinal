import os
import jwt
import requests
from django.contrib.auth.models import User
from rest_framework import authentication
from rest_framework import exceptions
from functools import lru_cache


class ClerkAuthentication(authentication.BaseAuthentication):
    @lru_cache(maxsize=1)
    def get_jwks(self):
        clerk_domain = os.environ.get('CLERK_DOMAIN', 'clerk.your-domain.com')
        jwks_url = f'https://{clerk_domain}/.well-known/jwks.json'
        response = requests.get(jwks_url, timeout=10)
        response.raise_for_status()
        return response.json()

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        
        try:
            jwks = self.get_jwks()
            unverified_header = jwt.get_unverified_header(token)
            
            rsa_key = {}
            for key in jwks['keys']:
                if key['kid'] == unverified_header['kid']:
                    rsa_key = {
                        'kty': key['kty'],
                        'kid': key['kid'],
                        'use': key['use'],
                        'n': key['n'],
                        'e': key['e']
                    }
            
            if not rsa_key:
                raise exceptions.AuthenticationFailed('Invalid token')
            
            clerk_audience = os.environ.get('CLERK_AUDIENCE', 'your-clerk-frontend-api')
            
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=['RS256'],
                audience=clerk_audience,
                options={'verify_exp': True}
            )
            
            user_id = payload.get('sub')
            if not user_id:
                raise exceptions.AuthenticationFailed('Invalid token')
            
            email = payload.get('email', f'{user_id}@clerk.user')
            
            user, created = User.objects.get_or_create(
                username=user_id,
                defaults={'email': email}
            )
            
            return (user, None)
            
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token expired')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token')
        except requests.RequestException as e:
            raise exceptions.AuthenticationFailed(f'Authentication failed: {str(e)}')
        except Exception as e:
            raise exceptions.AuthenticationFailed(f'Authentication failed: {str(e)}')

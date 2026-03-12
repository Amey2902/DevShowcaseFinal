#!/usr/bin/env python
"""
Quick login script - extracts token from magic link and logs you in
Usage: python quick_login.py <magic_link_url>
"""

import sys
import os
import django
from dotenv import load_dotenv

# Load .env
load_dotenv('.env')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import MagicLink
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

def quick_login(magic_link_url):
    # Extract token from URL
    token = magic_link_url.split('/')[-1]
    
    print(f"Token: {token}")
    
    try:
        magic_link = MagicLink.objects.get(token=token)
        print(f"✅ Magic link found for: {magic_link.email}")
        
        if not magic_link.is_valid():
            print("❌ Magic link has expired or been used")
            return
        
        # Mark as used
        magic_link.mark_as_used()
        
        # Get or create user
        email = magic_link.email
        try:
            user = User.objects.get(email=email)
            print(f"✅ User found: {user.username}")
        except User.DoesNotExist:
            username = email.split('@')[0]
            user = User.objects.create_user(username=username, email=email)
            print(f"✅ New user created: {user.username}")
        
        # Get auth token
        auth_token, _ = Token.objects.get_or_create(user=user)
        
        print("\n" + "="*80)
        print("SUCCESS! You're logged in!")
        print("="*80)
        print(f"\nYour auth token: {auth_token.key}")
        print(f"\nTo use in browser:")
        print(f"1. Go to: http://localhost:3001/dashboard")
        print(f"2. Open browser console (F12)")
        print(f"3. Run: localStorage.setItem('token', '{auth_token.key}')")
        print(f"4. Run: localStorage.setItem('user', '{{\\"username\\":\\"{user.username}\\",\\"email\\":\\"{user.email}\\"}}')") 
        print(f"5. Refresh the page")
        print("="*80)
        
    except MagicLink.DoesNotExist:
        print("❌ Invalid magic link token")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python quick_login.py <magic_link_url>")
        print("Example: python quick_login.py http://localhost:3001/auth/verify/abc123...")
        sys.exit(1)
    
    quick_login(sys.argv[1])

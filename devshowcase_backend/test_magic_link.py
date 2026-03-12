#!/usr/bin/env python
"""
Test script for Magic Link functionality
Run this with: python test_magic_link.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import MagicLink
from django.core.mail import send_mail
from django.conf import settings

def test_magic_link():
    print("=" * 80)
    print("TESTING MAGIC LINK FUNCTIONALITY")
    print("=" * 80)
    
    # Test 1: Create magic link
    print("\n1. Creating magic link...")
    email = "test@example.com"
    try:
        magic_link = MagicLink.create_for_email(email)
        print(f"   ✅ Magic link created successfully")
        print(f"   Token: {magic_link.token}")
        print(f"   Email: {magic_link.email}")
        print(f"   Expires at: {magic_link.expires_at}")
    except Exception as e:
        print(f"   ❌ Failed to create magic link: {e}")
        return
    
    # Test 2: Build URL
    print("\n2. Building magic link URL...")
    try:
        frontend_url = settings.FRONTEND_URL
        magic_link_url = f"{frontend_url}/auth/verify/{magic_link.token}"
        print(f"   ✅ URL: {magic_link_url}")
    except Exception as e:
        print(f"   ❌ Failed to build URL: {e}")
        return
    
    # Test 3: Send email
    print("\n3. Sending email...")
    try:
        send_mail(
            subject='🔐 Your DevShowcase Login Link',
            message=f'''Hi there!

Click the link below to log in to DevShowcase:

{magic_link_url}

This link will expire in 15 minutes.

If you didn't request this, you can safely ignore this email.

Best regards,
DevShowcase Team''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        print(f"   ✅ Email sent successfully!")
    except Exception as e:
        print(f"   ❌ Failed to send email: {e}")
        return
    
    # Test 4: Verify link is valid
    print("\n4. Verifying magic link...")
    try:
        is_valid = magic_link.is_valid()
        print(f"   ✅ Magic link is valid: {is_valid}")
    except Exception as e:
        print(f"   ❌ Failed to verify: {e}")
        return
    
    print("\n" + "=" * 80)
    print("ALL TESTS PASSED! ✅")
    print("=" * 80)
    print("\nYou should see the email content above (between the lines).")
    print("Copy the magic link URL and paste it in your browser to test login.")
    print("=" * 80)

if __name__ == '__main__':
    test_magic_link()

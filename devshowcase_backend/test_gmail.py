#!/usr/bin/env python
"""
Quick test script to verify Gmail SMTP is working
Run this with: python test_gmail.py
"""

import os
import django
from dotenv import load_dotenv

# Load .env file
load_dotenv('.env')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_gmail():
    print("=" * 80)
    print("TESTING GMAIL SMTP CONFIGURATION")
    print("=" * 80)
    
    # Check configuration
    print("\n📋 Current Configuration:")
    print(f"   EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    
    if 'smtp' in settings.EMAIL_BACKEND:
        print(f"   EMAIL_HOST: {settings.EMAIL_HOST}")
        print(f"   EMAIL_PORT: {settings.EMAIL_PORT}")
        print(f"   EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        print(f"   EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        print(f"   EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")
        
        if not settings.EMAIL_HOST_PASSWORD:
            print("\n❌ ERROR: EMAIL_HOST_PASSWORD is not set!")
            print("   Please follow GMAIL_MAGIC_LINK_SETUP.md to configure Gmail")
            return
    else:
        print("   ℹ️  Using console backend (emails print to terminal)")
    
    # Send test email
    print("\n📧 Sending test email...")
    
    test_email = settings.EMAIL_HOST_USER if 'smtp' in settings.EMAIL_BACKEND else 'test@example.com'
    
    try:
        send_mail(
            subject='✅ DevShowcase Gmail Test - Success!',
            message='''Hi there!

This is a test email from your DevShowcase application.

If you're seeing this in your Gmail inbox, congratulations! 🎉
Your Gmail SMTP configuration is working perfectly.

You can now send magic link emails to real email addresses.

Best regards,
DevShowcase Team

---
This is an automated test email. You can safely delete it.''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[test_email],
            fail_silently=False,
        )
        
        if 'smtp' in settings.EMAIL_BACKEND:
            print(f"   ✅ Test email sent successfully to {test_email}!")
            print(f"   📬 Check your inbox at {test_email}")
            print("   ⏱️  It might take 5-10 seconds to arrive")
        else:
            print("   ✅ Email printed to console (see above)")
        
    except Exception as e:
        print(f"   ❌ Failed to send email: {e}")
        print("\n🔍 Troubleshooting:")
        print("   1. Check your app password is correct in .env file")
        print("   2. Make sure 2FA is enabled on your Google account")
        print("   3. Try generating a new app password")
        print("   4. Remove any spaces from the app password")
        return
    
    print("\n" + "=" * 80)
    print("TEST COMPLETED SUCCESSFULLY! ✅")
    print("=" * 80)
    
    if 'smtp' in settings.EMAIL_BACKEND:
        print("\n🎉 Gmail SMTP is configured and working!")
        print("   You can now send magic links to real email addresses.")
        print("\n📝 Next steps:")
        print("   1. Go to http://localhost:5173/login")
        print("   2. Enter any email address")
        print("   3. Check that email's inbox for the magic link")
        print("   4. Click the link to log in")
    else:
        print("\n📝 To enable Gmail SMTP:")
        print("   Follow the guide in GMAIL_MAGIC_LINK_SETUP.md")
    
    print("=" * 80)

if __name__ == '__main__':
    test_gmail()

# ✨ Magic Link Authentication - Setup Guide

## 🎉 What's Been Implemented

Magic Link authentication is now fully integrated into your DevShowcase project!

### Features:
- ✅ Passwordless login via email
- ✅ Secure token generation (expires in 15 minutes)
- ✅ Auto-create users on first login
- ✅ Beautiful animated UI
- ✅ Email verification flow
- ✅ Fallback to traditional login

---

## 🚀 How to Use (Development)

### 1. Start Backend Server
```bash
cd devshowcase_backend
python manage.py runserver
```

### 2. Start Frontend Server
```bash
cd devshowcase_frontend
npm run dev
```

### 3. Test Magic Link

**Option A: Console Email (Current Setup)**
1. Go to: http://localhost:5173/magic-link
2. Enter your email: `test@example.com`
3. Click "Send Magic Link"
4. Check your **terminal/console** where Django is running
5. Copy the magic link URL from the console output
6. Paste it in your browser
7. You're logged in! ✅

**Example Console Output:**
```
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Subject: =?utf-8?q?=F0=9F=94=90_Your_DevShowcase_Login_Link?=
From: DevShowcase <noreply@devshowcase.com>
To: test@example.com
Date: Mon, 15 Jan 2024 10:30:00 -0000
Message-ID: <...>

Hi there!

Click the link below to log in to DevShowcase:

http://localhost:5173/auth/verify/abc123xyz...

This link will expire in 15 minutes.
```

---

## 📧 Setup Real Email (Production)

### Using Gmail (Free):

1. **Enable 2-Factor Authentication** on your Gmail account

2. **Generate App Password**:
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Name it "DevShowcase"
   - Copy the 16-character password

3. **Update `devshowcase_backend/config/settings.py`**:
```python
# Replace this:
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# With this:
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'  # Your Gmail
EMAIL_HOST_PASSWORD = 'your-app-password'  # 16-char password from step 2
DEFAULT_FROM_EMAIL = 'DevShowcase <your-email@gmail.com>'
```

4. **Test it**:
   - Go to http://localhost:5173/magic-link
   - Enter your real email
   - Check your inbox!

---

## 🎨 User Flow

### New User Registration (Magic Link):
```
1. User visits: /magic-link
2. Enters email: alice@example.com
3. Clicks "Send Magic Link"
4. Receives email with link
5. Clicks link → Auto-creates account
6. Logged in! ✅
```

### Existing User Login:
```
1. User visits: /magic-link
2. Enters email: bob@example.com
3. Clicks "Send Magic Link"
4. Receives email with link
5. Clicks link → Logs in
6. Redirected to dashboard ✅
```

---

## 🔒 Security Features

- ✅ **Secure Tokens**: 32-byte URL-safe random tokens
- ✅ **Expiration**: Links expire after 15 minutes
- ✅ **One-Time Use**: Each link can only be used once
- ✅ **Auto-Cleanup**: Old unused links are deleted
- ✅ **No Password Storage**: More secure than passwords!

---

## 🎯 API Endpoints

### Request Magic Link
```http
POST /api/auth/magic-link/request/
Content-Type: application/json

{
  "email": "user@example.com"
}

Response:
{
  "message": "Magic link sent! Check your email.",
  "email": "user@example.com"
}
```

### Verify Magic Link
```http
POST /api/auth/magic-link/verify/
Content-Type: application/json

{
  "token": "abc123xyz..."
}

Response:
{
  "token": "django-token-here",
  "user": {
    "id": 1,
    "username": "user",
    "email": "user@example.com"
  },
  "message": "Successfully logged in!"
}
```

---

## 🎓 Demo Tips for Professor

### Impressive Points to Highlight:

1. **Modern Authentication**: "This uses passwordless authentication, the same technology used by Slack and Notion"

2. **Security**: "Magic links are more secure than passwords - they expire in 15 minutes and can only be used once"

3. **User Experience**: "Users don't need to remember passwords, reducing friction and improving security"

4. **Auto-Registration**: "New users are automatically created on first login - no separate registration needed"

5. **Fallback Option**: "Traditional password login is still available for users who prefer it"

---

## 🐛 Troubleshooting

### Email not sending?
- Check Django console for errors
- Verify EMAIL_BACKEND setting
- For Gmail: Ensure App Password is correct

### Link expired?
- Links expire after 15 minutes
- Request a new link from /magic-link

### Token invalid?
- Each link can only be used once
- Request a new link if needed

---

## 📱 Frontend Routes

- `/magic-link` - Request magic link page
- `/auth/verify/:token` - Verification page (auto-redirects)
- `/login` - Traditional login (with magic link button)
- `/register` - Traditional registration

---

## 🎨 Customization

### Change Link Expiration:
In `devshowcase_backend/accounts/models.py`:
```python
# Change from 15 minutes to 30 minutes:
expires_at = timezone.now() + timedelta(minutes=30)
```

### Customize Email Template:
In `devshowcase_backend/accounts/views.py`, edit the `send_mail()` message.

### Change Frontend URL:
In `devshowcase_backend/config/settings.py`:
```python
FRONTEND_URL = 'https://your-domain.com'
```

---

## ✅ Testing Checklist

- [ ] Request magic link with valid email
- [ ] Check console/email for link
- [ ] Click link and verify login
- [ ] Try expired link (wait 15+ minutes)
- [ ] Try used link (click same link twice)
- [ ] Test with new user (auto-registration)
- [ ] Test with existing user (login)
- [ ] Test fallback to password login

---

## 🚀 Next Steps

1. **Test in development** (console email)
2. **Setup Gmail** for real emails
3. **Deploy to production** with environment variables
4. **Show to professor** and impress! 🎓

---

**Congratulations!** Your project now has modern, secure, passwordless authentication! ✨

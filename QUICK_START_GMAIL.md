# ⚡ Quick Start - Gmail Magic Link (5 Minutes)

## 🎯 Goal
Get Gmail magic links working in 5 minutes!

---

## 📝 Step-by-Step

### 1️⃣ Get Gmail App Password (2 min)

```
1. Go to: https://myaccount.google.com/apppasswords
2. Sign in if needed
3. Select app: "Mail"
4. Select device: "Other" → Type "DevShowcase"
5. Click "Generate"
6. Copy the 16-character password (remove spaces)
   Example: abcdefghijklmnop
```

### 2️⃣ Add to .env File (1 min)

```bash
# Open this file:
devshowcase_backend/.env

# Find this line:
EMAIL_HOST_PASSWORD=your-app-password-here

# Replace with your actual password:
EMAIL_HOST_PASSWORD=abcdefghijklmnop

# Save the file
```

### 3️⃣ Install Dependencies (1 min)

```bash
cd devshowcase_backend
pip install python-dotenv
```

### 4️⃣ Restart Server (30 sec)

```bash
# Stop Django (Ctrl+C)
python manage.py runserver

# Look for this message:
# 📧 Email configured: Gmail SMTP (amey020607@gmail.com)
```

### 5️⃣ Test It! (30 sec)

```bash
python test_gmail.py
```

Check your Gmail inbox for test email!

---

## ✅ Verification

You should see:
- ✅ "📧 Email configured: Gmail SMTP" when server starts
- ✅ Test email in your Gmail inbox
- ✅ No errors in terminal

---

## 🎬 Try the Full Flow

1. Go to: http://localhost:5173/login
2. Enter: amey020607@gmail.com
3. Click: "✨ Send Magic Link"
4. Check Gmail inbox (5-10 seconds)
5. Click the link in email
6. You're logged in! 🎉

---

## 🐛 Not Working?

### Can't find apppasswords page?
- Make sure 2FA is enabled first
- Try: Google Account → Security → 2-Step Verification → App passwords

### Still seeing "Console" mode?
- Check .env file has EMAIL_HOST_PASSWORD set
- Make sure no spaces in the password
- Restart Django server

### Email not arriving?
- Check spam folder
- Wait 30 seconds
- Run: `python test_gmail.py` to see errors

---

## 📚 More Help

- **Full Guide**: GMAIL_MAGIC_LINK_SETUP.md
- **Demo Script**: DEMO_MAGIC_LINK.md
- **Summary**: MAGIC_LINK_SUMMARY.md

---

That's it! You're ready to impress your professor! 🚀

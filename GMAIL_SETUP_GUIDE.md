# Gmail SMTP Setup Guide for Magic Link

## Step 1: Enable 2-Factor Authentication (if not already enabled)

1. Go to your Google Account: https://myaccount.google.com/
2. Click on "Security" in the left sidebar
3. Under "How you sign in to Google", click on "2-Step Verification"
4. Follow the steps to enable 2FA if it's not already enabled

## Step 2: Generate App Password

1. Go to: https://myaccount.google.com/apppasswords
   - OR: Google Account → Security → 2-Step Verification → App passwords (at the bottom)

2. You might need to sign in again

3. In the "Select app" dropdown, choose "Mail"

4. In the "Select device" dropdown, choose "Other (Custom name)"

5. Type: "DevShowcase Magic Link"

6. Click "Generate"

7. Google will show you a 16-character password like: `abcd efgh ijkl mnop`

8. **IMPORTANT**: Copy this password immediately! You won't be able to see it again.

## Step 3: Add to Environment Variables

I'll create a `.env` file in your backend folder. You'll need to paste your app password there.

## Step 4: Test

Once configured, try sending a magic link and check your actual Gmail inbox!

---

## Troubleshooting

### "Username and Password not accepted"
- Make sure you're using the App Password, not your regular Gmail password
- Make sure 2FA is enabled on your Google account
- Remove any spaces from the app password

### "SMTPAuthenticationError"
- Double-check the app password is correct
- Try generating a new app password

### Emails going to Spam
- Check your spam folder
- Mark the email as "Not Spam"
- For production, you'd want to set up SPF/DKIM records

---

## Security Note

Never commit your app password to Git! The `.env` file should be in `.gitignore`.

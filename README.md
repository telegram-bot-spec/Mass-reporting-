# Telegram Channel Reporter Bot

Automated Telegram userbot for reporting channels.

## Features
- 📋 Single & Bulk reporting
- ⚡ Quick reply commands
- 📊 Statistics tracking
- 🔐 Admin-only access
- ☁️ Cloud deployment ready

## Setup

### 1. Get API Credentials
1. Go to https://my.telegram.org
2. Login and create an app
3. Note down API_ID and API_HASH

### 2. Generate Session (Run Locally)
```bash
pip install telethon
python generate_session.py
Save the SESSION_STRING output!
3. Deploy to Railway
Fork this repo
Connect to Railway
Add environment variables:
API_ID
API_HASH
PHONE_NUMBER
SESSION_STRING
ADMIN_IDS (your user ID)
4. Get Your User ID
Message @userinfobot on Telegram
Commands
/start - Show menu
/report @channel spam - Report single
/bulk spam - Start bulk mode
/stats - View statistics
/spam - Quick report (reply)
Available Reasons
spam, violence, porn, child, copyright, fake, drugs, other
Usage
/report @scamchannel spam
/bulk fake
@channel1
@channel2
@channel3
⚠️ Important
Max 50 reports/day per account
Use 7-10 second delays
Admin-only commands
Keep session secure
Support
Open an issue for help
---

## **🚀 Deployment Steps:**

### **Step 1: Generate Session (LOCALLY)**
```bash
pip install telethon
python generate_session.py
Save the SESSION_STRING!
Step 2: Upload to GitHub
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/telegram-reporter.git
git push -u origin main
Step 3: Deploy to Railway
Go to Railway.app
Click "New Project" → "Deploy from GitHub"
Select your repo
Add Environment Variables:
API_ID = 12345678
API_HASH = your_hash
PHONE_NUMBER = +1234567890
SESSION_STRING = (from generate_session.py)
ADMIN_IDS = your_user_id
Click Deploy!
Step 4: Get Your User ID
Message @userinfobot on Telegram
Add your ID to ADMIN_IDS in Railway

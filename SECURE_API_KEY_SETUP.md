# 🔒 SECURE API KEY SETUP GUIDE

## ⚠️ IMMEDIATE ACTION REQUIRED

Your API key has been **EXPOSED** in the conversation thread.

### Step 1: Revoke the Exposed Key (DO THIS NOW!)
1. Visit: https://platform.openai.com/api-keys
2. Find the key that was exposed in the chat (scroll down to find it)
3. Click the trash/delete icon
4. Confirm deletion

### Step 2: Generate a New API Key
1. On the same page, click "+ Create new secret key"
2. Copy the new key immediately (you can't see it again)
3. Do NOT close the window until you've saved it

### Step 3: Add New Key to .env Locally
```bash
# Edit the .env file in your project root
nano /Users/niharshah/Desktop/Meta\ Hackathon/.env
```

Replace:
```
HF_TOKEN=your-api-key-here
```

With your new key:
```
HF_TOKEN=sk-proj-YOUR-NEW-KEY-HERE
```

### Step 4: Test the Setup
```bash
cd "/Users/niharshah/Desktop/Meta Hackathon"
export $(cat .env | xargs)
python inference.py
```

## ✅ Security Checklist

- ✅ `.env` file exists and is in `.gitignore`
- ✅ API key was NOT committed to git (verified)
- ✅ `.env.local` is also in `.gitignore` (extra safety)
- ✅ `inference.py` reads from environment variables only
- ✅ Old API key should be revoked immediately

## 🚀 How to Use Your API Key Securely

### Option 1: Load from .env file (RECOMMENDED)
```bash
# Automatic loading with python-dotenv
pip install python-dotenv

# In your Python script:
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("HF_TOKEN")
```

### Option 2: Set environment variable directly
```bash
export HF_TOKEN="sk-proj-your-new-key"
python inference.py
```

### Option 3: Pass via command line (NOT RECOMMENDED)
```bash
# Only for testing - never do this in production
HF_TOKEN="sk-proj-your-key" python inference.py
```

## ⚠️ NEVER Do This

- ❌ Don't commit `.env` to git
- ❌ Don't share your API key in messages/chat
- ❌ Don't put it in code as a string literal
- ❌ Don't post it in logs or error messages
- ❌ Don't use the same key across multiple projects

## 📋 Current Setup Status

| Item | Status |
|------|--------|
| `.env` file exists | ✅ |
| `.env` in `.gitignore` | ✅ |
| API key in git history | ❌ None found |
| `.gitignore` covers `.env` | ✅ |
| `.gitignore` covers `.env.local` | ✅ |

---

**Your exposed key should be revoked immediately!**
**Generate a new key and update your `.env` file.**
**Then you're ready to run `python inference.py`**

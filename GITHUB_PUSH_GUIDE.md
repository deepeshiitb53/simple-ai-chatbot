# 🔐 How to Push Code to GitHub

You need authentication to push code. Here are your options:

## Option 1: Add SSH Key to GitHub (Recommended - One-time setup)

### Step 1: Copy Your SSH Public Key
Your SSH public key is shown above. Copy the entire key (starts with `ssh-rsa` and ends with your email).

### Step 2: Add to GitHub
1. Go to: https://github.com/settings/keys
2. Click **"New SSH key"**
3. Give it a title (e.g., "My Mac")
4. Paste your public key
5. Click **"Add SSH key"**

### Step 3: Push Code
```bash
git push origin main
```

---

## Option 2: Use Personal Access Token (HTTPS)

### Step 1: Create Token
1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Give it a name: "Streamlit Deployment"
4. Select scopes: ✅ **repo** (full control)
5. Click **"Generate token"**
6. **COPY THE TOKEN** (you won't see it again!)

### Step 2: Update Remote to HTTPS
```bash
git remote set-url origin https://github.com/deepeshiitb53/simple-ai-chatbot.git
```

### Step 3: Push with Token
```bash
git push origin main
```
When prompted:
- Username: `deepeshiitb53`
- Password: **Paste your token** (not your GitHub password)

---

## Option 3: Use GitHub Desktop (Easiest)

1. Download: https://desktop.github.com/
2. Sign in with your GitHub account
3. Open your repository
4. Click "Push origin" button

---

## Quick Test

After setting up, test with:
```bash
git push origin main
```

If successful, you'll see your commits pushed to GitHub!

---

## What You Need Summary

**For SSH:**
- ✅ SSH key exists on your computer
- ❌ Need to add it to GitHub account

**For HTTPS:**
- ✅ GitHub account exists
- ❌ Need to create Personal Access Token

**For GitHub Desktop:**
- ✅ Just need GitHub account
- ✅ Desktop app handles authentication


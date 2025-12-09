# 🚀 Streamlit Cloud Deployment - Step by Step

Your code is committed locally! Follow these steps to deploy:

## Step 1: Push to GitHub

You have two options:

### Option A: Fix Authentication & Push
```bash
# Update your remote URL (if needed)
git remote set-url origin https://github.com/deepeshiitb53/simple-ai-chatbot.git

# Push using GitHub CLI (if installed)
gh auth login
git push origin main

# OR push manually after fixing credentials
git push origin main
```

### Option B: Push via GitHub Website
1. Go to: https://github.com/deepeshiitb53/simple-ai-chatbot
2. Click "Upload files" or use GitHub Desktop
3. Upload all your files (except `.env`)

---

## Step 2: Deploy on Streamlit Cloud

1. **Go to Streamlit Cloud**
   - Visit: https://share.streamlit.io/
   - Sign in with your GitHub account

2. **Create New App**
   - Click **"New app"** button
   - Select repository: `deepeshiitb53/simple-ai-chatbot`
   - Branch: `main`
   - Main file path: `app.py`
   - Click **"Deploy"**

3. **Wait for Deployment**
   - Streamlit will install dependencies and start your app
   - This takes 1-2 minutes

---

## Step 3: Add Secrets (API Keys)

1. **Go to App Settings**
   - In your app dashboard, click **"Settings"** (⚙️ icon)
   - Click **"Secrets"** tab

2. **Add Your API Keys**
   - Click **"Edit"** or **"New secret"**
   - Add this format:
     ```toml
     OPENAI_API_KEY = "sk-your-actual-openai-key-here"
     ELEVENLABS_API_KEY = "your-elevenlabs-key-here"
     ```
   - Click **"Save"**

3. **App Will Redeploy**
   - Streamlit automatically redeploys when you save secrets
   - Wait for deployment to complete

---

## Step 4: Share Your App! 🎉

Your app will be live at:
```
https://simple-ai-chatbot.streamlit.app
```
(Or similar URL - check your dashboard)

**Share this URL with your friends!**

---

## Troubleshooting

### App won't start?
- Check the logs in Streamlit Cloud dashboard
- Verify `requirements.txt` has all dependencies
- Make sure `app.py` is the main file

### API errors?
- Double-check secrets are set correctly
- Verify API keys are valid
- Check usage limits on OpenAI account

### Need help?
- Streamlit Cloud docs: https://docs.streamlit.io/streamlit-community-cloud
- Check deployment logs in dashboard

---

## Quick Checklist

- [ ] Code pushed to GitHub
- [ ] App deployed on Streamlit Cloud
- [ ] Secrets added (OPENAI_API_KEY)
- [ ] App is running successfully
- [ ] Shared URL with friends!


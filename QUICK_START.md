# 🚀 Quick Start Guide - Share Your App

## Fastest Way to Share (3 Steps)

### 1️⃣ Push to GitHub
```bash
git add .
git commit -m "Ready to share"
git push
```

### 2️⃣ Deploy on Streamlit Cloud
- Go to [share.streamlit.io](https://share.streamlit.io/)
- Click "New app"
- Select your repo → Deploy

### 3️⃣ Add Secrets
In Streamlit Cloud dashboard → Settings → Secrets:
```toml
OPENAI_API_KEY = "sk-your-key-here"
ELEVENLABS_API_KEY = "your-key-here"  # Optional
```

**Done!** Share your URL: `https://YOUR_APP.streamlit.app`

---

## Share on Same WiFi (Even Faster!)

```bash
# Run this command
streamlit run app.py --server.address 0.0.0.0

# Find your IP address
# Mac/Linux: ifconfig | grep "inet "
# Windows: ipconfig

# Share: http://YOUR_IP:8501
```

---

## Need More Help?

- 📖 Full guide: [DEPLOYMENT.md](DEPLOYMENT.md)
- 🛠️ Helper script: Run `./deploy.sh` (Mac/Linux) or `deploy.bat` (Windows)

---

## ⚠️ Important Notes

- ✅ Never commit `.env` file (it's in `.gitignore`)
- ✅ Use Streamlit Secrets for cloud deployments
- ✅ Set usage limits on OpenAI to avoid surprises
- ✅ Test locally before deploying


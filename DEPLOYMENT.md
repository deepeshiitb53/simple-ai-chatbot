# Deployment Guide - Sharing Your Chatbot App

This guide covers multiple ways to share your chatbot app with friends and the world.

## 🚀 Option 1: Streamlit Community Cloud (Recommended - Free & Easy)

**Best for**: Sharing with friends and public access

### Steps:

1. **Prepare Your Repository**
   ```bash
   # Make sure your code is ready
   git add .
   git commit -m "Ready for deployment"
   ```

2. **Push to GitHub**
   - Create a new repository on [GitHub](https://github.com/new)
   - Push your code:
     ```bash
     git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
     git push -u origin main
     ```
   - ⚠️ **Important**: Make sure `.env` is in `.gitignore` (it should be already)

3. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io/)
   - Sign in with your GitHub account
   - Click **"New app"**
   - Select your repository and branch
   - Set **Main file path**: `app.py`
   - Click **"Deploy"**

4. **Configure Secrets**
   - Once deployed, go to your app's **Settings** → **Secrets**
   - Add your API keys:
     ```toml
     OPENAI_API_KEY = "sk-your-openai-key-here"
     ELEVENLABS_API_KEY = "your-elevenlabs-key-here"
     ```
   - Click **"Save"** - your app will automatically redeploy

5. **Share Your App**
   - Your app will be live at: `https://YOUR_APP_NAME.streamlit.app`
   - Share this URL with your friends!

### Notes:
- ✅ Free forever
- ✅ Automatic HTTPS
- ✅ Auto-deploys on git push
- ⚠️ Advanced streaming (WebSocket) won't work on Streamlit Cloud (use regular TTS mode)

---

## 🌐 Option 2: Local Network Sharing (Quick Testing)

**Best for**: Sharing with friends on the same WiFi network

### Steps:

1. **Find Your Local IP Address**
   - **Mac/Linux**: Run `ifconfig | grep "inet "` or `ip addr show`
   - **Windows**: Run `ipconfig` and look for IPv4 Address
   - Example: `192.168.1.100`

2. **Run Streamlit with Network Access**
   ```bash
   streamlit run app.py --server.address 0.0.0.0 --server.port 8501
   ```

3. **Share the URL**
   - Your friends can access: `http://YOUR_IP:8501`
   - Example: `http://192.168.1.100:8501`

4. **For Advanced Streaming (Optional)**
   - Start the realtime bridge in another terminal:
     ```bash
     uvicorn realtime_bridge:app --host 0.0.0.0 --port 8001
     ```
   - Update `app.py` line 249 to use your IP instead of `localhost`:
     ```python
     const ws = new WebSocket("ws://YOUR_IP:8001/ws/audio/" + sessionId);
     ```

### Notes:
- ✅ Works immediately
- ✅ Supports all features including advanced streaming
- ⚠️ Only works on same network
- ⚠️ Your computer must stay on

---

## ☁️ Option 3: Railway (Paid, More Control)

**Best for**: Production apps with custom domains

1. **Sign up** at [railway.app](https://railway.app)
2. **Create new project** → **Deploy from GitHub**
3. **Add environment variables**:
   - `OPENAI_API_KEY`
   - `ELEVENLABS_API_KEY` (optional)
4. **Set start command**: `streamlit run app.py --server.port $PORT`
5. **Deploy!**

---

## 🐳 Option 4: Docker (Advanced)

**Best for**: Self-hosting on VPS or cloud

1. **Create `Dockerfile`**:
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 8501
   CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```

2. **Build and run**:
   ```bash
   docker build -t chatbot .
   docker run -p 8501:8501 -e OPENAI_API_KEY=your-key chatbot
   ```

---

## 📋 Pre-Deployment Checklist

- [ ] `.env` file is in `.gitignore`
- [ ] `requirements.txt` is up to date
- [ ] Code is pushed to GitHub
- [ ] API keys are ready (OpenAI required, ElevenLabs optional)
- [ ] Tested locally first

---

## 🔒 Security Best Practices

1. **Never commit API keys** - Always use environment variables or secrets
2. **Use Streamlit Secrets** for cloud deployments
3. **Set usage limits** on your OpenAI account to prevent unexpected charges
4. **Consider adding authentication** if sharing publicly (Streamlit has built-in options)

---

## 🆘 Troubleshooting

### App won't start
- Check that all dependencies are in `requirements.txt`
- Verify API keys are set correctly
- Check Streamlit Cloud logs in the dashboard

### TTS not working
- Verify ElevenLabs API key is set
- Check browser console for errors
- Try disabling advanced streaming if on cloud

### Friends can't access
- For local network: Check firewall settings
- For cloud: Verify deployment completed successfully
- Check the app URL is correct

---

## 💡 Quick Start Commands

```bash
# Local development
streamlit run app.py

# Local network sharing
streamlit run app.py --server.address 0.0.0.0

# With advanced streaming
uvicorn realtime_bridge:app --host 0.0.0.0 --port 8001
```


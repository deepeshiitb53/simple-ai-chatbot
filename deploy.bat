@echo off
REM Quick deployment helper script for Windows
REM This script helps you prepare and share your chatbot app

echo 🤖 Simple Chatbot - Deployment Helper
echo ======================================
echo.

REM Check if .env exists
if not exist .env (
    echo ⚠️  Warning: .env file not found!
    echo    Creating from .env.example...
    if exist .env.example (
        copy .env.example .env
        echo    ✅ Created .env file
        echo    📝 Please edit .env and add your API keys
    ) else (
        echo    ❌ .env.example not found either
        echo    Please create .env manually with your API keys
    )
)

echo.
echo Select deployment method:
echo 1) Run locally (localhost)
echo 2) Share on local network (same WiFi)
echo 3) Show deployment instructions
echo.
set /p choice="Enter choice (1-3): "

if "%choice%"=="1" (
    echo.
    echo 🚀 Starting app locally...
    streamlit run app.py
) else if "%choice%"=="2" (
    echo.
    echo 🌐 Starting app on local network...
    echo    Friends can access via: http://YOUR_IP:8501
    echo.
    set /p bridge="Start advanced streaming bridge? (y/n): "
    if "%bridge%"=="y" (
        echo    Starting bridge in background...
        start /B uvicorn realtime_bridge:app --host 0.0.0.0 --port 8001
    )
    streamlit run app.py --server.address 0.0.0.0 --server.port 8501
) else if "%choice%"=="3" (
    echo.
    echo 📖 Deployment Instructions:
    echo.
    echo For Streamlit Cloud (Recommended):
    echo 1. Push code to GitHub (make sure .env is NOT committed)
    echo 2. Go to https://share.streamlit.io
    echo 3. Deploy your repository
    echo 4. Add secrets in Settings → Secrets
    echo.
    echo See DEPLOYMENT.md for detailed instructions!
) else (
    echo Invalid choice
)

pause


#!/bin/bash

# Quick deployment helper script
# This script helps you prepare and share your chatbot app

echo "🤖 Simple Chatbot - Deployment Helper"
echo "======================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "   Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "   ✅ Created .env file"
        echo "   📝 Please edit .env and add your API keys"
    else
        echo "   ❌ .env.example not found either"
        echo "   Please create .env manually with your API keys"
    fi
fi

echo ""
echo "Select deployment method:"
echo "1) Run locally (localhost)"
echo "2) Share on local network (same WiFi)"
echo "3) Show deployment instructions"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Starting app locally..."
        streamlit run app.py
        ;;
    2)
        echo ""
        echo "🌐 Starting app on local network..."
        echo "   Friends can access via: http://YOUR_IP:8501"
        echo ""
        read -p "Start advanced streaming bridge? (y/n): " bridge
        if [ "$bridge" = "y" ]; then
            echo "   Starting bridge in background..."
            uvicorn realtime_bridge:app --host 0.0.0.0 --port 8001 &
            BRIDGE_PID=$!
            echo "   Bridge PID: $BRIDGE_PID"
        fi
        streamlit run app.py --server.address 0.0.0.0 --server.port 8501
        if [ "$bridge" = "y" ]; then
            kill $BRIDGE_PID 2>/dev/null
        fi
        ;;
    3)
        echo ""
        echo "📖 Deployment Instructions:"
        echo ""
        echo "For Streamlit Cloud (Recommended):"
        echo "1. Push code to GitHub (make sure .env is NOT committed)"
        echo "2. Go to https://share.streamlit.io"
        echo "3. Deploy your repository"
        echo "4. Add secrets in Settings → Secrets"
        echo ""
        echo "See DEPLOYMENT.md for detailed instructions!"
        ;;
    *)
        echo "Invalid choice"
        ;;
esac


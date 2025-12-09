# Simple AI Chatbot

A simple, ChatGPT-like AI chatbot built using Python, Streamlit, and the OpenAI API.

## Features

-   **Interactive Chat Interface**: Clean and simple UI powered by Streamlit.
-   **Real-time Streaming**: Responses are streamed in real-time, just like ChatGPT.
-   **Conversation History**: Maintains context of the conversation within the session.

## How Context Works

The chatbot "remembers" your conversation by sending the entire chat history to the OpenAI API with every new message.

1.  **Session State**: Streamlit's `st.session_state` stores a list of all messages (user inputs and AI responses) in the current browser tab.
2.  **Full History Transmission**: When you send a new prompt, the app sends the *entire* list of previous messages along with your new one.
3.  **Contextual Responses**: This allows the AI to understand references to previous topics (e.g., if you say "Explain it further", it knows what "it" refers to).

## Prerequisites

-   Python 3.7 or higher
-   An OpenAI API Key (You can get one from [OpenAI Platform](https://platform.openai.com/))

## Setup & Installation

1.  **Clone the repository** (if applicable) or navigate to the project directory.

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment Variables**:
    -   Rename `.env.example` to `.env`:
        ```bash
        mv .env.example .env
        # On Windows (Command Prompt): ren .env.example .env
        ```
    -   Open the `.env` file and replace `your_openai_api_key_here` with your actual OpenAI API key.

## Running the Application

Run the Streamlit app with the following command:

```bash
streamlit run app.py
```

The application will open in your default web browser (usually at `http://localhost:8501`).

## Usage

1.  Enter your message in the input box at the bottom of the screen.
2.  Press Enter to send.
3.  Watch the AI respond in real-time!

## 🚀 Sharing Your App with Friends

Want to share your chatbot? 

- ⚡ **Quick start**: See [QUICK_START.md](QUICK_START.md) for the fastest way
- 📖 **Full guide**: See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions
- 🛠️ **Helper scripts**: Use `./deploy.sh` (Mac/Linux) or `deploy.bat` (Windows)

### Quick Options:

1. **🌐 Streamlit Cloud (Recommended)** - Free, easy, public URL
   - Push to GitHub → Deploy on [share.streamlit.io](https://share.streamlit.io/)
   - Add secrets in dashboard → Share URL with friends!

2. **🏠 Local Network** - Share on same WiFi
   ```bash
   streamlit run app.py --server.address 0.0.0.0
   ```
   Then share: `http://YOUR_IP:8501`

3. **☁️ Other Platforms** - Railway, Render, Docker, etc.
   - See [DEPLOYMENT.md](DEPLOYMENT.md) for full guide

### Quick Deploy Steps (Streamlit Cloud):

1. **Push to GitHub** (make sure `.env` is NOT committed)
2. **Go to** [share.streamlit.io](https://share.streamlit.io/)
3. **Deploy** your repository
4. **Add secrets**:
   ```toml
   OPENAI_API_KEY = "sk-..."
   ELEVENLABS_API_KEY = "..."  # Optional
   ```
5. **Share** your app URL!
## TTS Integration (New!)

- **Ultra-low latency TTS**: Uses ElevenLabs API with Flash models for near real-time speech playback.
- **Experiment Voices**: Dynamic list from ElevenLabs, prioritizes Indian English accents automatically.
- **Real-time Feel**: Audio starts immediately after AI text response completes (~200ms TTS latency).
- **Usage**: Toggle TTS on in sidebar, enter API key, select voice & model. Audio auto-plays with controls.

### TTS Setup
1. Create account at [elevenlabs.io](https://elevenlabs.io/app/settings/api-keys)
2. Copy your API key
3. Paste into sidebar "ElevenLabs API Key" field
4. Choose voice (Indian prioritized) and model (e.g., eleven_flash_2_5 for speed)

**Note**: Browser autoplay policies may require clicking play first. For true streaming sync, future enhancement possible.
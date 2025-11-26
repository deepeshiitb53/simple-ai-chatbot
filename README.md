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

## Deployment (Share Your App)

The easiest way to share your app with the world is using **Streamlit Community Cloud**.

1.  **Push to GitHub**:
    -   Create a GitHub repository.
    -   Push your code (`app.py`, `requirements.txt`) to the repository.
    -   *Note: Do NOT push your `.env` file containing your API key.*

2.  **Deploy on Streamlit Cloud**:
    -   Go to [share.streamlit.io](https://share.streamlit.io/).
    -   Log in with GitHub.
    -   Click "New app" and select your repository.
    -   Click "Deploy".

3.  **Add Secrets (API Key)**:
    -   Once deployed, go to your app's dashboard.
    -   Click "Settings" -> "Secrets".
    -   Add your API key like this:
        ```toml
        OPENAI_API_KEY = "sk-..."
        ```
    -   Save, and your app is live!
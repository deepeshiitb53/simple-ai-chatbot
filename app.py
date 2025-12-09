import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
import os
import base64
import requests
import time
import uuid
import threading
import asyncio
import json
import queue
import websockets
from typing import Optional
from elevenlabs.client import ElevenLabs

from dotenv import load_dotenv
load_dotenv()

# Detect local development
LOCAL_DEV = os.getenv("LOCAL_DEV", "false").lower() == "true"

# Set page configuration
st.set_page_config(page_title="Simple AI Chatbot", page_icon="🤖")

st.title("🤖 Simple AI Chatbot")

# Sidebar settings
with st.sidebar:
    st.header("Settings")
    model_name = st.selectbox(
        "Select Model",
        ["gpt-4o", "gpt-4o-mini", "gpt-4.1", "gpt-5.1", "gpt-5-mini"],
        index=1
    )
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=1.0,
        step=0.1,
        help="Higher values make the output more random, lower values make it more focused."
    )
    
    system_prompt = st.text_area(
        "System Prompt (Roleplay)",
        value="You are Riva, You are a fun and witty conversation partner. Use very simple English that even a pre-beginner can understand — short sentences, common words, no hard grammar. Make the tone playful and friendly, adding light jokes or funny pictures in words. Keep answers short (2–3 sentences max). if user says something inappropriate then ask user to stick to appropriate topics only. If user talks in hindi or any language other than english then add this in your response \"let's stick to english please\"",
        help="Define the AI's personality or role here."
    )
    
    reasoning_effort = None
    if model_name == "gpt-5.1":
        reasoning_effort = st.selectbox(
            "Reasoning Effort",
            ["none", "low", "medium", "high"],
            index=0,
            help=f"Control the reasoning depth for {model_name}."
        )
    elif model_name == "gpt-5-mini":
        reasoning_effort = st.selectbox(
            "Reasoning Effort",
            ["minimal", "medium", "high"],
            index=0,
            help=f"Control the reasoning depth for {model_name}."
        )

    st.subheader("TTS Settings")
    tts_enabled = st.toggle("Enable TTS", value=True)
    
    # Load ElevenLabs API key from environment (local) or secrets (cloud)
    if LOCAL_DEV:
        default_el_key = os.getenv("ELEVENLABS_API_KEY", "")
    else:
        default_el_key = st.secrets.get("ELEVENLABS_API_KEY", "")
    # Hide ElevenLabs API Key field from UI - use environment/secrets only
    el_api_key = default_el_key
    # TTS model IDs (flash v2.5 for fastest latency, plus turbo/multilingual/monolingual)
    tts_model = st.selectbox(
        "TTS Model",
        ["eleven_flash_v2_5", "eleven_turbo_v2", "eleven_multilingual_v2", "eleven_monolingual_v1", "eleven_v3", "eleven_turbo_v2_5"],
        index=5,
        disabled=not tts_enabled,
    )
    advanced_streaming = st.toggle(
        "Advanced streaming (WebSocket)",
        value=LOCAL_DEV,  # Default to True for local dev, False for cloud
        help="Requires realtime bridge: `uvicorn realtime_bridge:app --port 8001`" if LOCAL_DEV else "Not available in cloud deployment",
        disabled=not tts_enabled or not LOCAL_DEV,  # Disable in cloud
    )
    # Preset voice IDs (user specified)
    PRESET_VOICES = {
        "Indian Voice 1": "kiaJRdXJzloFWi6AtFBf",
        "Indian Voice 2": "zT03pEAEi0VHKciJODfn",
    }
    
    selected_voice_id = None
    if tts_enabled:
        # Option to use preset voice, custom ID, or select from library
        # Default to "Enter custom Voice ID" (index=1)
        voice_source = st.radio(
            "Voice selection",
            ["Use preset voice", "Enter custom Voice ID", "Select from library"],
            index=1,
            horizontal=True,
        )
        
        if voice_source == "Use preset voice":
            preset_name = st.selectbox("Preset Voice", list(PRESET_VOICES.keys()))
            selected_voice_id = PRESET_VOICES[preset_name]
            st.caption(f"Voice ID: {selected_voice_id}")
        elif voice_source == "Enter custom Voice ID":
            custom_voice_id = st.text_input(
                "Voice ID",
                value="kvQSb3naDTi3sgHwwBC1",
                placeholder="Enter ElevenLabs Voice ID (e.g., pNInz6obpgDQGcFmaJgB)",
                help="Find voice IDs at https://elevenlabs.io/app/voice-library",
            )
            if custom_voice_id and custom_voice_id.strip():
                selected_voice_id = custom_voice_id.strip()
                st.caption(f"Using custom voice ID: {selected_voice_id}")
            else:
                st.info("Enter a voice ID to use TTS")
        elif el_api_key:
            try:
                # Fetch voices via HTTP instead of SDK to avoid internal encoding issues
                headers = {
                    "xi-api-key": el_api_key,
                    "Accept": "application/json",
                }
                resp = requests.get(
                    "https://api.elevenlabs.io/v1/voices",
                    headers=headers,
                    timeout=10,
                )
                resp.raise_for_status()
                data = resp.json()
                voices_data = data.get("voices", [])

                # Build a safe ASCII-only label for each voice name to avoid encoding issues
                voice_dict = {}
                for v in voices_data:
                    raw_name = (v.get("name") or "").strip()
                    safe_name = raw_name.encode("ascii", "ignore").decode("ascii").strip()
                    if not safe_name:
                        safe_name = f"Voice {v.get('voice_id', '')[:8]}"
                    voice_dict[safe_name] = v.get("voice_id")

                # Prioritize Indian English voices
                indian_keywords = ['indian', 'hindi', 'delhi', 'mumbai', 'bangalore', 'accent', 'south asian']
                indian_voices = {
                    name: vid
                    for name, vid in voice_dict.items()
                    if any(kw in name.lower() for kw in indian_keywords)
                }
                sorted_voices = dict(
                    sorted(
                        {**indian_voices, **voice_dict}.items(),
                        key=lambda x: (x[0] not in indian_voices, x[0]),
                    )
                )
                selected_name = st.selectbox("Voice (Indian first)", list(sorted_voices.keys()))
                selected_voice_id = sorted_voices[selected_name]
            except Exception as e:
                # Ensure any unicode in the error itself never breaks rendering
                safe_err = str(e)
                try:
                    safe_err = safe_err.encode("utf-8", "ignore").decode("utf-8")
                except Exception:
                    pass
                st.error(f"Failed to fetch voices: {safe_err}")
                st.info("Enter valid API key to load voices.")
        else:
            st.info("Enter API key to select from voice list.")
    else:
        st.info("Enable TTS to configure voice.")
# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.warning("Please set your OPENAI_API_KEY in the .env file to continue.")
    st.stop()

client = OpenAI(api_key=api_key)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        # Prepare messages with system prompt
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(
            [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ]
        )

        # Prepare API arguments
        api_args = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "stream": True,
        }

        # Add reasoning_effort only if applicable
        if reasoning_effort:
            api_args["reasoning_effort"] = reasoning_effort

        # --- Measure first-token latency while streaming text manually ---
        t_request = time.time()
        stream = client.chat.completions.create(**api_args)

        response_placeholder = st.empty()
        response_text = ""
        first_token_latency = None

        # Optional: token-level streaming into ElevenLabs Realtime bridge
        text_ws_queue: Optional[queue.Queue] = None
        session_id = None

        if tts_enabled and selected_voice_id and el_api_key and advanced_streaming:
            session_id = str(uuid.uuid4())

            # Inject JS audio client that connects to the realtime bridge WebSocket
            # Handles PCM 24kHz 16-bit mono audio from ElevenLabs
            audio_player = f"""
            <script>
            (function() {{
                const sessionId = "{session_id}";
                const ws = new WebSocket("ws://localhost:8001/ws/audio/" + sessionId);
                const AudioContext = window.AudioContext || window.webkitAudioContext;
                const audioCtx = new AudioContext({{ sampleRate: 24000 }});
                
                // Queue for audio chunks
                const audioQueue = [];
                let isPlaying = false;
                let nextStartTime = 0;
                
                // PCM format: 24kHz, 16-bit signed, mono
                const SAMPLE_RATE = 24000;
                
                function playNextChunk() {{
                    if (audioQueue.length === 0) {{
                        isPlaying = false;
                        return;
                    }}
                    
                    isPlaying = true;
                    const pcmData = audioQueue.shift();
                    
                    // Convert Int16 PCM to Float32 for Web Audio API
                    const int16Array = new Int16Array(pcmData);
                    const float32Array = new Float32Array(int16Array.length);
                    for (let i = 0; i < int16Array.length; i++) {{
                        float32Array[i] = int16Array[i] / 32768.0;
                    }}
                    
                    // Create audio buffer
                    const audioBuffer = audioCtx.createBuffer(1, float32Array.length, SAMPLE_RATE);
                    audioBuffer.getChannelData(0).set(float32Array);
                    
                    // Create and play source
                    const source = audioCtx.createBufferSource();
                    source.buffer = audioBuffer;
                    source.connect(audioCtx.destination);
                    
                    // Schedule playback
                    const now = audioCtx.currentTime;
                    const startTime = Math.max(now, nextStartTime);
                    source.start(startTime);
                    nextStartTime = startTime + audioBuffer.duration;
                    
                    // Play next chunk when this one ends
                    source.onended = playNextChunk;
                }}

                ws.binaryType = "arraybuffer";
                ws.onmessage = (event) => {{
                    // Resume audio context if suspended (browser autoplay policy)
                    if (audioCtx.state === 'suspended') {{
                        audioCtx.resume();
                    }}
                    
                    // Add to queue
                    audioQueue.push(event.data);
                    
                    // Start playing if not already
                    if (!isPlaying) {{
                        playNextChunk();
                    }}
                }};
                ws.onerror = (err) => console.error("Audio WS error", err);
                ws.onclose = () => console.log("Audio WS closed");
            }})();
            </script>
            """
            components.html(audio_player, height=0, width=0)

            # Local queue used to push text deltas to the bridge worker
            text_ws_queue = queue.Queue()

            def _text_ws_worker() -> None:
                async def _run() -> None:
                    uri = f"ws://localhost:8001/ws/text/{session_id}"
                    try:
                        async with websockets.connect(uri) as ws:
                            # Send config first (output_format is ignored, bridge uses pcm_24000)
                            cfg = {
                                "api_key": el_api_key,
                                "voice_id": selected_voice_id,
                                "model_id": tts_model,
                                "output_format": "pcm_24000",
                            }
                            await ws.send(json.dumps(cfg))

                            loop = asyncio.get_running_loop()
                            while True:
                                # Block in a thread-safe way waiting for next item
                                item = await loop.run_in_executor(None, text_ws_queue.get)
                                if item is None:
                                    break
                                await ws.send(json.dumps(item))
                    except Exception:
                        # Avoid crashing the app on WS failure; audio will just stop.
                        pass

                asyncio.run(_run())

            threading.Thread(target=_text_ws_worker, daemon=True).start()

        for chunk in stream:
            # OpenAI ChatCompletionChunk: choices[0].delta.content contains new text
            content_delta = ""
            try:
                if chunk.choices and chunk.choices[0].delta:
                    content_delta = chunk.choices[0].delta.content or ""
            except Exception:
                # Fallback for any unexpected structure
                content_delta = ""

            if not content_delta:
                continue

            if first_token_latency is None:
                first_token_latency = time.time() - t_request

            response_text += content_delta
            response_placeholder.markdown(response_text)

            # Push token-level text into ElevenLabs bridge
            if text_ws_queue is not None:
                text_ws_queue.put({"type": "text_delta", "text": content_delta})

        # Signal text end to bridge
        if text_ws_queue is not None:
            text_ws_queue.put({"type": "end"})
            text_ws_queue.put(None)

        response = response_text

        # --- Generate TTS and measure / stream audio for non-advanced path ---
        audio_latency = None
        if (
            tts_enabled
            and selected_voice_id
            and el_api_key
            and response
            and not advanced_streaming
        ):
            try:
                t_tts_start = time.time()
                el_client = ElevenLabs(api_key=el_api_key)
                audio_result = el_client.text_to_speech.convert(
                    voice_id=selected_voice_id,
                    model_id=tts_model,
                    text=response,
                    output_format="mp3_44100_128",
                )
                # convert() may return bytes or a generator/iterator of chunks
                if isinstance(audio_result, bytes):
                    audio_bytes = audio_result
                else:
                    audio_bytes = b"".join(audio_result)

                audio_latency = time.time() - t_tts_start

                # Use Streamlit's native audio player
                st.audio(audio_bytes, format="audio/mpeg", autoplay=True)
            except Exception as e:
                st.error(f"TTS generation failed: {str(e)}")

        # --- Show latency metrics under the assistant message ---
        if first_token_latency is not None:
            latency_text = f"First token latency: {first_token_latency*1000:.0f} ms"
            if audio_latency is not None:
                latency_text += f" • Audio ready latency: {audio_latency*1000:.0f} ms"
            st.caption(latency_text)
     
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
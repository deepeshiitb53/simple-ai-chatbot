import asyncio
import json
import base64
import logging
from typing import Dict, Optional, Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from elevenlabs.client import ElevenLabs
import websockets
from websockets.exceptions import ConnectionClosed

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(title="Realtime TTS Bridge")

# Allow local dev from Streamlit frontend and browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TTSRequest(BaseModel):
    """Legacy HTTP TTS request (kept for compatibility)."""

    session_id: str
    text: str
    api_key: str
    voice_id: str
    model_id: str = "eleven_flash_v2_5"
    output_format: str = "mp3_44100_128"


class SessionConfig(BaseModel):
    """Config required to start a Realtime ElevenLabs session."""

    api_key: str
    voice_id: str
    model_id: str = "eleven_flash_v2_5"
    output_format: str = "mp3_44100_128"


class SessionState:
    """Holds per-session state for the Realtime WS bridge."""

    def __init__(self, session_id: str, cfg: SessionConfig) -> None:
        self.session_id = session_id
        self.cfg = cfg
        self.text_queue: asyncio.Queue[dict] = asyncio.Queue()
        self.audio_clients: Set[WebSocket] = set()
        self.eleven_task: Optional[asyncio.Task] = None


sessions: Dict[str, SessionState] = {}


def get_session(session_id: str, cfg: Optional[SessionConfig] = None) -> SessionState:
    state = sessions.get(session_id)
    if state is None:
        if cfg is None:
            raise RuntimeError("Session not initialized")
        state = SessionState(session_id, cfg)
        sessions[session_id] = state
    return state


async def run_eleven_realtime(state: SessionState) -> None:
    """Maintain a Realtime WS session with ElevenLabs for this state.

    - Reads text messages from state.text_queue and forwards them.
    - Reads audio frames from ElevenLabs and fans them out to all audio WebSocket clients.
    
    Uses ElevenLabs WebSocket streaming API:
    wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream-input?model_id={model_id}
    
    Text is buffered into sentence-like chunks for better audio quality.
    """

    # Use pcm_24000 for raw audio that can be played chunk by chunk
    output_format = "pcm_24000"
    
    url = (
        f"wss://api.elevenlabs.io/v1/text-to-speech/{state.cfg.voice_id}/stream-input"
        f"?model_id={state.cfg.model_id}&output_format={output_format}"
    )
    headers = {"xi-api-key": state.cfg.api_key}

    logger.info(f"Connecting to ElevenLabs: {url}")

    try:
        async with websockets.connect(url, additional_headers=headers) as ws:
            logger.info("Connected to ElevenLabs WebSocket")
            
            # Send BOS (beginning of stream) message
            bos_msg = {
                "text": " ",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.8,
                },
                "xi_api_key": state.cfg.api_key,
            }
            await ws.send(json.dumps(bos_msg))
            logger.debug("Sent BOS message")

            async def text_pump() -> None:
                """Buffer text into sentence-like chunks before sending."""
                text_buffer = ""
                sentence_endings = ".!?;:"
                
                while True:
                    msg = await state.text_queue.get()
                    msg_type = msg.get("type")
                    logger.debug(f"Text pump received: {msg_type}")
                    
                    if msg_type == "end":
                        # Send any remaining buffered text
                        if text_buffer.strip():
                            payload = {"text": text_buffer, "try_trigger_generation": True}
                            await ws.send(json.dumps(payload))
                            logger.debug(f"Sent final buffered text: {text_buffer[:50]}...")
                        # Send EOS (end of stream) message
                        try:
                            await ws.send(json.dumps({"text": ""}))
                            logger.debug("Sent EOS message")
                        except Exception as e:
                            logger.error(f"Error sending EOS: {e}")
                        break
                    elif msg_type == "text_delta":
                        text = msg.get("text") or ""
                        if not text:
                            continue
                        
                        text_buffer += text
                        
                        # Check if we have a sentence ending or buffer is large enough
                        should_send = False
                        if any(end in text_buffer for end in sentence_endings):
                            should_send = True
                        elif len(text_buffer) > 100:  # Send if buffer gets too large
                            should_send = True
                        
                        if should_send:
                            payload = {"text": text_buffer, "try_trigger_generation": True}
                            await ws.send(json.dumps(payload))
                            logger.debug(f"Sent buffered text ({len(text_buffer)} chars): {text_buffer[:50]}...")
                            text_buffer = ""

            async def audio_pump() -> None:
                logger.info("Audio pump started")
                async for raw in ws:
                    try:
                        data = json.loads(raw)
                    except Exception:
                        continue
                    
                    # ElevenLabs returns audio in base64 under "audio" key
                    audio_b64 = data.get("audio")
                    if not audio_b64:
                        # Check for errors
                        if "error" in data:
                            logger.error(f"ElevenLabs error: {data['error']}")
                        continue
                    
                    try:
                        audio_bytes = base64.b64decode(audio_b64)
                        logger.debug(f"Received audio chunk: {len(audio_bytes)} bytes")
                    except Exception as e:
                        logger.error(f"Error decoding audio: {e}")
                        continue
                    
                    # Fan out to all connected browser audio clients
                    for client in list(state.audio_clients):
                        try:
                            await client.send_bytes(audio_bytes)
                        except Exception as e:
                            logger.error(f"Error sending to client: {e}")
                            try:
                                await client.close()
                            except Exception:
                                pass
                            state.audio_clients.discard(client)

            await asyncio.gather(text_pump(), audio_pump())
    except ConnectionClosed as e:
        logger.warning(f"ElevenLabs connection closed: {e}")
        return
    except Exception as e:
        logger.error(f"ElevenLabs WS error: {e}", exc_info=True)
        return


@app.websocket("/ws/text/{session_id}")
async def text_ws(websocket: WebSocket, session_id: str) -> None:
    """WebSocket endpoint for backend (Streamlit) to push text deltas.

    Protocol:
    - First message: JSON config
        { "api_key": "...", "voice_id": "...", "model_id": "...", "output_format": "..." }
    - Subsequent messages: JSON
        { "type": "text_delta", "text": "..." }
        { "type": "end" }
    """

    await websocket.accept()
    cfg: Optional[SessionConfig] = None
    state: Optional[SessionState] = None
    try:
        # First message must be config
        first = await websocket.receive_text()
        data = json.loads(first)
        cfg = SessionConfig(
            api_key=data["api_key"],
            voice_id=data["voice_id"],
            model_id=data.get("model_id", "eleven_flash_v2_5"),
            output_format=data.get("output_format", "mp3_44100_128"),
        )
        state = get_session(session_id, cfg)
        if state.eleven_task is None:
            state.eleven_task = asyncio.create_task(run_eleven_realtime(state))

        # Forward all subsequent text messages into the session queue
        while True:
            msg = await websocket.receive_text()
            obj = json.loads(msg)
            await state.text_queue.put(obj)
            if obj.get("type") == "end":
                break
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass


@app.websocket("/ws/audio/{session_id}")
async def audio_ws(websocket: WebSocket, session_id: str) -> None:
    """WebSocket endpoint that streams raw audio chunks to the browser."""

    await websocket.accept()
    logger.info(f"Audio WS connected for session {session_id}")
    
    # Wait for session to be created (up to 5 seconds)
    for _ in range(50):
        state = sessions.get(session_id)
        if state is not None:
            break
        await asyncio.sleep(0.1)
    
    if state is None:
        logger.warning(f"No session found for {session_id}, closing audio WS")
        await websocket.close()
        return

    state.audio_clients.add(websocket)
    logger.info(f"Audio client added, total: {len(state.audio_clients)}")
    
    try:
        # We only send from server to client; keep connection alive by receiving pings
        while True:
            try:
                # Wait for any message (ping/pong) or disconnect
                await asyncio.wait_for(websocket.receive(), timeout=60)
            except asyncio.TimeoutError:
                # Send a ping to keep alive
                continue
    except WebSocketDisconnect:
        logger.info(f"Audio WS disconnected for session {session_id}")
    finally:
        state.audio_clients.discard(websocket)
        try:
            await websocket.close()
        except Exception:
            pass


@app.post("/tts")
async def start_tts(req: TTSRequest) -> dict:
    """Legacy HTTP streaming TTS using ElevenLabs SDK.

    Kept for backwards compatibility with the earlier design; not used
    in the true token-level streaming path.
    """

    client = ElevenLabs(api_key=req.api_key)
    # Consume the iterator to trigger generation; caller does not use audio here.
    _ = list(
        client.text_to_speech.stream(
            voice_id=req.voice_id,
            model_id=req.model_id,
            text=req.text,
            output_format=req.output_format,
        )
    )
    return {"status": "ok"}
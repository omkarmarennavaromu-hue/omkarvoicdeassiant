"""
server.py — Omkar's Personal Assistant Backend
Flask server that handles:
  1. Audio upload → Whisper transcription
  2. Transcription → GPT chat (language-agnostic)
  3. GPT reply → TTS audio
  4. Audio streaming back to frontend
"""

import os
import io
import logging
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv

# ── Init ──────────────────────────────────────────────────────────────────────
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ── System prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a highly capable, concise, and friendly personal assistant named ARIA 
(Adaptive Reasoning Intelligence Assistant), serving Omkar personally.

CRITICAL LANGUAGE RULE:
- Detect the language the user is speaking in and ALWAYS reply in that EXACT SAME language.
- If the user speaks Hindi, reply in Hindi. English → English. Marathi → Marathi. Etc.
- Never switch languages unless explicitly asked to.

PERSONALITY:
- Warm, professional, slightly futuristic in tone.
- Concise: keep replies brief and conversational (1–3 sentences unless detail is needed).
- Proactive: offer helpful follow-ups when appropriate.
- Address Omkar by name occasionally.

You have no memory between sessions, so don't reference past conversations."""

# ── Voice map (frontend label → OpenAI TTS voice) ────────────────────────────
VOICE_MAP = {
    "alloy":   "alloy",    # Neutral / clear
    "nova":    "nova",     # Female
    "onyx":    "onyx",     # Deep male
    "shimmer": "shimmer",  # Clear female
    "echo":    "echo",     # Male
    "fable":   "fable",    # Expressive
}

# ── Chat conversation memory (per session — cleared on restart) ───────────────
conversation_history = []
MAX_HISTORY = 20  # keep last 20 exchanges to avoid token overflow


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "Omkar's Assistant"})


@app.route("/chat", methods=["POST"])
def chat():
    """
    Expects:
      - multipart/form-data
      - 'audio' file field (webm/mp4/ogg — any format Whisper accepts)
      - 'voice' text field (optional, defaults to 'alloy')

    Returns:
      - audio/mpeg stream
    """
    # ── Validate input ────────────────────────────────────────────────────────
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    voice_key  = request.form.get("voice", "alloy").lower()
    tts_voice  = VOICE_MAP.get(voice_key, "alloy")

    log.info(f"Received audio: {audio_file.filename}, size: {audio_file.content_length}, voice: {tts_voice}")

    # ── Step 1: Transcribe with Whisper ──────────────────────────────────────
    try:
        audio_bytes = audio_file.read()
        if len(audio_bytes) < 1000:
            return jsonify({"error": "Audio too short"}), 400

        # Whisper needs a filename with extension for format detection
        filename    = audio_file.filename or "recording.webm"
        audio_buffer = io.BytesIO(audio_bytes)
        audio_buffer.name = filename

        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=(filename, audio_buffer, "audio/webm"),
            # No language param → Whisper auto-detects
        )
        user_text = transcription.text.strip()
        log.info(f"Transcribed: '{user_text}'")

        if not user_text:
            return jsonify({"error": "Could not transcribe audio — please speak clearly"}), 400

    except Exception as e:
        log.error(f"Transcription error: {e}")
        return jsonify({"error": f"Transcription failed: {str(e)}"}), 500

    # ── Step 2: Chat with GPT ─────────────────────────────────────────────────
    try:
        # Build message list with rolling history
        conversation_history.append({"role": "user", "content": user_text})
        if len(conversation_history) > MAX_HISTORY:
            del conversation_history[0:2]  # remove oldest user+assistant pair

        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.75,
            max_tokens=300,
        )

        assistant_text = response.choices[0].message.content.strip()
        log.info(f"Assistant: '{assistant_text}'")

        # Store assistant reply in history
        conversation_history.append({"role": "assistant", "content": assistant_text})

    except Exception as e:
        log.error(f"Chat error: {e}")
        return jsonify({"error": f"Chat failed: {str(e)}"}), 500

    # ── Step 3: TTS → audio stream ────────────────────────────────────────────
    try:
        tts_response = client.audio.speech.create(
            model="tts-1",
            voice=tts_voice,
            input=assistant_text,
            response_format="mp3",
        )

        audio_out = io.BytesIO(tts_response.content)
        audio_out.seek(0)
        log.info("TTS generated successfully")

        return send_file(
            audio_out,
            mimetype="audio/mpeg",
            as_attachment=False,
            download_name="response.mp3",
        )

    except Exception as e:
        log.error(f"TTS error: {e}")
        return jsonify({"error": f"TTS failed: {str(e)}"}), 500


@app.route("/reset", methods=["POST"])
def reset():
    """Clear conversation history."""
    conversation_history.clear()
    return jsonify({"status": "conversation reset"})


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set in .env file")
        exit(1)

    print("\n" + "="*50)
    print("  Omkar's Personal Assistant — Backend")
    print("  Running on http://localhost:5000")
    print("="*50 + "\n")

    app.run(host="0.0.0.0", port=5000, debug=False)

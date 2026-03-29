# omkarvoicdeassiant
# Omkar's Personal Assistant 🎙️

A Jarvis-style voice AI assistant with a glowing orb UI and full OpenAI integration.

---

## Folder Structure

```
voice-assistant/
├── index.html          ← Frontend (open directly in browser)
├── server.py           ← Flask backend
├── requirements.txt    ← Python dependencies
├── .env.example        ← Copy this to .env and add your key
└── README.md
```

---

## Setup & Run

### 1. Clone / copy the files
Place all files in a single folder, e.g. `voice-assistant/`.

### 2. Create your `.env` file
```bash
cp .env.example .env
```
Open `.env` and replace the placeholder with your real OpenAI API key:
```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```
Get a key at: https://platform.openai.com/api-keys

### 3. Install Python dependencies
```bash
pip install -r requirements.txt
```
> Requires Python 3.9+

### 4. Start the backend
```bash
python server.py
```
You should see:
```
==================================================
  Omkar's Personal Assistant — Backend
  Running on http://localhost:5000
==================================================
```

### 5. Open the frontend
Simply open `index.html` in your browser (Chrome or Edge recommended):
```bash
# macOS
open index.html

# Linux
xdg-open index.html

# Windows
start index.html
```
Or serve it with any static server:
```bash
python -m http.server 8080
# then open http://localhost:8080
```

---

## How to Use

1. Select a **voice profile** from the bottom bar
2. Click **INITIALIZE** — the orb starts its idle breathing animation
3. **Speak** — the orb pulses with your voice volume
4. When you stop speaking, audio is sent automatically
5. The orb enters **THINKING** mode while the AI processes
6. The AI replies and the orb **SPEAKS** in sync with the audio
7. It automatically returns to listening for your next input
8. Click **TERMINATE** to end the session

---

## Voice Profiles

| Button   | OpenAI Voice | Character              |
|----------|-------------|------------------------|
| Alloy    | alloy       | Neutral, clear         |
| Nova     | nova        | Female, warm           |
| Onyx     | onyx        | Deep male              |
| Shimmer  | shimmer     | Clear female, bright   |

---

## Orb States

| State     | Animation                         |
|-----------|-----------------------------------|
| Idle      | Slow breathing glow               |
| Listening | Pulse rings expand with mic input |
| Thinking  | Shimmer + orbit dots rotate       |
| Speaking  | Rapid pulse synced to audio       |

---

## Language Support

The AI automatically detects and replies in the same language you speak.
- Speak Hindi → replies in Hindi
- Speak English → replies in English
- Speak Marathi → replies in Marathi
- Any language Whisper supports → auto-matched

---

## Requirements

- **Python** 3.9+
- **Browser**: Chrome 90+ or Edge 90+ (for MediaRecorder + Web Audio API)
- **Microphone** access allowed in browser
- **OpenAI API key** with access to:
  - `whisper-1` (transcription)
  - `gpt-4o-mini` (chat)
  - `tts-1` (text-to-speech)

# Easy Note Taker 📝

**Easy Note Taker** is a small FastAPI + static frontend project for uploading meeting audio, generating transcripts, translations, summaries, and downloading results.

Visit here for live demo: `https://easy-note-taker-app.vercel.app/`

## 🚀 Quickstart

You can run the project in two ways:

1. **Docker Compose** – fully reproducible setup
2. **Local Python development** – for development and debugging

---

## Option 1: Run with Docker Compose

### Prerequisites

- Docker
- Docker Compose

### Start the application

From the project root:

````bash
docker-compose up --build
````
- Home: `http://localhost:3000`
---
## Option 2: Local python development

### Prerequisites
- Python 3.10+ (Windows instructions below)

1. Create and activate a virtual environment (PowerShell):

```powershell
python -m venv venv
# Activate in PowerShell
venv\Scripts\Activate.ps1
# Or in cmd.exe
# venv\Scripts\activate.bat
````

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the server (development):

```bash
uvicorn app:app --reload
```

4. Open the app in your browser:

- Home: `http://127.0.0.1:8000/`

---

## ⚙️ Features

- Frontend pages in `frontend/` (Tailwind CDN used for styles).
- Shared navbar partial: `frontend/_navbar.html` (used via Jinja include).
- Upload page (`/upload.html`) accepts audio and posts to `POST /process`.
- Server saves uploads to the `uploads/` directory and calls `process_meeting(file_path)` to produce results.

### 🤖 AI Features

- **Transcription** — Uses OpenAI Whisper (model: `base`) to transcribe audio into text and saves a raw transcript (`output/transcript_raw.txt`).
- **Translation** — Uses MarianMT (Helsinki-NLP/opus-mt-mul-en via `transformers`) to translate the transcript and saves `output/translated.txt`.
- **Summarization & Action Items** — Uses a summarization pipeline (`facebook/bart-large-cnn`) to produce meeting summaries and extract key action items (`output/summary.txt`).
- **Speaker Diarization** — Splits audio into chunks, extracts speaker embeddings with `resemblyzer`, clusters with `AgglomerativeClustering` (scikit-learn), and assigns speaker labels to transcript segments (`output/speaker_transcript.txt`).
- **Configurable** — `CHUNK_DURATION_MS` and `NUM_SPEAKERS` are defined in `process_meeting.py` and can be adjusted for different audio lengths and expected speaker counts.

---

## 🏗️ Architecture

This project follows a simple server-driven static-front-end pattern with an AI processing module:

- **Backend**: FastAPI (`app.py`) accepts the uploaded audio and exposes endpoints:
  - `GET /` → serves `frontend/index.html`
  - `GET /upload.html`, `GET /features.html`, `GET /contact.html` → templates
  - `POST /process` → accepts `file` (audio), saves it to `uploads/`, and calls `process_meeting(file_path)`
- **AI Processing**: `process_meeting.py` performs the heavy lifting (transcription, translation, summarization, and diarization) and writes output files to `output/` and returns a JSON payload containing `transcript`, `translated`, `summary`, and `speaker_transcript`.
- **Frontend**: Static HTML templates in `frontend/` (uses Tailwind CDN). Shared snippets live in `frontend/_navbar.html` and pages are rendered via Jinja2 templates.
- **Storage**: Incoming uploads are stored in `uploads/` and processing artifacts are written to `output/`.

Example request flow:

````
Browser --(POST /process with file)--> FastAPI --(saves file)-> uploads/ --(process_meeting)--> output/ + JSON response --> Browser (shows transcript/summary/etc.)
---

## 🧪 API / Testing

- Test `/process` using curl:

```bash
curl -F "file=@/path/to/sample.mp3" http://127.0.0.1:8000/process
````

- The response will be JSON containing keys such as `transcript`, `translated`, `summary`, and `speaker_transcript` (depends on `process_meeting` implementation).

---

## ✨ Contributing

Contributions welcome! Open issues or submit a pull request. Keep changes small and focused.

---

© Easy Note Taker

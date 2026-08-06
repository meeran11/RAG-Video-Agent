# AI Video Agent

A smart AI-powered assistant for turning videos and meetings into structured knowledge. Upload a local file or share a YouTube link, and the system will transcribe the content, generate a summary, extract action items and decisions, and let you ask questions about the material using retrieval-augmented generation (RAG).

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![Whisper](https://img.shields.io/badge/Whisper-Transcription-orange)
![LangChain](https://img.shields.io/badge/LangChain-RAG-purple)

## ✨ What this project does

This project helps you quickly turn long video content into something actionable:

- Transcribes audio using Whisper
- Generates a concise and professional summary
- Extracts action items, key decisions, and open questions
- Builds a searchable knowledge base for Q&A over the transcript
- Exposes a FastAPI backend for integration into apps or dashboards

## 🧠 Key features

- Support for local video/audio files and YouTube URLs
- Audio preprocessing and chunking for long recordings
- AI-generated meeting titles and summaries
- Structured extraction of follow-ups and decisions
- Conversational chat over the processed transcript via RAG

## 🏗️ Architecture overview

The workflow is simple and modular:

1. Input ingestion
   - Accepts a local file path or a YouTube URL
2. Audio processing
   - Downloads, converts, and chunks audio into manageable segments
3. Transcription
   - Runs Whisper to generate a transcript
4. Intelligence layer
   - Summarizes the transcript and extracts important insights
5. RAG chat
   - Builds a vector-based index so you can ask questions about the content

## 🚀 Getting started

### Prerequisites

Before you begin, make sure you have:

- Python 3.10 or newer
- FFmpeg installed and available on your system
- A Mistral API key

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd "AI Video Agent"
```

### 2. Create a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
MISTRAL_API_KEY=your_mistral_api_key
WHISPER_MODEL=small
```

> You can change `WHISPER_MODEL` to `tiny`, `base`, `small`, `medium`, or `large` depending on your hardware and accuracy needs.

## ▶️ Run the CLI

```bash
python main.py
```

The CLI will prompt you for:

- a local file path or YouTube URL
- whether you want translation to English

It will then output:

- the generated title
- a summary
- action items
- key decisions
- open questions
- an interactive Q&A experience over the transcript

## 🌐 Run the API server

Start the FastAPI backend with:

```bash
uvicorn video_agent_api:app --reload --port 8000
```

### Available API endpoints

- `POST /api/videos/upload` — Upload a video file for processing
- `POST /api/videos/process` — Process a video from a URL
- `GET /api/videos` — List processed videos
- `GET /api/videos/{id}` — Retrieve a specific video result
- `DELETE /api/videos/{id}` — Remove a video entry
- `POST /api/chat` — Ask a question about a processed video

## 📁 Project structure

```text
.
├── main.py                  # CLI entry point
├── video_agent_api.py       # FastAPI backend
├── requirements.txt         # Python dependencies
├── core/                    # Transcription, summarization, extraction, RAG logic
├── utils/                   # Audio processing helpers
├── api/                     # Additional API modules
├── uploads/                 # Uploaded files
├── downloads/               # Downloaded media assets
└── vector-db/               # Vector store files
```

## 🛠️ Tech stack

- Python
- FastAPI
- Whisper
- LangChain
- Mistral AI
- Chroma / vector storage
- yt-dlp and pydub for media handling

## 💡 Notes

- Processing time depends on the length of the video and the Whisper model size.
- Large videos may take a while to transcribe and summarize.
- For the best experience, use a machine with sufficient CPU/GPU resources.

## 🤝 Contributing

Contributions are welcome. If you improve the pipeline, add new features, or fix issues, feel free to open a pull request.

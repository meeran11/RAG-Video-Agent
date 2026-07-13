"""
FastAPI backend connecting the VideoRAG frontend (frontend/) to the
processing pipeline defined in main.py / core / utils.

Implements the API contract documented in frontend/INTEGRATION_GUIDE.md:

  POST   /api/videos/upload   - upload a video file, kicks off processing
  POST   /api/videos/process  - add a video from a URL, kicks off processing
  GET    /api/videos          - list all videos
  GET    /api/videos/{id}     - get one video (status + results once ready)
  DELETE /api/videos/{id}     - remove a video
  POST   /api/chat            - ask a question about a processed video

Run with:
    uvicorn video_agent_api:app --reload --port 8000
"""

import os
import shutil
import threading
import uuid
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarize import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def format_date(dt: datetime) -> str:
    """M/D/Y with no leading zeros, without relying on the platform-specific
    '%-m'/'%-d' strftime flags (those aren't supported on Windows)."""
    return f"{dt.month}/{dt.day}/{dt.year}"

app = FastAPI(title="VideoRAG API")

# The Next.js dev server runs on :3000 by default.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------------------------
# In-memory store. Good enough for a single-process dev/demo backend.
# Each entry looks like:
# {
#   "id": str, "name": str, "size": str, "status": "processing"|"ready"|"error",
#   "uploadedAt": str, "type": "uploaded"|"url", "url": Optional[str],
#   "error": Optional[str],
#   "title": Optional[str], "summary": Optional[str],
#   "action_items": Optional[str], "key_decisions": Optional[str],
#   "open_questions": Optional[str],
#   "rag_chain": Optional[Runnable],  # not serialized in responses
# }
# ----------------------------------------------------------------------
VIDEOS: dict[str, dict] = {}
VIDEOS_LOCK = threading.Lock()


def public_video(video: dict) -> dict:
    """Strip internal-only fields (like the rag_chain object) before sending to the client."""
    return {k: v for k, v in video.items() if k not in ("rag_chain",)}


def run_pipeline_for_video(video_id: str, source: str, translate: bool = False):
    """Runs the full pipeline (transcribe -> summarize -> extract -> build RAG index)
    in a background thread and updates VIDEOS[video_id] as it goes."""
    try:
        chunks = process_input(source)
        transcript = transcribe_all(chunks, translate=translate)

        title = generate_title(transcript)
        summary = summarize(transcript)
        action_items = extract_action_items(transcript)
        key_decisions = extract_key_decisions(transcript)
        open_questions = extract_questions(transcript)

        # Give each video its own Chroma collection so answers don't leak
        # across different videos' content. Also pass the summary in so the
        # assistant can answer broad "what is this about" style questions,
        # not just ones that happen to match a retrieved transcript chunk.
        rag_chain = build_rag_chain(
            transcript, collection_name=f"video_{video_id}", summary=summary
        )

        with VIDEOS_LOCK:
            if video_id in VIDEOS:
                VIDEOS[video_id].update(
                    {
                        "status": "ready",
                        "name": title or VIDEOS[video_id]["name"],
                        "title": title,
                        "summary": summary,
                        "action_items": action_items,
                        "key_decisions": key_decisions,
                        "open_questions": open_questions,
                        "rag_chain": rag_chain,
                    }
                )
    except Exception as exc:  # noqa: BLE001 - want to surface any pipeline failure to the UI
        with VIDEOS_LOCK:
            if video_id in VIDEOS:
                VIDEOS[video_id].update({"status": "error", "error": str(exc)})


def start_processing(video_id: str, source: str, translate: bool = False):
    thread = threading.Thread(
        target=run_pipeline_for_video, args=(video_id, source, translate), daemon=True
    )
    thread.start()


# ----------------------------------------------------------------------
# Videos
# ----------------------------------------------------------------------

@app.post("/api/videos/upload")
async def upload_video(file: UploadFile = File(...)):
    video_id = f"video-{uuid.uuid4().hex[:12]}"
    dest_path = os.path.join(UPLOAD_DIR, f"{video_id}_{file.filename}")

    with open(dest_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    size_mb = f"{os.path.getsize(dest_path) / (1024 * 1024):.2f}"

    video = {
        "id": video_id,
        "name": file.filename,
        "size": size_mb,
        "type": "uploaded",
        "status": "processing",
        "uploadedAt": format_date(datetime.now()),
        "error": None,
    }

    with VIDEOS_LOCK:
        VIDEOS[video_id] = video

    start_processing(video_id, dest_path)

    return public_video(video)


class ProcessRequest(BaseModel):
    videoId: Optional[str] = None
    url: str
    translate: bool = False


@app.post("/api/videos/process")
async def process_video(payload: ProcessRequest):
    """Adds (and starts processing) a video from a URL. If videoId is given
    and already exists, re-processing is kicked off for that entry instead
    of creating a new one."""
    video_id = payload.videoId or f"video-{uuid.uuid4().hex[:12]}"

    with VIDEOS_LOCK:
        existing = VIDEOS.get(video_id)
        if existing:
            existing.update({"status": "processing", "error": None, "url": payload.url})
            video = existing
        else:
            video = {
                "id": video_id,
                "name": payload.url,
                "url": payload.url,
                "type": "url",
                "status": "processing",
                "uploadedAt": format_date(datetime.now()),
                "error": None,
            }
            VIDEOS[video_id] = video

    start_processing(video_id, payload.url, payload.translate)

    return public_video(video)


@app.get("/api/videos")
async def list_videos():
    with VIDEOS_LOCK:
        return [public_video(v) for v in VIDEOS.values()]


@app.get("/api/videos/{video_id}")
async def get_video(video_id: str):
    with VIDEOS_LOCK:
        video = VIDEOS.get(video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        return public_video(video)


@app.delete("/api/videos/{video_id}")
async def delete_video(video_id: str):
    with VIDEOS_LOCK:
        if video_id not in VIDEOS:
            raise HTTPException(status_code=404, detail="Video not found")
        del VIDEOS[video_id]
    return {"id": video_id, "deleted": True}


# ----------------------------------------------------------------------
# Chat
# ----------------------------------------------------------------------

class ChatRequest(BaseModel):
    videoId: str
    query: str


@app.post("/api/chat")
async def chat(payload: ChatRequest):
    with VIDEOS_LOCK:
        video = VIDEOS.get(payload.videoId)

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    if video["status"] == "processing":
        raise HTTPException(status_code=409, detail="Video is still processing")
    if video["status"] == "error":
        raise HTTPException(status_code=422, detail=video.get("error") or "Video processing failed")

    rag_chain = video.get("rag_chain")
    if rag_chain is None:
        raise HTTPException(status_code=422, detail="Video has no RAG index available")

    answer = ask_question(rag_chain, payload.query)
    return {"answer": answer}


@app.get("/api/health")
async def health():
    return {"status": "ok"}
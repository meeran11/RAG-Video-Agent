# Running the connected app

The frontend (`frontend/`) now talks to a real backend: `video_agent_api.py`,
a FastAPI wrapper around the existing pipeline (`main.py` / `core/` / `utils/`).

## 1. Backend

```bash
# from the repo root
pip install -r requirements.txt --break-system-packages   # if not already installed
cp .env.example .env   # if you have one; otherwise create .env with MISTRAL_API_KEY=...

uvicorn video_agent_api:app --reload --port 8000
```

This exposes:

- `POST /api/videos/upload` — multipart file upload, starts processing in a background thread
- `POST /api/videos/process` — `{ "url": "..." }`, for YouTube/remote URLs, also backgrounded
- `GET  /api/videos` — list all videos + status (`processing` / `ready` / `error`)
- `GET  /api/videos/{id}` — single video, includes `summary`, `action_items`,
  `key_decisions`, `open_questions` once `status` is `ready`
- `DELETE /api/videos/{id}`
- `POST /api/chat` — `{ "videoId": "...", "query": "..." }` → `{ "answer": "..." }`

Each video gets processed through the same pipeline as the CLI
(`process_input` → `transcribe_all` → `summarize`/`extract_*` →
`build_rag_chain`) and gets its own Chroma collection
(`video_<id>`) so multiple videos' embeddings don't mix.

Uploaded files are written to `uploads/` (not `downloads/`, to avoid
colliding with the CLI's yt-dlp download folder).

## 2. Frontend

```bash
cd frontend
pnpm install     # or npm install
pnpm dev         # or npm run dev
```

`frontend/.env.local` already points `NEXT_PUBLIC_API_URL` at
`http://localhost:8000`. Change it if you run the backend elsewhere.

Open http://localhost:3000. Uploading a file or pasting a URL now hits the
real backend, the video list polls every 3s while anything is
`processing`, and the chat panel calls `/api/chat` against that video's
RAG index once it's `ready`.

## Notes / things you may want to change next

- State is in-memory in `video_agent_api.py` (a plain dict) — restart the
  server and the video list resets. Swap in a real DB if you need
  persistence.
- Whisper transcription and embedding are CPU/GPU-bound and can take a
  while for long videos; the background thread keeps the API responsive
  in the meantime, but there's no progress percentage, just
  `processing` → `ready`/`error`.
- CORS is currently locked to `http://localhost:3000` — update the
  `allow_origins` list in `video_agent_api.py` for other environments.

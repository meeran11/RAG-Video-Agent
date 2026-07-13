const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Video {
  id: string;
  name: string;
  size?: string;
  type: 'uploaded' | 'url';
  url?: string;
  status: 'processing' | 'ready' | 'error';
  uploadedAt: string;
  error?: string | null;
  title?: string;
  summary?: string;
  action_items?: string;
  key_decisions?: string;
  open_questions?: string;
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      // response wasn't JSON, fall back to statusText
    }
    throw new Error(detail);
  }
  return res.json();
}

export async function uploadVideo(file: File): Promise<Video> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_URL}/api/videos/upload`, {
    method: 'POST',
    body: formData,
  });

  return handleResponse<Video>(res);
}

export async function addVideoFromUrl(url: string): Promise<Video> {
  const res = await fetch(`${API_URL}/api/videos/process`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  });

  return handleResponse<Video>(res);
}

export async function fetchVideos(): Promise<Video[]> {
  const res = await fetch(`${API_URL}/api/videos`);
  return handleResponse<Video[]>(res);
}

export async function fetchVideo(videoId: string): Promise<Video> {
  const res = await fetch(`${API_URL}/api/videos/${videoId}`);
  return handleResponse<Video>(res);
}

export async function deleteVideo(videoId: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/videos/${videoId}`, {
    method: 'DELETE',
  });
  await handleResponse(res);
}

export async function askQuestion(videoId: string, query: string): Promise<string> {
  const res = await fetch(`${API_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ videoId, query }),
  });

  const data = await handleResponse<{ answer: string }>(res);
  return data.answer;
}

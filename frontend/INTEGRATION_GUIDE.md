# VideoRAG Frontend - Backend Integration Guide

This is a modern, elegant frontend for the RAG Video Agent. The frontend is built with React, Next.js, Tailwind CSS, and shadcn/ui.

## Features

✨ **Modern Design**
- Minimalistic and elegant UI with a clean aesthetic
- Golden accent color (#D4AF37) with neutral monochrome palette
- Responsive design for mobile, tablet, and desktop

🎥 **Video Management**
- Upload videos directly or add from URL
- Video list with status tracking (processing, ready, error)
- Delete videos from the list
- Real-time status updates

💬 **Interactive Chat Interface**
- Ask questions about video content
- Message history with timestamps
- Loading states and animations
- Disabled states during video processing

⚡ **Performance**
- Built with Next.js 16 for optimal performance
- Client-side state management with React hooks
- Smooth animations and transitions

## Project Structure

```
app/
├── page.tsx                 # Main app page
├── layout.tsx              # Root layout
└── globals.css             # Global styles with theme tokens

components/
├── header.tsx              # App header with branding
├── video-uploader.tsx      # Video upload/URL input component
├── video-list.tsx          # List of uploaded videos
├── chat-interface.tsx      # Chat UI for asking questions
└── ui/
    ├── button.tsx          # shadcn button component
    └── input.tsx           # shadcn input component
```

## Backend Integration

The frontend is designed as a complete UI layer ready to connect to your RAG Video Agent backend. Here's what needs to be implemented:

### 1. Video Upload Endpoint

**File**: `components/video-uploader.tsx` (Lines 36-43 and 51-62)

Replace the simulated upload with actual API calls:

```typescript
// Example: POST /api/videos/upload
const formData = new FormData();
formData.append('file', file);

const response = await fetch('/api/videos/upload', {
  method: 'POST',
  body: formData,
});

const video = await response.json();
onVideoAdded(video);
```

### 2. Video Processing Endpoint

The video processing is simulated in `components/video-uploader.tsx`. Connect to your backend:

```typescript
// Example: POST /api/videos/process
const response = await fetch('/api/videos/process', {
  method: 'POST',
  body: JSON.stringify({
    videoId: video.id,
    url: video.url, // if from URL
  }),
  headers: { 'Content-Type': 'application/json' },
});
```

### 3. Chat/RAG Query Endpoint

**File**: `components/chat-interface.tsx` (Lines 54-66)

Replace the simulated response with RAG queries:

```typescript
// Example: POST /api/chat
const response = await fetch('/api/chat', {
  method: 'POST',
  body: JSON.stringify({
    videoId: video.id,
    query: input,
    messages: messages,
  }),
  headers: { 'Content-Type': 'application/json' },
});

const data = await response.json();
const assistantMessage: Message = {
  id: `msg-${Date.now() + 1}`,
  role: 'assistant',
  content: data.answer, // Your RAG response
  timestamp: new Date(),
};
```

### 4. Video List Endpoint (Optional)

For persistent video storage, add an endpoint to fetch videos:

```typescript
// app/page.tsx - useEffect hook
useEffect(() => {
  const fetchVideos = async () => {
    const response = await fetch('/api/videos');
    const videos = await response.json();
    setVideos(videos);
  };
  
  fetchVideos();
}, []);
```

## API Contract

Your backend should implement these endpoints:

### POST `/api/videos/upload`
Upload a video file.

**Request**:
```
Content-Type: multipart/form-data
file: File
```

**Response**:
```json
{
  "id": "video-123",
  "name": "filename.mp4",
  "size": "50.25",
  "status": "processing",
  "uploadedAt": "7/11/2026"
}
```

### POST `/api/videos/process`
Process a video (transcribe, embed, etc.)

**Request**:
```json
{
  "videoId": "video-123",
  "url": "https://example.com/video.mp4"
}
```

**Response**:
```json
{
  "videoId": "video-123",
  "status": "processing"
}
```

### POST `/api/chat`
Query the RAG system about a video.

**Request**:
```json
{
  "videoId": "video-123",
  "query": "What is the main topic?",
  "messages": [...]
}
```

**Response**:
```json
{
  "answer": "Based on the video analysis...",
  "confidence": 0.95
}
```

### GET `/api/videos`
Fetch all videos (optional).

**Response**:
```json
[
  {
    "id": "video-123",
    "name": "filename.mp4",
    "status": "ready",
    "uploadedAt": "7/11/2026"
  }
]
```

## Deployment

### Via Vercel (Recommended)

```bash
# Install dependencies
npm install
# or
pnpm install

# Deploy to Vercel
vercel
```

### Via Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

### Self-Hosted

```bash
pnpm install
pnpm build
pnpm start
```

## Environment Variables

Create a `.env.local` file:

```
NEXT_PUBLIC_API_URL=http://localhost:8000  # Your backend URL
NEXT_PUBLIC_MAX_FILE_SIZE=1000            # Max upload size in MB
```

## Customization

### Colors & Branding

Edit `app/globals.css` to change the theme:

```css
:root {
  --background: oklch(0.99 0.001 0);
  --foreground: oklch(0.13 0.01 0);
  --accent: oklch(0.85 0.25 103);  /* Change this */
  /* ... other colors ... */
}
```

### Font

Edit `app/layout.tsx` to change fonts:

```typescript
import { YourFont } from 'next/font/google';

const font = YourFont({ subsets: ['latin'] });

export default function RootLayout(...) {
  // Use font.className
}
```

## Development

```bash
# Start dev server
pnpm dev

# Run type checking
pnpm type-check

# Build for production
pnpm build
```

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari 14+, Chrome Mobile)

## License

MIT

'use client';

import { useState } from 'react';
import { Upload, Link as LinkIcon, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface VideoUploaderProps {
  onVideoAdded: (video: any) => void;
}

export function VideoUploader({ onVideoAdded }: VideoUploaderProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [urlInput, setUrlInput] = useState('');
  const [mode, setMode] = useState<'upload' | 'url'>('upload');

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsLoading(true);
    try {
      // Simulate file upload - replace with actual API call
      const reader = new FileReader();
      reader.onload = () => {
        const video = {
          id: `video-${Date.now()}`,
          name: file.name,
          duration: '0:00',
          size: (file.size / (1024 * 1024)).toFixed(2),
          type: 'uploaded',
          status: 'processing',
          uploadedAt: new Date().toLocaleDateString(),
        };
        onVideoAdded(video);
        setIsLoading(false);
      };
      reader.readAsArrayBuffer(file);
    } catch (error) {
      console.error('Upload failed:', error);
      setIsLoading(false);
    }
  };

  const handleUrlSubmit = () => {
    if (!urlInput.trim()) return;

    setIsLoading(true);
    try {
      // Simulate URL processing - replace with actual API call
      const video = {
        id: `video-${Date.now()}`,
        name: new URL(urlInput).hostname || 'Video from URL',
        duration: '0:00',
        url: urlInput,
        type: 'url',
        status: 'processing',
        uploadedAt: new Date().toLocaleDateString(),
      };
      onVideoAdded(video);
      setUrlInput('');
      setIsLoading(false);
      setMode('upload');
    } catch (error) {
      console.error('URL processing failed:', error);
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <button
          onClick={() => setMode('upload')}
          className={`flex-1 rounded-lg border border-border px-3 py-2 text-sm font-medium transition-colors ${
            mode === 'upload'
              ? 'border-accent bg-accent text-accent-foreground'
              : 'text-foreground hover:bg-secondary'
          }`}
        >
          Upload
        </button>
        <button
          onClick={() => setMode('url')}
          className={`flex-1 rounded-lg border border-border px-3 py-2 text-sm font-medium transition-colors ${
            mode === 'url'
              ? 'border-accent bg-accent text-accent-foreground'
              : 'text-foreground hover:bg-secondary'
          }`}
        >
          From URL
        </button>
      </div>

      {mode === 'upload' ? (
        <label className="flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-border bg-secondary/30 px-4 py-8 text-center transition-colors hover:border-accent hover:bg-secondary">
          <Upload className="mb-2 h-6 w-6 text-muted-foreground" />
          <p className="text-sm font-medium text-foreground">
            Click to upload or drag and drop
          </p>
          <p className="text-xs text-muted-foreground">
            MP4, WebM, or other video formats
          </p>
          <input
            type="file"
            accept="video/*"
            onChange={handleFileUpload}
            disabled={isLoading}
            className="hidden"
          />
        </label>
      ) : (
        <div className="space-y-2">
          <Input
            type="url"
            placeholder="https://example.com/video.mp4"
            value={urlInput}
            onChange={(e) => setUrlInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleUrlSubmit()}
            disabled={isLoading}
            className="border-border"
          />
          <Button
            onClick={handleUrlSubmit}
            disabled={isLoading || !urlInput.trim()}
            className="w-full"
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <LinkIcon className="mr-2 h-4 w-4" />
                Add from URL
              </>
            )}
          </Button>
        </div>
      )}
    </div>
  );
}

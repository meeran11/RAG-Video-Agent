'use client';

import { Trash2, Play, Clock, Database } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface Video {
  id: string;
  name: string;
  duration?: string;
  size?: string;
  status: 'processing' | 'ready' | 'error';
  uploadedAt: string;
}

interface VideoListProps {
  videos: Video[];
  selectedId?: string;
  onSelect: (video: Video) => void;
  onRemove: (videoId: string) => void;
}

export function VideoList({
  videos,
  selectedId,
  onSelect,
  onRemove,
}: VideoListProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'processing':
        return 'bg-yellow-50 text-yellow-700 border-yellow-200';
      case 'ready':
        return 'bg-green-50 text-green-700 border-green-200';
      case 'error':
        return 'bg-red-50 text-red-700 border-red-200';
      default:
        return 'bg-gray-50 text-gray-700 border-gray-200';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'processing':
        return 'Processing...';
      case 'ready':
        return 'Ready';
      case 'error':
        return 'Error';
      default:
        return 'Unknown';
    }
  };

  return (
    <div className="space-y-2">
      {videos.map((video) => (
        <div
          key={video.id}
          onClick={() => onSelect(video)}
          className={`group cursor-pointer rounded-lg border border-border p-3 transition-all ${
            selectedId === video.id
              ? 'border-accent bg-accent/5'
              : 'hover:border-border hover:bg-secondary/50'
          }`}
        >
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1 min-w-0">
              <p className="truncate text-sm font-medium text-foreground">
                {video.name}
              </p>
              <div className="mt-2 flex items-center gap-2 text-xs text-muted-foreground">
                {video.size && (
                  <>
                    <Database className="h-3 w-3" />
                    <span>{video.size} MB</span>
                  </>
                )}
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                onRemove(video.id);
              }}
              className="h-8 w-8 p-0 opacity-0 transition-opacity group-hover:opacity-100"
            >
              <Trash2 className="h-4 w-4 text-destructive" />
            </Button>
          </div>
          <div className="mt-3 flex items-center justify-between">
            <span
              className={`inline-flex items-center rounded border px-2 py-1 text-xs font-medium ${getStatusColor(
                video.status
              )}`}
            >
              {getStatusText(video.status)}
            </span>
            <span className="text-xs text-muted-foreground">
              {video.uploadedAt}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}

'use client';

import { useState } from 'react';
import { VideoUploader } from '@/components/video-uploader';
import { ChatInterface } from '@/components/chat-interface';
import { VideoList } from '@/components/video-list';
import { Header } from '@/components/header';

export default function Home() {
  const [videos, setVideos] = useState<any[]>([]);
  const [selectedVideo, setSelectedVideo] = useState<any>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleVideoAdded = (video: any) => {
    setVideos([...videos, video]);
    setSelectedVideo(video);
  };

  const handleVideoSelect = (video: any) => {
    setSelectedVideo(video);
  };

  const handleRemoveVideo = (videoId: string) => {
    setVideos(videos.filter((v) => v.id !== videoId));
    if (selectedVideo?.id === videoId) {
      setSelectedVideo(null);
    }
  };

  return (
    <div className="flex h-screen flex-col bg-background">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar - Video Management */}
        <div className="w-full flex-1 border-r border-border md:w-96 md:flex-none">
          <div className="flex h-full flex-col">
            <div className="border-b border-border p-6">
              <h2 className="text-lg font-semibold text-foreground">Videos</h2>
              <p className="mt-1 text-sm text-muted-foreground">
                Upload or link videos to analyze
              </p>
            </div>
            <div className="flex-1 overflow-y-auto">
              <div className="p-6">
                <VideoUploader onVideoAdded={handleVideoAdded} />
              </div>
              {videos.length > 0 && (
                <div className="px-6">
                  <VideoList
                    videos={videos}
                    selectedId={selectedVideo?.id}
                    onSelect={handleVideoSelect}
                    onRemove={handleRemoveVideo}
                  />
                </div>
              )}
              {videos.length === 0 && (
                <div className="flex h-full items-center justify-center px-6 py-12">
                  <div className="text-center">
                    <p className="text-sm text-muted-foreground">
                      No videos added yet
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Section - Chat & Processing */}
        <div className="hidden flex-1 flex-col md:flex">
          {selectedVideo ? (
            <ChatInterface
              video={selectedVideo}
              isProcessing={isProcessing}
              onProcessingChange={setIsProcessing}
            />
          ) : (
            <div className="flex flex-1 items-center justify-center">
              <div className="text-center">
                <div className="mb-4 flex justify-center">
                  <div className="rounded-full bg-secondary p-4">
                    <svg
                      className="h-8 w-8 text-muted-foreground"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={1.5}
                        d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
                      />
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={1.5}
                        d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                  </div>
                </div>
                <h3 className="text-lg font-semibold text-foreground">
                  Select a video
                </h3>
                <p className="mt-2 text-sm text-muted-foreground">
                  Choose a video from the list to start analyzing
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

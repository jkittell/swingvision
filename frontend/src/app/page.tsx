'use client';

import { useState } from 'react';
import VideoUpload from '@/components/VideoUpload';
import SwingAnalysis from '@/components/SwingAnalysis';

export default function Home() {
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const handleVideoUpload = async (file: File) => {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:8000/api/v1/videos/', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to upload video');
      }

      const data = await response.json();
      setVideoUrl(data.video_url);
      console.log('Upload response:', data);
    } catch (error) {
      console.error('Error uploading video:', error);
      setUploadError('Failed to upload video. Please try again.');
    }
  };

  return (
    <div className="min-h-screen bg-black">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-center mb-8 text-gray-100">
          SwingVision
        </h1>
        <div className="max-w-4xl mx-auto">
          {uploadError && (
            <div className="bg-red-900/30 border border-red-500/50 text-red-200 px-4 py-3 rounded mb-4">
              {uploadError}
            </div>
          )}
          {!videoUrl ? (
            <VideoUpload onUpload={handleVideoUpload} />
          ) : (
            <SwingAnalysis videoUrl={videoUrl} />
          )}
        </div>
      </div>
    </div>
  );
}
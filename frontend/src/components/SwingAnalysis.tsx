'use client';

import { useEffect, useRef, useState } from 'react';

interface SwingAnalysisProps {
  videoUrl: string;
}

export default function SwingAnalysis({ videoUrl }: SwingAnalysisProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    return () => {
      if (videoUrl && videoUrl.startsWith('blob:')) {
        URL.revokeObjectURL(videoUrl);
      }
    };
  }, [videoUrl]);

  const handleError = (e: any) => {
    console.error('Video error:', e);
    setError('Failed to load video. Please try uploading again.');
  };

  return (
    <div className="space-y-4">
      <div className="relative aspect-video rounded-lg overflow-hidden bg-black">
        <video
          ref={videoRef}
          src={videoUrl}
          className="w-full h-full"
          controls
          autoPlay
          onError={handleError}
        />
      </div>
      {error && (
        <div className="bg-red-900/30 border border-red-500/50 text-red-200 px-4 py-3 rounded">
          {error}
        </div>
      )}
      <div className="text-sm text-gray-500">
        Debug info:
        <pre className="mt-2 p-2 bg-gray-900 rounded overflow-auto border border-gray-800 text-gray-400">
          {JSON.stringify({ videoUrl }, null, 2)}
        </pre>
      </div>
    </div>
  );
}
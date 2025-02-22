'use client';

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';

interface VideoUploadProps {
  onUpload: (file: File) => void;
}

export default function VideoUpload({ onUpload }: VideoUploadProps) {
  const [isDragging, setIsDragging] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file && file.type.startsWith('video/')) {
      onUpload(file);
    }
  }, [onUpload]);

  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    accept: {
      'video/*': []
    },
    maxFiles: 1
  });

  return (
    <div
      {...getRootProps()}
      className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-all duration-200 ease-in-out bg-black
        ${isDragging 
          ? 'border-blue-500/50 bg-gray-900' 
          : 'border-gray-700 hover:border-gray-600 hover:bg-gray-900'
        }`}
      onDragEnter={() => setIsDragging(true)}
      onDragLeave={() => setIsDragging(false)}
    >
      <input {...getInputProps()} />
      <div className="space-y-6">
        <div className="mx-auto w-20 h-20">
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            fill="none" 
            viewBox="0 0 24 24" 
            strokeWidth={1.5} 
            stroke="currentColor"
            className={`w-full h-full transition-colors duration-200
              ${isDragging ? 'text-blue-400' : 'text-gray-500'}`}
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5" 
            />
          </svg>
        </div>
        <div>
          <h3 className="text-xl font-semibold text-gray-200 mb-2">
            Upload Your Swing Video
          </h3>
          <p className="text-gray-400 mb-3">
            Drag and drop your video here, or click to select a file
          </p>
          <p className="text-sm text-gray-600">
            Supported formats: MP4, MOV
          </p>
        </div>
      </div>
    </div>
  );
}
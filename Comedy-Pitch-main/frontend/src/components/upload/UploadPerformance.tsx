import React from 'react';
import { FileUpload } from './FileUpload';
import { BottomNav } from './BottomNav';
import Header from '../Header';

interface UploadPerformanceProps {
  onNavigate: (destination: string, params?: { [key: string]: any }) => void;
}

const UploadPerformance: React.FC<UploadPerformanceProps> = ({ onNavigate }) => {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header title="Upload" onNavigate={onNavigate} />
      
      <main className="flex-1 container mx-auto px-4 py-6 space-y-6 pb-24">
        <FileUpload />
      </main>

      <BottomNav onNavigate={onNavigate} currentView="upload" />
    </div>
  );
};

export default UploadPerformance;

// src/components/UploadPerformance.tsx

import { Header } from './Header';
import { FileUpload } from './upload/FileUpload';
import { PerformanceForm } from './upload/PerformanceForm';
import { BottomNav } from './upload/BottomNav';

interface UploadPerformanceProps {
  onNavigate?: (destination: string, params?: { [key: string]: any }) => void;
}

export default function UploadPerformance({ onNavigate }: UploadPerformanceProps) {
  return (
    <div className="bg-white min-h-screen flex flex-col">
      <Header title="Upload" />
      <main className="flex-grow overflow-y-auto p-4 space-y-6 pb-24">
        <FileUpload />
        <PerformanceForm />
      </main>
      <BottomNav onNavigate={onNavigate} currentView="upload" />
    </div>
  );
}

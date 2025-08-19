import React, { useState, useRef } from 'react';
import { BottomNav } from "./upload/BottomNav";
import Header from "./Header";
import { FiMic } from 'react-icons/fi';
import Summary from "./Summary";

interface VoiceRecorderProps {
  onNavigate: (destination: string, params?: { [key: string]: any }) => void;
}

const VoiceRecorder: React.FC<VoiceRecorderProps> = ({ onNavigate }) => {
  const [recordingState, setRecordingState] = useState<'idle' | 'ready' | 'recording'>('idle');
  const [showSummary, setShowSummary] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        // Handle the recorded audio if needed
        console.log('Recording stopped, blob created:', audioBlob);
      };

      mediaRecorderRef.current.start();
      setRecordingState('recording');
    } catch (error) {
      console.error('Error accessing microphone:', error);
      setRecordingState('idle');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && recordingState === 'recording') {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      setShowSummary(true);
      setRecordingState('idle');
    }
  };

  const handleHeaderAction = () => {
    switch (recordingState) {
      case 'idle':
        // When play icon is clicked, start recording immediately
        startRecording();
        break;
      case 'recording':
        // When stop icon is clicked
        stopRecording();
        break;
    }
  };

  const getHeaderIcon = () => {
    switch (recordingState) {
      case 'idle':
        return (
          <svg className="w-16 h-16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M8 5v14l11-7z"/>
          </svg>
        );
      case 'recording':
        return '/assets/wave.png';
      default:
        return (
          <svg className="w-16 h-16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M8 5v14l11-7z"/>
          </svg>
        );
    }
  };

  return (
    <div className="bg-white min-h-screen flex flex-col">
      <Header 
        title="" 
        onNavigate={onNavigate} 
        customIcon={getHeaderIcon()}
        onCustomIconClick={handleHeaderAction}
        showStopOverlay={recordingState === 'recording'}
        onStopClick={stopRecording}
      />

      {/* Main Content */}
      <main className="flex-grow overflow-y-auto p-4 space-y-6 pb-24">
        {/* Profile Info Section */}
        <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-4">
              <div className="w-20 h-20 rounded-full overflow-hidden bg-gray-100">
                <img 
                  src="/assets/personpicture.png" 
                  alt="Mike Rodriguez profile"
                  className="w-full h-full object-cover"
                />
              </div>
              <div>
                <h2 className="font-display text-xl font-semibold text-gray-900">Mike Rodriguez</h2>
                <p className="font-inter text-sm text-gray-600">Comedian</p>
              </div>
            </div>
            <button 
              onClick={() => onNavigate('edit-profile')}
              className="bg-[#1d1d1d] text-white px-4 py-2 rounded-lg hover:bg-gray-900 transition-colors font-inter text-sm font-medium"
            >
              Edit Profile
            </button>
          </div>

          <p className="font-inter text-sm text-gray-700 leading-relaxed mb-6">
            Explore the world of comedy shows! Discover performances that bring laughter and joy.
            Passionate about creating content that makes people laugh and think.
          </p>

          {/* Social Icons */}
          <div className="flex items-center space-x-3 mb-6">
            <button className="w-10 h-10 bg-gray-100 hover:bg-gray-200 transition-colors rounded-full flex items-center justify-center">
              <svg className="w-5 h-5 text-gray-600" viewBox="0 0 24 24" fill="currentColor">
                <path d="M23.643 4.937c-.835.37-1.732.62-2.675.733.962-.576 1.7-1.49 2.048-2.578-.9.534-1.897.922-2.958 1.13-.85-.904-2.06-1.47-3.4-1.47-2.572 0-4.658 2.086-4.658 4.66 0 .364.042.718.12 1.06-3.873-.195-7.304-2.05-9.602-4.868-.4.69-.63 1.49-.63 2.342 0 1.616.823 3.043 2.072 3.878-.764-.025-1.482-.234-2.11-.583v.06c0 2.257 1.605 4.14 3.737 4.568-.392.106-.803.162-1.227.162-.3 0-.593-.028-.877-.082.593 1.85 2.313 3.198 4.352 3.234-1.595 1.25-3.604 1.995-5.786 1.995-.376 0-.747-.022-1.112-.065 2.062 1.323 4.51 2.093 7.14 2.093 8.57 0 13.255-7.098 13.255-13.254 0-.2-.005-.402-.014-.602.91-.658 1.7-1.477 2.323-2.41z"/>
              </svg>
            </button>
            <button className="w-10 h-10 bg-gray-100 hover:bg-gray-200 transition-colors rounded-full flex items-center justify-center">
              <svg className="w-5 h-5 text-gray-600" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
              </svg>
            </button>
            <button className="w-10 h-10 bg-gray-100 hover:bg-gray-200 transition-colors rounded-full flex items-center justify-center">
              <svg className="w-5 h-5 text-gray-600" viewBox="0 0 24 24" fill="currentColor">
                <path d="M19.615 3.184c-3.604-.246-11.631-.245-15.23 0-3.897.266-4.356 2.62-4.385 8.816.029 6.185.484 8.549 4.385 8.816 3.6.245 11.626.246 15.23 0 3.897-.266 4.356-2.62 4.385-8.816-.029-6.185-.484-8.549-4.385-8.816zm-10.615 12.816v-8l8 3.993-8 4.007z"/>
              </svg>
            </button>
          </div>

          {/* Average Score */}
          <div className="flex items-center space-x-2">
            <svg className="w-5 h-5 text-red-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M13 10V3L4 14h7v7l9-11h-7z" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            <span className="font-inter text-sm font-medium text-gray-700">
              Average Score: 3.3/5
            </span>
          </div>
        </div>

        {/* Performance Visualization */}
        <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
          <div className="rounded-lg overflow-hidden">
            <img 
              src="/assets/ownperformance.png" 
              alt="Own performance visualization"
              className="w-full h-auto"
            />
          </div>
          <button 
            onClick={() => onNavigate('dashboard')}
            className="w-full bg-[#636ae8] text-white py-3 rounded-lg font-bold text-lg mt-4"
          >
            Check my Dashboard
          </button>
        </div>



      </main>

      {/* Bottom Navigation */}
      <BottomNav onNavigate={onNavigate} currentView="voice-recorder" />

      {/* Summary Overlay */}
      {showSummary && (
        <Summary 
          onNavigate={(destination) => {
            if (destination === 'analysis') {
              onNavigate('analysis');
            } else if (destination === 'voice-recorder') {
              setShowSummary(false);
            }
          }} 
        />
      )}
    </div>
  );
};

export default VoiceRecorder;
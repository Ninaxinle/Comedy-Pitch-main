import React, { ReactElement } from 'react';
import { FiMic } from 'react-icons/fi';

interface HeaderProps {
  title: string;
  onNavigate: (destination: string, params?: { [key: string]: any }) => void;
  customIcon?: string | ReactElement;
  onCustomIconClick?: () => void;
  showStopOverlay?: boolean;
  onStopClick?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ 
  title, 
  onNavigate, 
  customIcon, 
  onCustomIconClick,
  showStopOverlay,
  onStopClick
}) => {
  return (
    <header className="bg-black sticky top-0 z-50 relative overflow-hidden">
      {showStopOverlay && (
        <div className="absolute inset-0 z-20">
          <img 
            src="/assets/wave.png" 
            alt="Recording waveform"
            className="w-full h-full object-cover"
          />
          <button
            onClick={onStopClick}
            className="absolute inset-0 flex items-center justify-center"
          >
            <img 
              src="/assets/stop.png" 
              alt="Stop recording"
              className="w-12 h-12 opacity-70 hover:opacity-100 transition-opacity"
            />
          </button>
        </div>
      )}
      <div className="container mx-auto px-4 py-8 flex items-center justify-between relative z-10">
        {title ? (
          <>
            <div className="w-10"></div>
            <h1 className="font-display text-xl font-semibold text-white absolute left-1/2 transform -translate-x-1/2">
              {title}
            </h1>
            <div className="flex items-center">
              {customIcon ? (
                <button 
                  onClick={onCustomIconClick}
                  className="relative text-white hover:text-gray-300 transition-colors p-2 rounded-lg hover:bg-gray-800"
                  aria-label="Custom Action"
                >
                  {typeof customIcon === 'string' ? (
                    <img 
                      src={customIcon} 
                      alt="Action icon"
                      className="w-6 h-6 object-contain"
                    />
                  ) : (
                    customIcon
                  )}
                </button>
              ) : (
                <button 
                  onClick={() => onNavigate('voice-recorder')}
                  className="text-white hover:text-gray-300 transition-colors p-2 rounded-lg hover:bg-gray-800"
                  aria-label="Open Voice Recorder"
                >
                  <FiMic className="h-6 w-6" />
                </button>
              )}
            </div>
          </>
        ) : (
          <div className="w-full flex items-center justify-center">
            {customIcon && (
              <button 
                onClick={onCustomIconClick}
                className="relative text-white hover:text-gray-300 transition-colors p-2 rounded-lg hover:bg-gray-800"
                aria-label="Custom Action"
              >
                {typeof customIcon === 'string' ? (
                  <img 
                    src={customIcon} 
                    alt="Action icon"
                    className="w-6 h-6 object-contain"
                  />
                ) : (
                  customIcon
                )}
              </button>
            )}
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
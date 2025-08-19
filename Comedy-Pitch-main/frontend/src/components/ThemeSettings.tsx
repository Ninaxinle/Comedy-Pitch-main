import React, { useState } from 'react';
import { FiChevronLeft } from 'react-icons/fi';
import { BottomNav } from './upload/BottomNav';

interface ThemeSettingsProps {
  onNavigate: (destination: string, params?: { [key: string]: any }) => void;
}

type ThemeMode = 'light' | 'dark' | 'auto' | 'high-contrast';

interface ToggleSwitchProps {
  isOn: boolean;
  onToggle: () => void;
  disabled?: boolean;
}

const ToggleSwitch: React.FC<ToggleSwitchProps> = ({ isOn, onToggle, disabled = false }) => {
  return (
    <button
      onClick={onToggle}
      disabled={disabled}
      className={`relative w-10 h-5 rounded-full border transition-all duration-200 ${
        isOn 
          ? 'bg-blue-500 border-blue-500' 
          : 'bg-white border-gray-300'
      } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
    >
      <div
        className={`absolute w-4 h-4 bg-white rounded-full top-0.5 transition-transform duration-200 ${
          isOn ? 'transform translate-x-5' : 'transform translate-x-0.5'
        }`}
      />
    </button>
  );
};

interface ThemeOptionProps {
  title: string;
  isSelected: boolean;
  onSelect: () => void;
}

const ThemeOption: React.FC<ThemeOptionProps> = ({ title, isSelected, onSelect }) => {
  return (
    <div className="flex items-center justify-between py-4 px-4 hover:bg-gray-50 transition-colors">
      <span className="text-lg font-semibold text-gray-900">{title}</span>
      <ToggleSwitch 
        isOn={isSelected} 
        onToggle={onSelect}
      />
    </div>
  );
};

const ThemeSettings: React.FC<ThemeSettingsProps> = ({ onNavigate }) => {
  const [selectedTheme, setSelectedTheme] = useState<ThemeMode>('light');

  const themeOptions = [
    { id: 'light' as ThemeMode, title: 'Light Mode' },
    { id: 'dark' as ThemeMode, title: 'Dark Mode' },
    { id: 'auto' as ThemeMode, title: 'Auto Mode' },
    { id: 'high-contrast' as ThemeMode, title: 'High Contrast Mode' },
  ];

  const handleThemeChange = (themeId: ThemeMode) => {
    setSelectedTheme(themeId);
    // Here you would typically apply the theme change
    console.log('Theme changed to:', themeId);
    
    // You could also save to localStorage or context
    localStorage.setItem('app-theme', themeId);
  };

  return (
    <div className="bg-white min-h-screen flex flex-col">
      {/* Header - matching Profile page style */}
      <header className="bg-gradient-to-br from-gray-800 via-gray-900 to-black backdrop-blur-sm sticky top-0 z-50 border-b border-gray-700 relative overflow-hidden">
        {/* Red Spotlight Effect */}
        <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-40 h-40 bg-gradient-to-b from-red-500/30 to-transparent rounded-full blur-xl"></div>
        
        <div className="container mx-auto px-4 py-8 flex items-center justify-between relative z-10">
          <button 
            className="text-gray-400 hover:text-white transition-colors p-2 rounded-lg hover:bg-gray-800"
            onClick={() => onNavigate('settings')}
          >
            <FiChevronLeft className="w-6 h-6" />
          </button>
          
          <h1 className="font-display text-xl font-semibold text-white absolute left-1/2 transform -translate-x-1/2">Theme</h1>
          
          <div className="w-10"></div>
        </div>
      </header>

      {/* Content */}
      <main className="flex-grow overflow-y-auto p-4 space-y-6 pb-24">
        {/* Theme Options */}
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm">
          {themeOptions.map((option, index) => (
            <div key={option.id}>
              <ThemeOption
                title={option.title}
                isSelected={selectedTheme === option.id}
                onSelect={() => handleThemeChange(option.id)}
              />
              {index < themeOptions.length - 1 && (
                <div className="border-b border-gray-200 mx-2.5" />
              )}
            </div>
          ))}
        </div>

        {/* Theme Preview or Description */}
        <div className="mt-8 p-4 bg-gray-50 rounded-lg">
          <h3 className="text-lg font-semibold text-gray-800 mb-2">
            Current Theme: {themeOptions.find(t => t.id === selectedTheme)?.title}
          </h3>
          <p className="text-gray-600 text-sm">
            {selectedTheme === 'light' && 'Clean and bright interface with light backgrounds.'}
            {selectedTheme === 'dark' && 'Easy on the eyes with dark backgrounds and light text.'}
            {selectedTheme === 'auto' && 'Automatically switches between light and dark based on system settings.'}
            {selectedTheme === 'high-contrast' && 'Enhanced contrast for better accessibility and readability.'}
          </p>
        </div>
      </main>

      {/* Bottom Navigation */}
      <BottomNav onNavigate={onNavigate} currentView="settings" />
    </div>
  );
};

export default ThemeSettings;
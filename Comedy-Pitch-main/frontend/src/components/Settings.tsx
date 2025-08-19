import React from 'react';
import { BottomNav } from './upload/BottomNav';
import Header from './Header';

interface SettingsProps {
  onNavigate: (destination: string, params?: { [key: string]: any }) => void;
}

// Icon components for better maintainability
const ThemeIcon = () => (
  <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
    <div className="w-3 h-3 bg-white rounded-full transform translate-x-1"></div>
  </div>
);

const FontSizeIcon = () => (
  <div className="w-6 h-6 flex items-center justify-center">
    <span className="text-blue-500 font-bold text-lg">Aa</span>
  </div>
);

const AccessibilityIcon = () => (
  <div className="w-6 h-6 text-blue-500">
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2a2 2 0 0 1 2 2 2 2 0 0 1-2 2 2 2 0 0 1-2-2 2 2 0 0 1 2-2m9 7h-6v2h6v-2m-6 2.5c-.8.8-2.1.8-2.9 0l-1.1-1c-.3-.4-.7-.7-1.2-.7-.6 0-1.1.3-1.4.8L7 12.5v5.5c0 .6-.4 1-1 1s-1-.4-1-1v-7c0-.6.4-1 1-1 .3 0 .5.1.7.3l1.4 1.4c.5.5 1.1.8 1.7.8.7 0 1.3-.3 1.8-.8l1.1-1.1c.8-.8 2.1-.8 2.9 0L21 11v7c0 .6-.4 1-1 1s-1-.4-1-1v-5.5l-1.4-1z"/>
    </svg>
  </div>
);

const LanguageIcon = () => (
  <div className="w-6 h-6 text-blue-500">
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M12.87 15.07l-2.54-2.51.03-.03A17.52 17.52 0 0 0 14.07 6H17V4h-7V2H8v2H1v2h11.17C11.5 7.92 10.44 9.75 9 11.35 8.07 10.32 7.3 9.19 6.69 8h-2c.73 1.63 1.73 3.17 2.98 4.56l-5.09 5.02L4 19l5-5 3.11 3.11.76-2.04zM18.5 10h-2L12 22h2l1.12-3h4.75L21 22h2l-4.5-12zm-2.62 7l1.62-4.33L19.12 17h-3.24z"/>
    </svg>
  </div>
);

const SecurityIcon = () => (
  <div className="w-6 h-6 text-blue-500">
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M12,1L3,5V11C3,16.55 6.84,21.74 12,23C17.16,21.74 21,16.55 21,11V5L12,1M12,7C13.4,7 14.8,8.6 14.8,10V11H16V18H8V11H9.2V10C9.2,8.6 10.6,7 12,7M12,8.2C11.2,8.2 10.4,8.7 10.4,10V11H13.6V10C13.6,8.7 12.8,8.2 12,8.2Z"/>
    </svg>
  </div>
);

const PrivacyIcon = () => (
  <div className="w-6 h-6 text-blue-500">
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M12,1L3,5V11C3,16.55 6.84,21.74 12,23C17.16,21.74 21,16.55 21,11V5L12,1M11,7H13V9H11V7M11,11H13V17H11V11Z"/>
    </svg>
  </div>
);

const NotificationIcon = () => (
  <div className="w-6 h-6 text-blue-500">
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M10 21h4c0 1.1-.9 2-2 2s-2-.9-2-2zm11-2v1H3v-1l2-2V9c0-3.3 2.7-6 6-6s6 2.7 6 6v9l2 2z"/>
    </svg>
  </div>
);

const ControlIcon = () => (
  <div className="w-6 h-6 text-blue-500">
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4M10.5,8.5L12,7L13.5,8.5L12,10L10.5,8.5M10.5,15.5L12,14L13.5,15.5L12,17L10.5,15.5Z"/>
    </svg>
  </div>
);

interface SettingItemProps {
  icon: React.ReactNode;
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
  onClick?: () => void;
}

const SettingItem: React.FC<SettingItemProps> = ({ 
  icon, 
  title, 
  subtitle, 
  action, 
  onClick 
}) => (
  <div 
    className="flex items-center justify-between py-4 px-4 cursor-pointer hover:bg-gray-50 transition-colors"
    onClick={onClick}
  >
    <div className="flex items-center space-x-4">
      {icon}
      <div>
        <h3 className="font-semibold text-gray-900 text-lg">{title}</h3>
        {subtitle && (
          <p className="text-gray-600 text-sm">{subtitle}</p>
        )}
      </div>
    </div>
    {action}
  </div>
);

interface SectionProps {
  title: string;
  children: React.ReactNode;
}

const Section: React.FC<SectionProps> = ({ title, children }) => (
  <div className="mb-8">
    <h2 className="text-gray-500 font-bold text-lg mb-4">{title}</h2>
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm divide-y divide-gray-200">
      {children}
    </div>
  </div>
);

const LinkButton: React.FC<{ linked?: boolean; onClick?: () => void }> = ({ 
  linked = false, 
  onClick 
}) => (
  <button
    onClick={onClick}
    className={`px-4 py-1 rounded-full text-sm font-semibold transition-colors ${
      linked 
        ? 'bg-blue-100 text-blue-600' 
        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
    }`}
  >
    {linked ? 'Linked' : 'Link Account'}
  </button>
);

const Settings: React.FC<SettingsProps> = ({ onNavigate }) => {
  return (
    <div className="bg-white min-h-screen flex flex-col">
      <Header title="Settings" onNavigate={onNavigate} />

      {/* Content */}
      <main className="flex-grow overflow-y-auto p-4 space-y-6 pb-24">
        {/* Interface Preferences */}
        <Section title="Interface Preferences">
          <SettingItem
            icon={<ThemeIcon />}
            title="Theme"
            subtitle="Light Mode"
            onClick={() => onNavigate('theme-settings')}
          />
          <SettingItem
            icon={<FontSizeIcon />}
            title="Font Size"
            subtitle="Medium"
            onClick={() => console.log('Font Size clicked')}
          />
          <SettingItem
            icon={<AccessibilityIcon />}
            title="Accessibility"
            onClick={() => console.log('Accessibility clicked')}
          />
          <SettingItem
            icon={<LanguageIcon />}
            title="Language & Locale"
            subtitle="English"
            onClick={() => console.log('Language clicked')}
          />
        </Section>

        {/* Account Setting */}
        <Section title="Account Setting">
          <SettingItem
            icon={<SecurityIcon />}
            title="Account Security"
            onClick={() => console.log('Account Security clicked')}
          />
          <SettingItem
            icon={<PrivacyIcon />}
            title="Privacy Setting"
            onClick={() => console.log('Privacy Setting clicked')}
          />
          <SettingItem
            icon={<NotificationIcon />}
            title="Notifications"
            onClick={() => console.log('Notifications clicked')}
          />
          <SettingItem
            icon={<ControlIcon />}
            title="Account Control"
            onClick={() => console.log('Account Control clicked')}
          />
        </Section>

        {/* Social Accounts */}
        <Section title="Social Accounts">
          <SettingItem
            icon={
              <div className="w-6 h-6 bg-gradient-to-br from-purple-600 via-pink-600 to-orange-600 rounded-lg flex items-center justify-center">
                <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                </svg>
              </div>
            }
            title="Instagram"
            action={<LinkButton linked={true} onClick={() => console.log('Instagram clicked')} />}
          />
          <SettingItem
            icon={
              <div className="w-6 h-6 bg-blue-600 rounded-lg flex items-center justify-center">
                <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                </svg>
              </div>
            }
            title="Facebook"
            action={<LinkButton onClick={() => console.log('Facebook clicked')} />}
          />
          <SettingItem
            icon={
              <div className="w-6 h-6 bg-black rounded-lg flex items-center justify-center">
                <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/>
                </svg>
              </div>
            }
            title="TikTok"
            action={<LinkButton onClick={() => console.log('TikTok clicked')} />}
          />
        </Section>
      </main>

      {/* Bottom Navigation */}
      <BottomNav onNavigate={onNavigate} currentView="settings" />
    </div>
  );
};

export default Settings;
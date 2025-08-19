// src/components/upload/BottomNav.tsx
import React from 'react';
import { 
  FiHome, 
  FiPlus, 
  FiUsers, 
  FiSettings,
  FiGrid
} from 'react-icons/fi';

const NavButton = ({ onClick, icon: Icon, isActive, disabled = false }: { onClick: () => void, icon: React.ComponentType<{ className?: string }>, isActive: boolean, disabled?: boolean }) => (
  <button
    onClick={onClick}
    disabled={disabled}
    className={`flex items-center justify-center p-4 rounded-full transition-all duration-200 ${
      disabled
        ? 'text-gray-400 cursor-not-allowed opacity-50'
        : isActive 
          ? 'bg-gradient-to-r from-red-500 to-red-600 text-white shadow-lg' 
          : 'text-gray-300 hover:bg-gray-700 hover:text-white'
    }`}
  >
    <Icon className={`w-5 h-5 ${disabled ? 'text-gray-400' : isActive ? 'text-white' : 'text-gray-300'}`} />
  </button>
);

export const BottomNav = ({ onNavigate, currentView = 'upload' }: { onNavigate?: (destination: string, params?: { [key: string]: any }) => void, currentView?: string }) => {
  const [activeTab, setActiveTab] = React.useState(currentView);

  // Update active tab when currentView changes
  React.useEffect(() => {
    setActiveTab(currentView);
  }, [currentView]);

  const navItems = [
    { name: 'home', dest: 'profile', icon: FiHome, disabled: false },
    { name: 'add', dest: 'upload', icon: FiPlus, disabled: false },
    { name: 'community', dest: 'community', icon: FiUsers, disabled: false },
    { name: 'groups', dest: 'groups', icon: FiGrid, disabled: false },
    { name: 'settings', dest: 'settings', icon: FiSettings, disabled: false },
  ];

  const handleNavigate = (dest: string, disabled: boolean) => {
    if (disabled) {
      // Do nothing for disabled buttons
      return;
    }
    setActiveTab(dest);
    onNavigate?.(dest);
  };

  return (
    <nav className="fixed bottom-4 left-1/2 transform -translate-x-1/2 bg-gray-900 z-50 rounded-full shadow-lg border border-gray-700">
      <div className="px-1 py-1 flex items-center space-x-6

      ">
        {navItems.map(item => (
          <NavButton
            key={item.name}
            onClick={() => handleNavigate(item.dest, item.disabled)}
            icon={item.icon}
            isActive={activeTab === item.dest}
            disabled={item.disabled}
          />
        ))}
      </div>
    </nav>
  );
};

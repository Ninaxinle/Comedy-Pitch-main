// src/components/upload/Header.tsx

import { FiMenu } from 'react-icons/fi';

export const Header = () => {
  return (
    <header className="bg-gradient-to-br from-gray-800 via-gray-900 to-black backdrop-blur-sm sticky top-0 z-50 border-b border-gray-700 relative overflow-hidden">
      {/* Red Spotlight Effect */}
      <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-40 h-40 bg-gradient-to-b from-red-500/30 to-transparent rounded-full blur-xl"></div>
      
              <div className="container mx-auto px-4 py-8 flex items-center justify-between relative z-10">
          <div className="w-10"></div>
          <h1 className="font-display text-xl font-semibold text-white absolute left-1/2 transform -translate-x-1/2">
            Upload
          </h1>
          <button className="text-gray-400 hover:text-white transition-colors p-2 rounded-lg hover:bg-gray-800">
            <FiMenu className="h-6 w-6" />
          </button>
        </div>
    </header>
  );
};

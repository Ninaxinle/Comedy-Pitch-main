// src/components/upload/FileUpload.tsx

import { 
  FiImage, 
  FiFile, 
  FiCheck 
} from 'react-icons/fi';

export const FileUpload = () => {
  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
      <h2 className="font-display text-lg font-semibold text-gray-900 mb-2">Performance File</h2>
      <p className="font-inter text-sm text-gray-600 mb-6 font-normal">
        Upload your video or audio file to get started.
      </p>
      
      {/* Light Upload Area */}
      <div className="space-y-3">
        {/* Gallery Upload Option */}
        <button className="w-full bg-gray-50 text-gray-700 rounded-lg p-4 flex items-center justify-center space-x-3 hover:bg-red-50 hover:border-red-300 transition-all duration-200 transform hover:scale-[1.01] active:scale-[0.99] border border-gray-200 shadow-sm group">
          <FiImage className="w-5 h-5 group-hover:text-red-600 transition-colors" />
          <span className="font-inter font-medium group-hover:text-red-700 transition-colors">Choose from Gallery</span>
        </button>

        {/* File Upload Option */}
        <button className="w-full bg-gray-50 text-gray-700 rounded-lg p-4 flex items-center justify-center space-x-3 hover:bg-red-50 hover:border-red-300 transition-all duration-200 transform hover:scale-[1.01] active:scale-[0.99] border border-gray-200 shadow-sm group">
          <FiFile className="w-5 h-5 group-hover:text-red-600 transition-colors" />
          <span className="font-inter font-medium group-hover:text-red-700 transition-colors">Browse Files</span>
        </button>
      </div>

      {/* Upload Progress (Hidden by default, shown when uploading) */}
      <div className="mt-6 hidden">
        <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
          <span className="font-inter">Uploading...</span>
          <span className="font-inter">75%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div className="bg-gradient-to-r from-red-500 to-red-600 h-2 rounded-full" style={{ width: '75%' }}></div>
        </div>
      </div>

      {/* File Info (Hidden by default, shown when file is selected) */}
      <div className="mt-4 hidden">
        <div className="bg-green-50 border border-green-200 rounded-lg p-3 flex items-center space-x-3">
          <FiCheck className="w-5 h-5 text-green-600" />
          <div className="flex-1">
            <p className="font-inter text-sm font-medium text-green-800">performance_video.mp4</p>
            <p className="font-inter text-xs text-green-600">15.2 MB • Ready to upload</p>
          </div>
        </div>
      </div>
    </div>
  );
};

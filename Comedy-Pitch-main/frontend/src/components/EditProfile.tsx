import React, { useState } from 'react';
import { FiChevronDown, FiChevronLeft, FiMenu } from 'react-icons/fi';
import { BottomNav } from './upload/BottomNav';

interface EditProfileProps {
  onNavigate: (destination: string, params?: { [key: string]: any }) => void;
}

const EditProfile: React.FC<EditProfileProps> = ({ onNavigate }) => {
  const [formData, setFormData] = useState({
    fullName: '',
    phoneNumber: '',
    gender: '',
    emailAddress: ''
  });

  const [isGenderDropdownOpen, setIsGenderDropdownOpen] = useState(false);

  const genderOptions = [
    { value: '', label: 'Select Gender' },
    { value: 'male', label: 'Male' },
    { value: 'female', label: 'Female' },
    { value: 'other', label: 'Other' },
    { value: 'prefer-not-to-say', label: 'Prefer not to say' }
  ];

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSaveChanges = () => {
    // Here you would typically save the profile data
    console.log('Saving profile changes:', formData);
    // Navigate back to profile or show success message
    onNavigate('profile');
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
            onClick={() => onNavigate('profile')}
          >
            <FiChevronLeft className="w-6 h-6" />
          </button>
          
          <h1 className="font-display text-xl font-semibold text-white absolute left-1/2 transform -translate-x-1/2">Edit Profile</h1>
          
          <button className="text-gray-400 hover:text-white transition-colors p-2 rounded-lg hover:bg-gray-800">
            <FiMenu className="w-6 h-6" />
          </button>
        </div>
      </header>

      {/* Content */}
      <main className="flex-grow overflow-y-auto p-4 space-y-6 pb-24">
        {/* Profile Image */}
        <div className="flex justify-center mb-8">
          <div className="w-28 h-28 rounded-full overflow-hidden bg-gray-200">
            <img 
              src="/assets/9decd998351cfde9c45fc40451723b54283aa78c.png" 
              alt="Profile"
              className="w-full h-full object-cover"
              onError={(e) => {
                // Fallback to placeholder if image fails to load
                e.currentTarget.style.display = 'none';
                e.currentTarget.nextElementSibling?.classList.remove('hidden');
              }}
            />
            <div className="hidden w-full h-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
              <span className="text-white text-2xl font-bold">P</span>
            </div>
          </div>
        </div>

        {/* Form Fields */}
        <div className="space-y-6">
          {/* Full Name */}
          <div>
            <label className="block text-gray-500 text-lg mb-2">
              Full Name
            </label>
            <input
              type="text"
              value={formData.fullName}
              onChange={(e) => handleInputChange('fullName', e.target.value)}
              className="w-full px-4 py-4 border border-gray-400 rounded-3xl focus:outline-none focus:border-blue-500 transition-colors text-lg"
              placeholder="Enter your full name"
            />
          </div>

          {/* Phone Number */}
          <div>
            <label className="block text-gray-500 text-lg mb-2">
              Phone Number
            </label>
            <input
              type="tel"
              value={formData.phoneNumber}
              onChange={(e) => handleInputChange('phoneNumber', e.target.value)}
              className="w-full px-4 py-4 border border-gray-400 rounded-3xl focus:outline-none focus:border-blue-500 transition-colors text-lg"
              placeholder="Enter your phone number"
            />
          </div>

          {/* Gender */}
          <div className="relative">
            <label className="block text-gray-500 text-lg mb-2">
              Gender
            </label>
            <div className="relative">
              <button
                type="button"
                onClick={() => setIsGenderDropdownOpen(!isGenderDropdownOpen)}
                className="w-full px-4 py-4 border border-gray-400 rounded-3xl focus:outline-none focus:border-blue-500 transition-colors text-lg text-left bg-white flex items-center justify-between"
              >
                <span className={formData.gender ? 'text-black' : 'text-gray-400'}>
                  {formData.gender 
                    ? genderOptions.find(opt => opt.value === formData.gender)?.label 
                    : 'Select Gender'
                  }
                </span>
                <FiChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${
                  isGenderDropdownOpen ? 'rotate-180' : ''
                }`} />
              </button>
              
              {isGenderDropdownOpen && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-300 rounded-2xl shadow-lg z-10 overflow-hidden">
                  {genderOptions.map((option) => (
                    <button
                      key={option.value}
                      type="button"
                      onClick={() => {
                        handleInputChange('gender', option.value);
                        setIsGenderDropdownOpen(false);
                      }}
                      className="w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors text-lg"
                    >
                      {option.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Email Address */}
          <div>
            <label className="block text-gray-500 text-lg mb-2">
              Email Address
            </label>
            <input
              type="email"
              value={formData.emailAddress}
              onChange={(e) => handleInputChange('emailAddress', e.target.value)}
              className="w-full px-4 py-4 border border-gray-400 rounded-3xl focus:outline-none focus:border-blue-500 transition-colors text-lg"
              placeholder="Enter your email address"
            />
          </div>
        </div>

        {/* Save Changes Button */}
        <div className="mt-12 flex justify-center">
          <button
            onClick={handleSaveChanges}
            className="bg-indigo-600 text-white px-12 py-4 rounded-3xl text-xl font-bold hover:bg-indigo-700 transition-colors shadow-lg"
          >
            Save Changes
          </button>
        </div>
      </main>

      {/* Bottom Navigation */}
      <BottomNav onNavigate={onNavigate} currentView="profile" />
    </div>
  );
};

export default EditProfile;
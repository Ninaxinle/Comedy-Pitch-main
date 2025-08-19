// src/components/upload/PerformanceForm.tsx
import React, { useState } from 'react';

const FormInput = ({ id, value, onChange, placeholder }: { id: string, value: string, onChange: (e: React.ChangeEvent<HTMLInputElement>) => void, placeholder: string }) => (
  <input
    id={id}
    type="text"
    value={value}
    onChange={onChange}
    placeholder={placeholder}
    className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500 transition-all font-inter text-gray-900 placeholder-gray-400"
  />
);

const FormTextarea = ({ id, value, onChange, placeholder }: { id: string, value: string, onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void, placeholder: string }) => (
  <textarea
    id={id}
    value={value}
    onChange={onChange}
    placeholder={placeholder}
    className="w-full px-4 py-3 h-32 bg-white border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500 transition-all font-inter text-gray-900 placeholder-gray-400"
  />
);

export const PerformanceForm = () => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');

  return (
    <div className="bg-white rounded-xl p-6 border border-gray-200">
      <h2 className="font-display text-lg font-semibold text-gray-900 mb-2">Performance Details</h2>
      <p className="font-inter text-sm text-gray-600 mb-6">
        Add title and description to your performance.
      </p>
      <div className="space-y-6">
        <div>
          <label htmlFor="title" className="block text-sm font-semibold text-gray-700 mb-2 font-inter">Title</label>
          <FormInput
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g., An Evening of Hilarity"
          />
        </div>
        <div>
          <label htmlFor="description" className="block text-sm font-semibold text-gray-700 mb-2 font-inter">Description</label>
          <FormTextarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="A bit about your act..."
          />
        </div>
      </div>
      <button className="w-full mt-8 bg-gradient-to-r from-red-500 to-red-600 text-white py-3.5 rounded-lg text-md font-semibold hover:from-red-600 hover:to-red-700 focus:outline-none focus:ring-4 focus:ring-red-300 transition-all duration-300 transform hover:scale-105 font-inter shadow-sm">
        Submit Performance
      </button>
    </div>
  );
};

// components/LoadingScreen.jsx
import React from 'react';
import { Loader } from 'lucide-react';

export default function LoadingScreen({ message = 'Loading...' }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
      <div className="text-center">
        <div className="mb-8 flex justify-center">
          <div className="relative w-24 h-24">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-blue-700 rounded-full opacity-20 blur-xl animate-pulse"></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <Loader className="text-blue-600 animate-spin" size={48} />
            </div>
          </div>
        </div>
        <h1 className="text-3xl font-bold text-white mb-4">{message}</h1>
        <p className="text-slate-400 text-sm">This may take a few moments</p>
      </div>
    </div>
  );
}
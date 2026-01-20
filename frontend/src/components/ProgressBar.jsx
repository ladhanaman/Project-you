// components/ProgressBar.jsx
import React from 'react';

export default function ProgressBar({ completed, total, section }) {
  const percentage = (completed / total) * 100;

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-slate-800 capitalize">
          {section} Assessment
        </h3>
        <span className="text-sm font-semibold text-blue-600">
          {completed}/{total} completed
        </span>
      </div>
      <div className="w-full bg-slate-200 rounded-full h-3 overflow-hidden">
        <div
          className="bg-gradient-to-r from-blue-600 to-blue-700 h-full rounded-full transition-all duration-500"
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
    </div>
  );
}
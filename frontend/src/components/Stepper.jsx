// components/Stepper.jsx
import React from 'react';

export default function Stepper({ currentSection }) {
  const sections = [
    { id: 'fundamentals', label: 'Fundamentals' },
    { id: 'applied', label: 'Applied' },
    { id: 'industry', label: 'Industry' },
  ];

  // Helper function to check if a step is completed
  const isCompleted = (index) => {
    const currentIndex = sections.findIndex(s => s.id === currentSection);
    return index < currentIndex;
  };

  return (
    <div className="flex items-center justify-between mb-2">
      {sections.map((step, i) => (
        <React.Fragment key={step.id}>
          {/* Step Circle & Label */}
          <div className="flex flex-col items-center">
            <div
              className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-sm transition-colors ${step.id === currentSection
                  ? 'bg-blue-600 text-white'
                  : isCompleted(i)
                    ? 'bg-green-600 text-white'
                    : 'bg-slate-200 text-slate-500'
                }`}
            >
              {isCompleted(i) ? (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              ) : (
                i + 1
              )}
            </div>
            <p className={`text-sm font-medium mt-2 ${step.id === currentSection ? 'text-blue-600' : 'text-slate-600'
              }`}>
              {step.label}
            </p>
          </div>

          {/* Connector Line */}
          {i < sections.length - 1 && (
            <div className="flex-1 mx-4 mb-8">
              <div
                className={`h-1 rounded-full transition-colors ${isCompleted(i) ? 'bg-green-600' : 'bg-slate-200'
                  }`}
              />
            </div>
          )}
        </React.Fragment>
      ))}
    </div>
  );
}
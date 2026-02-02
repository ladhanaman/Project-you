// src/components/JourneyProgressCard.jsx
import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function JourneyProgressCard({ journeyData, progressPercentage }) {
    const navigate = useNavigate();

    // Calculate completed days count
    const completedCount = Object.values(journeyData?.days || {}).filter(d => d.completed).length;

    return (
        <div className="glass-panel p-4 sm:p-5 h-full flex flex-col relative overflow-hidden group glass-card-hover">
            {/* Hover Shine - One way animation only (resets instantly when not hovering) */}
            <div className="absolute inset-0 bg-gradient-to-tr from-transparent via-white/40 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-0 group-hover:duration-1000 ease-in-out pointer-events-none z-20" />

            {/* Header with Progress */}
            <div className="flex items-center justify-between mb-8 relative z-10 animate-slide-up-fade" style={{ animationDelay: '0.1s' }}>
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-gradient-to-br from-purple-100/80 to-indigo-100/80 rounded-xl shadow-inner border border-white/50">
                        <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                        </svg>
                    </div>
                    <h3 className="text-lg font-bold text-gray-900">Journey Progress</h3>
                </div>
                <div className="text-right">
                    <div className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                        {Math.round(progressPercentage)}%
                    </div>
                    <p className="text-[10px] sm:text-xs text-gray-500 mt-0.5">
                        {completedCount} of 7 days
                    </p>
                </div>
            </div>

            {/* Timeline with Connected Dots */}
            <div className="mb-4 sm:mb-5 animate-slide-up-fade" style={{ animationDelay: '0.2s' }}>
                <div className="relative px-1 sm:px-2">
                    <div className="flex items-start justify-between">
                        {[1, 2, 3, 4, 5, 6, 7].map((day, index) => {
                            const dayInfo = journeyData?.days?.[day.toString()];
                            const isCompleted = dayInfo?.completed || false;
                            const currentDay = journeyData?.current_day || 1;
                            const isCurrent = currentDay === day;
                            const isLocked = day > currentDay;
                            const isMilestone = day === 7;

                            return (
                                <div key={day} className="flex flex-col items-center relative flex-1">
                                    {/* Connecting Line */}
                                    {index > 0 && (
                                        <div
                                            className={`
                                                absolute top-[15px] right-1/2 h-[2px] transition-all duration-500 z-0
                                                ${isCompleted || (isCurrent && index > 0)
                                                    ? 'bg-gradient-to-r from-green-500 to-purple-600'
                                                    : 'bg-gray-200'
                                                }
                                            `}
                                            style={{
                                                width: 'calc(100% - 20px)',
                                                left: 'calc(-50% + 10px)'
                                            }}
                                        />
                                    )}

                                    {/* Day Dot/Icon */}
                                    <div className="relative z-10 mb-1 sm:mb-2 transition-transform duration-300 hover:scale-110">
                                        {isMilestone ? (
                                            <div className={`
                                                w-8 h-8 rounded-full flex items-center justify-center transition-all duration-300
                                                ${isCompleted
                                                    ? 'bg-gradient-to-br from-yellow-400 to-orange-500 shadow-lg scale-110'
                                                    : 'bg-gray-200 border-2 border-gray-300'
                                                }
                                            `}>
                                                <svg className={`w-4 h-4 sm:w-5 sm:h-5 ${isCompleted ? 'text-white' : 'text-gray-400'}`} fill="currentColor" viewBox="0 0 20 20">
                                                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                                                </svg>
                                            </div>
                                        ) : (
                                            <div className={`
                                                w-8 h-8 rounded-full flex items-center justify-center transition-all duration-300 border-[3px]
                                                ${isCompleted
                                                    ? 'bg-green-500 border-green-500 shadow-md'
                                                    : isCurrent
                                                        ? 'bg-white border-purple-600 shadow-lg ring-4 ring-purple-100 scale-110'
                                                        : 'bg-white border-gray-300'
                                                }
                                                ${isCurrent ? 'animate-pulse' : ''}
                                            `}>
                                                {isCompleted ? (
                                                    <svg className="w-4 h-4 sm:w-5 sm:h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                                                    </svg>
                                                ) : isCurrent ? (
                                                    <div className="w-2.5 h-2.5 sm:w-3 sm:h-3 rounded-full bg-gradient-to-br from-indigo-600 to-purple-600" />
                                                ) : (
                                                    <div className="w-2.5 h-2.5 sm:w-3 sm:h-3 rounded-full bg-gray-300" />
                                                )}
                                            </div>
                                        )}
                                    </div>

                                    {/* Day Label */}
                                    <div className="text-center">
                                        <p className={`
                                            text-[10px] sm:text-xs font-bold leading-tight
                                            ${isCompleted ? 'text-green-600' : isCurrent ? 'text-purple-600' : 'text-gray-400'}
                                        `}>
                                            {day}
                                        </p>
                                        <p className="text-[8px] sm:text-[9px] text-gray-500 mt-0.5 hidden sm:block">
                                            {isCompleted ? '✓' : isCurrent ? 'Now' : isMilestone ? '★' : ''}
                                        </p>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>


            {/* Completion Celebration */}
            {completedCount === 7 && (
                <div className="text-center p-3 sm:p-4 bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl border-2 border-green-200 animate-slide-up-fade" style={{ animationDelay: '0.3s' }}>
                    <div className="text-3xl sm:text-4xl mb-2">🎉</div>
                    <p className="font-bold text-green-900 text-base sm:text-lg">Journey Complete!</p>
                    <p className="text-xs sm:text-sm text-green-700 mt-1">You've finished all 7 days</p>
                </div>
            )}
        </div>
    );
}

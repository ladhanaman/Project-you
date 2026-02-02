import React, { useState, useEffect } from 'react';
import { Lock, CheckCircle, Clock, Calendar, Sparkles } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { getDailyReflections } from '../services/apiService.js';

const ReflectionJourney = ({ session }) => {
    const navigate = useNavigate();
    const [userProgress, setUserProgress] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    // Fetch user's progress on mount
    useEffect(() => {
        const fetchProgress = async () => {
            try {
                setIsLoading(true);
                const history = await getDailyReflections();
                setUserProgress(history || []);
            } catch (err) {
                // Silently fail - user just won't have progress data
                // This prevents redirect to login if endpoint is not available
                console.warn('Could not fetch reflection history, continuing without progress:', err);
                setUserProgress([]);
            } finally {
                setIsLoading(false);
            }
        };

        if (session?.days) {
            fetchProgress();
        }
    }, [session]);

    const isDayCompleted = (dayNumber) => {
        return userProgress.some(p => p.day_number === dayNumber);
    };

    const handleDayClick = (dayNumber) => {
        navigate(`/journey/day/${dayNumber}`);
    };

    if (!session || !session.days) {
        return (
            <div className="bg-surface rounded-xl shadow-sm p-8 text-center">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Calendar className="w-8 h-8 text-gray-400" />
                </div>
                <h3 className="text-lg font-semibold text-gray-800">Journey Loading...</h3>
                <p className="text-gray-500">Your personalized reflection journey is being prepared.</p>
            </div>
        );
    }

    if (isLoading) {
        return (
            <div className="bg-surface rounded-xl shadow-sm p-8 text-center">
                <div className="animate-pulse space-y-4">
                    <div className="h-4 bg-gray-200 rounded w-3/4 mx-auto"></div>
                    <div className="h-4 bg-gray-200 rounded w-1/2 mx-auto"></div>
                </div>
            </div>
        );
    }

    const sortedDays = [...session.days].sort((a, b) => a.day - b.day);
    const completedCount = userProgress.length;
    const totalDays = sortedDays.length;

    return (
        <div className="space-y-6">
            {/* Header with Progress */}
            <div className="bg-accent-lighter rounded-xl shadow-sm border border-theme p-4 sm:p-6">
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4 gap-4 sm:gap-0">
                    <div>
                        <h2 className="text-xl sm:text-2xl font-bold text-gray-900 flex items-center gap-2">
                            <Sparkles className="w-6 h-6 text-accent" />
                            {session.session_title}
                        </h2>
                        <p className="text-sm text-gray-600 mt-1">Your personalized 7-day journey to self-discovery</p>
                    </div>
                    <div className="text-left sm:text-right">
                        <div className="text-3xl font-bold text-accent">{completedCount}/{totalDays}</div>
                        <div className="text-xs text-gray-500 uppercase tracking-wide">Days Complete</div>
                    </div>
                </div>

                {/* Progress Bar */}
                <div className="relative w-full h-3 bg-gray-200 rounded-full overflow-hidden">
                    <div
                        className="absolute top-0 left-0 h-full progress-bar-fill transition-all duration-500"
                        style={{ width: `${(completedCount / totalDays) * 100}%` }}
                    />
                </div>

                {/* Themes */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-4">
                    <div className="bg-white/60 backdrop-blur p-3 rounded-lg border border-theme">
                        <span className="block text-xs uppercase text-accent font-bold mb-1">Primary Focus</span>
                        <span className="font-semibold text-gray-800">{session.primary_theme?.dimension}: </span>
                        <span className="text-sm text-gray-600">{session.primary_theme?.reason}</span>
                    </div>
                    <div className="bg-white/60 backdrop-blur p-3 rounded-lg border border-purple-100">
                        <span className="block text-xs uppercase text-purple-600 font-bold mb-1">Secondary Focus</span>
                        <span className="font-semibold text-gray-800">{session.secondary_theme?.dimension}: </span>
                        <span className="text-sm text-gray-600">{session.secondary_theme?.reason}</span>
                    </div>
                </div>
            </div>

            {/* Day Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {sortedDays.map((day) => {
                    const completed = isDayCompleted(day.day);
                    const isNextDay = day.day === completedCount + 1;
                    const isLocked = day.day > completedCount + 1;

                    return (
                        <button
                            key={day.day}
                            onClick={() => !isLocked && handleDayClick(day.day)}
                            disabled={isLocked}
                            className={`
                                relative p-4 sm:p-6 rounded-xl border-2 text-left transition-all transform hover:scale-105
                                ${completed ? 'bg-green-50 border-green-300 hover:bg-green-100' : ''}
                                ${isNextDay ? 'bg-accent-light border-accent hover:bg-accent-lighter ring-2 ring-accent' : ''}
                                ${isLocked ? 'bg-gray-50 border-gray-200 opacity-50 cursor-not-allowed hover:scale-100' : ''}
                                ${!completed && !isNextDay && !isLocked ? 'bg-white border-gray-200 hover:border-accent' : ''}
                            `}
                        >
                            {/* Day Number Badge */}
                            <div className="flex items-start justify-between mb-3">
                                <div className={`
                                    w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg
                                    ${completed ? 'bg-green-600 text-white' : ''}
                                    ${isNextDay ? 'bg-accent text-white' : ''}
                                    ${isLocked ? 'bg-gray-400 text-white' : ''}
                                    ${!completed && !isNextDay && !isLocked ? 'bg-gray-200 text-gray-600' : ''}
                                `}>
                                    {day.day}
                                </div>
                                <div>
                                    {completed && <CheckCircle className="w-6 h-6 text-green-600" />}
                                    {isLocked && <Lock className="w-6 h-6 text-gray-400" />}
                                    {isNextDay && <Sparkles className="w-6 h-6 text-accent" />}
                                </div>
                            </div>

                            {/* Title */}
                            <h3 className={`font-semibold text-lg mb-2 ${isLocked ? 'text-gray-400' : 'text-gray-900'}`}>
                                {day.title}
                            </h3>

                            {/* Unlock Info */}
                            <div className={`flex items-center gap-2 text-xs ${isLocked ? 'text-gray-400' : 'text-gray-500'}`}>
                                <Clock className="w-3 h-3" />
                                Day {day.unlock_day} at {day.unlock_time_local}
                            </div>

                            {/* Status Badge */}
                            <div className="mt-3">
                                {completed && (
                                    <span className="inline-block px-2 py-1 bg-green-100 text-green-700 text-xs font-medium rounded">
                                        Completed
                                    </span>
                                )}
                                {isNextDay && (
                                    <span className="inline-block px-2 py-1 bg-accent-light text-accent text-xs font-medium rounded">
                                        Start Today
                                    </span>
                                )}
                                {isLocked && (
                                    <span className="inline-block px-2 py-1 bg-gray-100 text-gray-500 text-xs font-medium rounded">
                                        Locked
                                    </span>
                                )}
                            </div>
                        </button>
                    );
                })}
            </div>

            {/* All Days Completed */}
            {completedCount === totalDays && (
                <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl p-8 text-center">
                    <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <CheckCircle className="w-10 h-10 text-green-600" />
                    </div>
                    <h3 className="text-2xl font-bold text-gray-900 mb-2">🎉 Journey Complete!</h3>
                    <p className="text-gray-600 max-w-md mx-auto">
                        You've completed all 7 days of reflection. Take a moment to review your insights and celebrate your growth.
                    </p>
                </div>
            )}
        </div>
    );
};

export default ReflectionJourney;

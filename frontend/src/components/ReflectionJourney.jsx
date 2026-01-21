import React, { useState } from 'react';
import { Lock, Unlock, CheckCircle, Clock, ChevronRight, ChevronLeft, Calendar } from 'lucide-react';

const ReflectionJourney = ({ session }) => {
    // session structure matches ReflectionSessionResponse schema from backend
    const [activeDay, setActiveDay] = useState(1);
    const [expandedDay, setExpandedDay] = useState(null);

    if (!session || !session.days) {
        return (
            <div className="bg-white rounded-xl shadow-sm p-8 text-center">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Calendar className="w-8 h-8 text-gray-400" />
                </div>
                <h3 className="text-lg font-semibold text-gray-800">Journey Loading...</h3>
                <p className="text-gray-500">Your personalized reflection journey is being prepared.</p>
            </div>
        );
    }

    const toggleDay = (dayNum) => {
        if (expandedDay === dayNum) {
            setExpandedDay(null);
        } else {
            setExpandedDay(dayNum);
        }
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="bg-white rounded-xl shadow-sm border border-indigo-100 p-6">
                <div className="flex items-center justify-between mb-2">
                    <h2 className="text-xl font-bold text-gray-900">{session.session_title}</h2>
                    <span className="text-sm px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full font-medium">
                        7-Day Journey
                    </span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600 mt-4">
                    <div className="bg-gray-50 p-3 rounded-lg border border-gray-100">
                        <span className="block text-xs uppercase text-gray-400 font-bold mb-1">Primary Theme</span>
                        <span className="font-semibold text-gray-800">{session.primary_theme?.dimension}: </span>
                        {session.primary_theme?.reason}
                    </div>
                    <div className="bg-gray-50 p-3 rounded-lg border border-gray-100">
                        <span className="block text-xs uppercase text-gray-400 font-bold mb-1">Secondary Theme</span>
                        <span className="font-semibold text-gray-800">{session.secondary_theme?.dimension}: </span>
                        {session.secondary_theme?.reason}
                    </div>
                </div>
            </div>

            {/* Days List */}
            <div className="space-y-4">
                {session.days.sort((a, b) => a.day - b.day).map((dayRec) => (
                    <div
                        key={dayRec.day}
                        className={`bg-white rounded-xl shadow-sm border transition-all duration-300 overflow-hidden
                ${expandedDay === dayRec.day ? 'border-indigo-300 ring-4 ring-indigo-50/50' : 'border-gray-200 hover:border-indigo-200'}
            `}
                    >
                        {/* Day Header - Clickable */}
                        <div
                            onClick={() => toggleDay(dayRec.day)}
                            className="p-5 flex items-center justify-between cursor-pointer"
                        >
                            <div className="flex items-center gap-4">
                                <div className={`
                        w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg
                        ${dayRec.day <= activeDay ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-400'}
                    `}>
                                    {dayRec.day}
                                </div>
                                <div>
                                    <h3 className={`font-semibold text-lg ${dayRec.day <= activeDay ? 'text-gray-900' : 'text-gray-500'}`}>
                                        {dayRec.title}
                                    </h3>
                                    <div className="flex items-center gap-2 text-xs text-gray-500">
                                        <Clock className="w-3 h-3" />
                                        Unlocks Day {dayRec.unlock_day} at {dayRec.unlock_time_local}
                                    </div>
                                </div>
                            </div>

                            <div className="flex items-center">
                                {expandedDay === dayRec.day ?
                                    <ChevronRight className="w-5 h-5 text-gray-400 transform rotate-90 transition-transform" /> :
                                    <ChevronRight className="w-5 h-5 text-gray-400" />
                                }
                            </div>
                        </div>

                        {/* Day Content - Collapsible */}
                        {expandedDay === dayRec.day && (
                            <div className="px-5 pb-6 pt-0 border-t border-gray-100 mt-2 bg-gray-50/30">
                                <div className="pt-6 space-y-6">

                                    {/* Questions */}
                                    <div className="space-y-4">
                                        <h4 className="font-medium text-gray-900 flex items-center gap-2">
                                            <BookOpenIcon className="w-4 h-4 text-indigo-500" />
                                            Reflection Questions
                                        </h4>
                                        <div className="space-y-3">
                                            {dayRec.questions.map((q, idx) => (
                                                <div key={idx} className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm relative group hover:border-indigo-200 transition-colors">
                                                    <span className="absolute top-3 left-3 text-xs font-bold text-gray-300 group-hover:text-indigo-200">Q{idx + 1}</span>
                                                    <p className="pl-6 text-gray-700 italic">"{q}"</p>
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Micro Action */}
                                    <div className="bg-emerald-50 border border-emerald-100 rounded-lg p-4">
                                        <h4 className="font-semibold text-emerald-800 flex items-center gap-2 mb-2">
                                            <TargetIcon className="w-4 h-4" />
                                            Micro Action
                                        </h4>
                                        <p className="text-emerald-700 text-sm">
                                            {dayRec.micro_action}
                                        </p>
                                    </div>

                                    {/* Notice Cue & Completion */}
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div className="bg-amber-50 border border-amber-100 rounded-lg p-4">
                                            <h4 className="font-semibold text-amber-800 text-sm mb-1">Daily Notice Cue</h4>
                                            <p className="text-amber-700 text-sm italic">"{dayRec.notice_cue}"</p>
                                        </div>
                                        <div className="bg-indigo-50 border border-indigo-100 rounded-lg p-4 flex items-center justify-between">
                                            <div>
                                                <h4 className="font-semibold text-indigo-800 text-sm mb-1">Completion Check</h4>
                                                <p className="text-indigo-700 text-sm">{dayRec.completion_check}</p>
                                            </div>
                                            <CheckCircle className="w-6 h-6 text-indigo-200" />
                                        </div>
                                    </div>

                                </div>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};

// Simple icons for this component
const BookOpenIcon = ({ className }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
    </svg>
);

const TargetIcon = ({ className }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
    </svg>
);

export default ReflectionJourney;

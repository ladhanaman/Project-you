// src/components/Dashboard.jsx
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
    BookOpen, ArrowRight, CheckCircle, FileText, LogOut, 
    Code, User, Brain, X, MessageSquare 
} from 'lucide-react';
import { useStore } from '../store/useStore.js';
import { fetchTests } from '../services/apiService.js';
import { DashboardSkeleton } from './Skeleton.jsx';

export default function Dashboard() {
    const navigate = useNavigate();
    const { user, logout } = useStore();
    const [tests, setTests] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [inProgressTests, setInProgressTests] = useState({});

    // --- NEW STATE FOR DAY CARDS ---
    const [activeDay, setActiveDay] = useState(null); // Stores the day number (1-7) currently open
    const days = [1, 2, 3, 4, 5, 6, 7];

    useEffect(() => {
        const loadTests = async () => {
            try {
                const data = await fetchTests();
                setTests(data);

                const savedStateStr = localStorage.getItem('testState');
                if (savedStateStr) {
                    try {
                        const savedState = JSON.parse(savedStateStr);
                        const now = Date.now();
                        const savedTime = savedState.timestamp || 0;
                        const expirationTime = 24 * 60 * 60 * 1000;

                        const isValidUser = savedState.userId === user?.id;
                        const isNotExpired = now - savedTime <= expirationTime;

                        if (isValidUser && isNotExpired) {
                            setInProgressTests({ [savedState.testId]: true });
                        } else if (!isValidUser) {
                            localStorage.removeItem('testState');
                        }
                    } catch (err) {
                        console.error('Failed to parse saved test state:', err);
                        localStorage.removeItem('testState');
                    }
                }
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        loadTests();
    }, [user?.id]);

    const handleStartTest = (testId, submissionId) => {
        if (submissionId) {
            navigate(`/results/${submissionId}`);
        } else {
            navigate(`/assessment/${testId}`);
        }
    };

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    // --- MODAL HANDLERS ---
    const handleDayClick = (dayNumber) => {
        setActiveDay(dayNumber);
    };

    const handleCloseModal = () => {
        setActiveDay(null);
    };

    const handleDaySubmit = (e) => {
        e.preventDefault();
        // FUTURE: Add API call here to save the answer
        console.log(`Submitted answer for Day ${activeDay}`);
        setActiveDay(null);
    };

    if (loading) {
        return <DashboardSkeleton />;
    }

    if (error) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center p-4">
                <div className="bg-white rounded-xl shadow-lg border border-slate-200 p-8 max-w-md text-center">
                    <div className="text-red-600 text-5xl mb-4">⚠</div>
                    <h2 className="text-2xl font-bold text-slate-900 mb-4">Error Loading Assessment</h2>
                    <p className="text-slate-600 mb-6">{error}</p>
                    <button
                        onClick={() => window.location.reload()}
                        className="bg-slate-900 hover:bg-slate-800 text-white font-medium py-3 px-6 rounded-lg transition"
                    >
                        Retry
                    </button>
                </div>
            </div>
        );
    }

    const mainTest = tests.length > 0 ? tests[0] : null;

    // --- TOGGLE THIS TO TRUE TO SEE THE UI WITHOUT COMPLETING THE TEST ---
    const TEST_MODE = true; 
    const showDailyTasks = TEST_MODE || (mainTest && mainTest.user_submission_id);

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 relative">
            <div className="max-w-5xl mx-auto px-4 py-8">
                {/* Header Section */}
                <div className="flex items-center justify-between mb-8">
                    <div>
                        <h1 className="text-3xl font-bold text-slate-900 mb-2">
                            Welcome, {user?.full_name}
                        </h1>
                        <p className="text-slate-600">Your journey starts here</p>
                    </div>
                    <button
                        onClick={handleLogout}
                        className="flex items-center gap-2 px-4 py-2 text-slate-700 hover:text-slate-900 hover:bg-white rounded-lg transition border border-slate-200"
                    >
                        <LogOut className="w-5 h-5" />
                        Logout
                    </button>
                </div>

                {/* Main "Know Yourself" Card */}
                {mainTest && (
                    <div className="w-full bg-white rounded-2xl shadow-lg border border-slate-200 p-10 md:p-14 hover:shadow-xl transition-all duration-300 flex flex-col items-center text-center mb-12">
                        
                        <div className="w-20 h-20 bg-slate-900 rounded-2xl flex items-center justify-center mb-6 shadow-md">
                            <Brain className="w-10 h-10 text-white" />
                        </div>

                        <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
                            Decode Your Psyche
                        </h2>

                        <p className="text-lg text-slate-600 mb-10 max-w-2xl leading-relaxed">
                            {mainTest.description || "Take this comprehensive assessment to evaluate your personality and readiness for the industry."}
                        </p>

                        <button
                            onClick={() => handleStartTest(mainTest.id, mainTest.user_submission_id)}
                            className={`min-w-[240px] font-bold text-lg py-4 px-8 rounded-xl transition duration-200 flex items-center justify-center gap-3 group ${
                                mainTest.user_submission_id
                                    ? 'bg-green-600 hover:bg-green-700 text-white shadow-green-200'
                                    : inProgressTests[mainTest.id]
                                        ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-blue-200'
                                        : 'bg-slate-900 hover:bg-slate-800 text-white shadow-slate-300'
                            } shadow-lg hover:translate-y-[-2px]`}
                        >
                            {mainTest.user_submission_id ? (
                                <>
                                    <CheckCircle className="w-6 h-6" />
                                    View Report
                                    <FileText className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
                                </>
                            ) : inProgressTests[mainTest.id] ? (
                                <>
                                    Continue Assessment
                                    <ArrowRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
                                </>
                            ) : (
                                <>
                                    Start Assessment
                                    <ArrowRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
                                </>
                            )}
                        </button>
                    </div>
                )}

                {/* --- NEW SECTION: 7 DAY JOURNEY --- */}
                {/* This only renders if the main test is completed (or TEST_MODE is true) */}
                {showDailyTasks && (
                    <div className="animate-fade-in-up">
                        <div className="flex items-center gap-3 mb-6">
                            <h3 className="text-2xl font-bold text-slate-900">Your 7-Day Journey</h3>
                            <div className="h-px flex-1 bg-slate-200"></div>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                            {days.map((day) => (
                                <button
                                    key={day}
                                    onClick={() => handleDayClick(day)}
                                    className="bg-white border border-slate-200 rounded-xl p-4 flex flex-col items-center justify-center gap-3 hover:shadow-lg hover:-translate-y-1 transition-all duration-200 group h-32"
                                >
                                    <div className="w-10 h-10 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center group-hover:bg-blue-600 group-hover:text-white transition-colors">
                                        <MessageSquare className="w-5 h-5" />
                                    </div>
                                    <span className="font-semibold text-slate-700 group-hover:text-blue-600 transition-colors">
                                        Day {day}
                                    </span>
                                </button>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            {/* --- MODAL POPUP --- */}
            {activeDay && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                    {/* Backdrop */}
                    <div 
                        className="absolute inset-0 bg-black/50 backdrop-blur-sm transition-opacity"
                        onClick={handleCloseModal}
                    ></div>

                    {/* Modal Content */}
                    <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden animate-scale-up">
                        {/* Header */}
                        <div className="bg-slate-50 px-6 py-4 border-b border-slate-100 flex justify-between items-center">
                            <h3 className="text-xl font-bold text-slate-900">
                                Day {activeDay} Reflection
                            </h3>
                            <button 
                                onClick={handleCloseModal}
                                className="p-2 hover:bg-slate-200 rounded-full transition-colors text-slate-500"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        {/* Form */}
                        <form onSubmit={handleDaySubmit} className="p-6">
                            <div className="mb-6">
                                <label className="block text-sm font-medium text-slate-700 mb-3">
                                    Question for Day {activeDay}:
                                </label>
                                <p className="text-slate-600 mb-4 italic">
                                    "Reflect on what you discovered about your professional interests today. How does this align with your goals?"
                                </p>
                                <textarea 
                                    className="w-full p-4 border border-slate-300 rounded-xl focus:ring-2 focus:ring-slate-900 focus:border-transparent outline-none min-h-[120px] resize-none text-slate-700"
                                    placeholder="Type your answer here..."
                                    required
                                ></textarea>
                            </div>

                            <div className="flex justify-end gap-3">
                                <button 
                                    type="button"
                                    onClick={handleCloseModal}
                                    className="px-5 py-2.5 text-slate-600 font-medium hover:bg-slate-50 rounded-lg transition"
                                >
                                    Cancel
                                </button>
                                <button 
                                    type="submit"
                                    className="px-5 py-2.5 bg-slate-900 text-white font-medium rounded-lg hover:bg-slate-800 transition shadow-lg shadow-slate-200"
                                >
                                    Submit Reflection
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
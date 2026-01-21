import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    BookOpen, ArrowRight, CheckCircle, FileText, LogOut,
    Code, User, Brain, X, MessageSquare, Loader
} from 'lucide-react';
import { useStore } from '../store/useStore.js';
import { fetchTests, getReflectionSession, submitDailyReflection, getDailyReflections } from '../services/apiService.js';
// Removed Skeleton.jsx - using inline loading component

// Inline DashboardSkeleton replacement
const DashboardSkeleton = () => (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-8">
        <div className="max-w-7xl mx-auto">
            <div className="animate-pulse space-y-6">
                <div className="h-12 bg-gray-200 rounded w-1/3"></div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="h-48 bg-gray-200 rounded"></div>
                    <div className="h-48 bg-gray-200 rounded"></div>
                </div>
            </div>
        </div>
    </div>
);

export default function Dashboard() {
    const navigate = useNavigate();
    const { user, logout } = useStore();
    const [tests, setTests] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [inProgressTests, setInProgressTests] = useState({});

    // --- PRI REFLECTION SESSION STATE ---
    const [reflectionSession, setReflectionSession] = useState(null);
    const [completedDays, setCompletedDays] = useState(new Set());
    const [loadingSession, setLoadingSession] = useState(false);

    // --- MODAL STATE ---
    const [activeDay, setActiveDay] = useState(null);
    const [submitting, setSubmitting] = useState(false);
    const [reflectionAnswer, setReflectionAnswer] = useState('');

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

                // Fetch reflection session if user has completed the main test
                const mainTest = data.length > 0 ? data[0] : null;
                if (mainTest && mainTest.user_submission_id) {
                    setLoadingSession(true);
                    try {
                        const session = await getReflectionSession(mainTest.user_submission_id);
                        setReflectionSession(session);

                        // Fetch completed reflections
                        const completedReflections = await getDailyReflections();
                        const completedSet = new Set(completedReflections.map(r => r.day_number));
                        setCompletedDays(completedSet);
                    } catch (err) {
                        console.error('Failed to fetch reflection session:', err);
                    } finally {
                        setLoadingSession(false);
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
        setReflectionAnswer('');
    };

    const handleCloseModal = () => {
        setActiveDay(null);
        setReflectionAnswer('');
    };

    const handleDaySubmit = async (e) => {
        e.preventDefault();
        if (!reflectionAnswer.trim()) return;

        setSubmitting(true);
        try {
            await submitDailyReflection(activeDay, reflectionAnswer);
            setCompletedDays(prev => new Set([...prev, activeDay]));
            setActiveDay(null);
            setReflectionAnswer('');
        } catch (err) {
            console.error('Failed to submit reflection:', err);
            alert('Failed to submit reflection. Please try again.');
        } finally {
            setSubmitting(false);
        }
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
    const showDailyTasks = reflectionSession !== null;

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
                            WHO AM I
                        </h2>

                        <p className="text-lg text-slate-600 mb-10 max-w-2xl leading-relaxed">
                            {mainTest.description || "Take this comprehensive assessment to evaluate your personality and readiness for the industry."}
                        </p>

                        <button
                            onClick={() => handleStartTest(mainTest.id, mainTest.user_submission_id)}
                            className={`min-w-[240px] font-bold text-lg py-4 px-8 rounded-xl transition duration-200 flex items-center justify-center gap-3 group ${mainTest.user_submission_id
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
                                    Continue
                                    <ArrowRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
                                </>
                            ) : (
                                <>
                                    Begin
                                    <ArrowRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
                                </>
                            )}
                        </button>
                    </div>
                )}

                {/* --- 7-DAY JOURNEY SECTION --- */}
                {showDailyTasks && (
                    <div className="animate-fade-in-up">
                        <div className="flex items-center gap-3 mb-6">
                            <h3 className="text-2xl font-bold text-slate-900">Your 7-Day Journey</h3>
                            <div className="h-px flex-1 bg-slate-200"></div>
                        </div>

                        {loadingSession ? (
                            <div className="text-center py-12">
                                <Loader className="animate-spin mx-auto mb-4 text-slate-400" size={32} />
                                <p className="text-slate-500">Loading your personalized journey...</p>
                            </div>
                        ) : (
                            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                                {reflectionSession?.days?.sort((a, b) => a.day - b.day).map((dayData) => (
                                    <button
                                        key={dayData.day}
                                        onClick={() => handleDayClick(dayData.day)}
                                        className={`bg-white border rounded-xl p-4 flex flex-col items-center justify-center gap-3 hover:shadow-lg hover:-translate-y-1 transition-all duration-200 group h-32 relative ${completedDays.has(dayData.day)
                                            ? 'border-green-300 bg-green-50'
                                            : 'border-slate-200'
                                            }`}
                                    >
                                        {completedDays.has(dayData.day) && (
                                            <div className="absolute top-2 right-2">
                                                <CheckCircle className="w-5 h-5 text-green-600" />
                                            </div>
                                        )}
                                        <div className={`w-10 h-10 rounded-full flex items-center justify-center group-hover:scale-110 transition-transform ${completedDays.has(dayData.day)
                                            ? 'bg-green-100 text-green-600'
                                            : 'bg-slate-100 text-slate-700 group-hover:bg-slate-700 group-hover:text-white'
                                            }`}>
                                            <MessageSquare className="w-5 h-5" />
                                        </div>
                                        <div className="text-center">
                                            <span className={`font-semibold text-sm block ${completedDays.has(dayData.day) ? 'text-green-700' : 'text-slate-700 group-hover:text-slate-900'
                                                }`}>
                                                Day {dayData.day}
                                            </span>
                                            <span className="text-xs text-slate-500 line-clamp-1">
                                                {dayData.title}
                                            </span>
                                        </div>
                                    </button>
                                ))}
                            </div>
                        )}
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
                            <div>
                                <h3 className="text-xl font-bold text-slate-900">
                                    Day {activeDay} Reflection
                                </h3>
                                <p className="text-sm text-slate-500">
                                    {reflectionSession?.days?.find(d => d.day === activeDay)?.title}
                                </p>
                            </div>
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
                                    Reflection Questions:
                                </label>
                                <div className="space-y-3 mb-4">
                                    {reflectionSession?.days?.find(d => d.day === activeDay)?.questions?.map((question, idx) => (
                                        <p key={idx} className="text-slate-600 italic bg-slate-50 p-3 rounded-lg border border-slate-200">
                                            {idx + 1}. "{question}"
                                        </p>
                                    ))}
                                </div>
                                <textarea
                                    className="w-full p-4 border border-slate-300 rounded-xl focus:ring-2 focus:ring-slate-900 focus:border-transparent outline-none min-h-[120px] resize-none text-slate-700"
                                    placeholder="Type your reflections here..."
                                    required
                                    value={reflectionAnswer}
                                    onChange={(e) => setReflectionAnswer(e.target.value)}
                                    disabled={submitting}
                                ></textarea>
                            </div>

                            <div className="flex justify-end gap-3">
                                <button
                                    type="button"
                                    onClick={handleCloseModal}
                                    className="px-5 py-2.5 text-slate-600 font-medium hover:bg-slate-50 rounded-lg transition"
                                    disabled={submitting}
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="px-5 py-2.5 bg-slate-900 text-white font-medium rounded-lg hover:bg-slate-800 transition shadow-lg shadow-slate-200 disabled:bg-slate-400 disabled:cursor-not-allowed flex items-center gap-2"
                                    disabled={submitting}
                                >
                                    {submitting ? (
                                        <>
                                            <Loader className="animate-spin" size={16} />
                                            Submitting...
                                        </>
                                    ) : (
                                        'Submit Reflection'
                                    )}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    BookOpen, ArrowRight, CheckCircle, FileText, LogOut,
    Code, User, Brain, X, MessageSquare, Loader, Sparkles
} from 'lucide-react';
import { useStore } from '../store/useStore.js';
import { fetchTests, getReflectionSession, getDailyReflections } from '../services/apiService.js';
import ThemeSwitcher from './ThemeSwitcher.jsx';

// Inline DashboardSkeleton replacement
const DashboardSkeleton = () => (
    <div className="min-h-screen bg-gradient-theme p-8">
        <div className="max-w-5xl mx-auto">
            <div className="animate-pulse space-y-6">
                <div className="h-12 bg-surface-elevated rounded w-1/3"></div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="h-48 bg-surface-elevated rounded-xl"></div>
                    <div className="h-48 bg-surface-elevated rounded-xl"></div>
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

    const handleDayClick = (dayNumber) => {
        navigate(`/reflection/${dayNumber}`);
    };

    if (loading) {
        return <DashboardSkeleton />;
    }

    if (error) {
        return (
            <div className="min-h-screen bg-gradient-theme flex items-center justify-center p-4">
                <div className="bg-white rounded-2xl shadow-xl border border-red-200 p-8 max-w-md text-center">
                    <div className="text-red-600 text-5xl mb-4">⚠</div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-4">Error Loading Assessment</h2>
                    <p className="text-gray-600 mb-6">{error}</p>
                    <button
                        onClick={() => window.location.reload()}
                        className="bg-button-gradient text-white font-medium py-3 px-6 rounded-xl transition"
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
        <div className="min-h-screen bg-gradient-theme relative">
            <div className="max-w-5xl mx-auto px-4 py-8">
                {/* Header Section */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-8 gap-4 sm:gap-0">
                    <div>
                        <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">
                            Welcome, {user?.full_name}
                        </h1>
                        <p className="text-gray-600">Your journey starts here</p>
                    </div>
                    <div className="flex items-center gap-3">
                        <ThemeSwitcher />
                        <button
                            onClick={handleLogout}
                            className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:text-gray-900 hover:bg-white/80 rounded-lg transition border border-gray-200 backdrop-blur-sm"
                        >
                            <LogOut className="w-5 h-5" />
                            Logout
                        </button>
                    </div>
                </div>

                {/* Main "Know Yourself" Card */}
                {mainTest && (
                    <div className="w-full bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg border border-theme p-6 sm:p-10 md:p-14 hover:shadow-xl transition-all duration-300 flex flex-col items-center text-center mb-12">

                        <div className="w-20 h-20 bg-icon-gradient rounded-2xl flex items-center justify-center mb-6 shadow-lg">
                            <Brain className="w-10 h-10 text-white" />
                        </div>

                        <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                            WHO AM I
                        </h2>

                        <p className="text-lg text-gray-600 mb-10 max-w-2xl leading-relaxed">
                            {mainTest.description || "Take this comprehensive assessment to evaluate your personality and readiness for the industry."}
                        </p>

                        <button
                            onClick={() => handleStartTest(mainTest.id, mainTest.user_submission_id)}
                            className={`w-full sm:w-auto sm:min-w-[240px] font-bold text-lg py-4 px-8 rounded-xl transition duration-200 flex items-center justify-center gap-3 group ${mainTest.user_submission_id
                                ? 'bg-completed-state text-white shadow-lg shadow-theme'
                                : inProgressTests[mainTest.id]
                                    ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg shadow-blue-200'
                                    : 'bg-button-gradient text-white shadow-lg shadow-theme'
                                } hover:translate-y-[-2px]`}
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
                            <Sparkles className="w-6 h-6 text-accent" />
                            <h3 className="text-2xl font-bold text-gray-900">Your 7-Day Journey</h3>
                            <div className="h-px flex-1 bg-gradient-to-r from-gray-200 to-transparent"></div>
                        </div>

                        {loadingSession ? (
                            <div className="text-center py-12">
                                <Loader className="animate-spin mx-auto mb-4 text-accent" size={32} />
                                <p className="text-accent font-medium">Loading your personalized journey...</p>
                            </div>
                        ) : (
                            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 sm:gap-6">
                                {reflectionSession?.days?.sort((a, b) => a.day - b.day).map((dayData) => (
                                    <button
                                        key={dayData.day}
                                        onClick={() => handleDayClick(dayData.day)}
                                        className={`bg-white/90 backdrop-blur-sm border-2 rounded-xl p-5 flex flex-col items-center justify-center gap-3 hover:shadow-lg hover:-translate-y-1 transition-all duration-200 group h-36 relative ${completedDays.has(dayData.day)
                                            ? 'border-green-300 bg-green-50/80'
                                            : 'border-theme hover:border-accent'
                                            }`}
                                    >
                                        {completedDays.has(dayData.day) && (
                                            <div className="absolute top-2 right-2">
                                                <CheckCircle className="w-5 h-5 text-green-600" />
                                            </div>
                                        )}
                                        <div className={`w-12 h-12 rounded-full flex items-center justify-center group-hover:scale-110 transition-transform shadow-sm ${completedDays.has(dayData.day)
                                            ? 'bg-green-100 text-green-600'
                                            : 'bg-accent-light text-accent group-hover:bg-accent group-hover:text-white'
                                            }`}>
                                            <MessageSquare className="w-5 h-5" />
                                        </div>
                                        <div className="text-center">
                                            <span className={`font-semibold text-sm block ${completedDays.has(dayData.day) ? 'text-green-700' : 'text-gray-700 group-hover:text-gray-900'
                                                }`}>
                                                Day {dayData.day}
                                            </span>
                                            <span className="text-xs text-gray-500 line-clamp-1">
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
        </div>
    );
}
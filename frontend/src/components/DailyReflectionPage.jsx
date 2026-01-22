import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ChevronLeft, ChevronRight, CheckCircle, Save, ArrowLeft, Loader, Sparkles } from 'lucide-react';
import { fetchTests, getReflectionSession, submitDailyReflection, getDailyReflections } from '../services/apiService';
import confetti from 'canvas-confetti';

export default function DailyReflectionPage() {
    const { dayNumber } = useParams();
    const navigate = useNavigate();
    const dayNum = parseInt(dayNumber);

    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [dayData, setDayData] = useState(null);
    const [questions, setQuestions] = useState([]);
    const [currentStep, setCurrentStep] = useState(0);
    const [answers, setAnswers] = useState({});
    const [showSuccess, setShowSuccess] = useState(false);
    const [userId, setUserId] = useState(null);  // Track user ID for localStorage keys

    // Initial Data Load
    useEffect(() => {
        const loadSession = async () => {
            try {
                // 1. Get tests to find submission ID
                const tests = await fetchTests();
                const mainTest = tests.length > 0 ? tests[0] : null;

                if (!mainTest || !mainTest.user_submission_id) {
                    navigate('/dashboard'); // No access if no submission
                    return;
                }

                // 2. Get Session Data
                const session = await getReflectionSession(mainTest.user_submission_id);
                if (!session) {
                    throw new Error("No session found");
                }

                const currentDay = session.days.find(d => d.day === dayNum);
                if (!currentDay) {
                    navigate('/dashboard');
                    return;
                }

                setDayData(currentDay);
                setQuestions(currentDay.questions || []);

                // 3. Load user ID from session
                setUserId(session.user_id || mainTest.user_id || 'unknown');

                // 4. Load Draft or Previous Submission
                const history = await getDailyReflections();
                const existing = history.find(h => h.day_number === dayNum);

                if (existing) {
                    // Start with existing answers if re-visiting (optional)
                    try {
                        // Try parsing as JSON first (new format)
                        const parsed = JSON.parse(existing.answer);
                        setAnswers(parsed);
                    } catch (e) {
                        // Fallback for old text format - put it in first box
                        setAnswers({ 0: existing.answer });
                    }
                } else {
                    // Load from local storage draft (with user ID to prevent cross-user leaks)
                    const userIdKey = session.user_id || mainTest.user_id || 'unknown';
                    const savedDraft = localStorage.getItem(`reflection_draft_user_${userIdKey}_day_${dayNum}`);
                    if (savedDraft) {
                        setAnswers(JSON.parse(savedDraft));
                    }
                }

            } catch (err) {
                console.error("Failed to load reflection data:", err);
                alert("Failed to load session. Returning to dashboard.");
                navigate('/dashboard');
            } finally {
                setLoading(false);
            }
        };

        loadSession();
    }, [dayNum, navigate]);

    // Save Draft on Change (with user ID to prevent cross-user leaks)
    useEffect(() => {
        if (!loading && userId && Object.keys(answers).length > 0) {
            localStorage.setItem(`reflection_draft_user_${userId}_day_${dayNum}`, JSON.stringify(answers));
        }
    }, [answers, dayNum, loading, userId]);

    const handleAnswerChange = (text) => {
        setAnswers(prev => ({
            ...prev,
            [currentStep]: text
        }));
    };

    const handleNext = () => {
        if (currentStep < questions.length - 1) {
            setCurrentStep(prev => prev + 1);
        } else {
            handleSubmit();
        }
    };

    const handlePrev = () => {
        if (currentStep > 0) {
            setCurrentStep(prev => prev - 1);
        }
    };

    const handleSubmit = async () => {
        setSubmitting(true);
        try {
            // Bundle answers as JSON string
            const answerPayload = JSON.stringify(answers);
            await submitDailyReflection(dayNum, answerPayload);

            // Trigger confetti
            confetti({
                particleCount: 150,
                spread: 70,
                origin: { y: 0.6 }
            });

            // Clear draft (use user-specific key)
            if (userId) {
                localStorage.removeItem(`reflection_draft_user_${userId}_day_${dayNum}`);
            }

            setShowSuccess(true);
            setTimeout(() => {
                navigate('/dashboard');
            }, 3000);
        } catch (err) {
            console.error("Submission failed:", err);
            alert("Failed to save reflection. Please try again.");
            setSubmitting(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-theme flex items-center justify-center">
                <div className="text-center">
                    <Loader className="animate-spin text-accent w-10 h-10 mx-auto mb-4" />
                    <p className="text-accent font-medium">Preparing your space...</p>
                </div>
            </div>
        );
    }

    if (showSuccess) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-50 flex items-center justify-center p-4">
                <div className="text-center animate-scale-up">
                    <div className="w-24 h-24 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                        <CheckCircle className="w-12 h-12 text-green-600" />
                    </div>
                    <h2 className="text-3xl font-bold text-gray-900 mb-2">Reflection Saved! 🎉</h2>
                    <p className="text-gray-600 mb-8">Great job taking time for yourself today.</p>
                    <p className="text-sm text-gray-500">Redirecting to dashboard...</p>
                </div>
            </div>
        );
    }

    // Handle both old string format and new object format
    const currentQuestion = questions[currentStep];
    const currentQuestionText = typeof currentQuestion === 'string'
        ? currentQuestion
        : currentQuestion?.question || 'Reflection question';
    const progress = ((currentStep + 1) / questions.length) * 100;

    return (
        <div className="min-h-screen bg-gradient-theme flex flex-col">
            {/* Header */}
            <header className="px-4 py-3 sm:px-6 sm:py-4 border-b border-theme flex items-center justify-between bg-white/80 backdrop-blur-sm sticky top-0 z-10 shadow-sm">
                <button
                    onClick={() => navigate('/dashboard')}
                    className="p-2 -ml-2 text-accent hover:text-accent-dark hover:bg-accent-light rounded-full transition"
                >
                    <ArrowLeft className="w-6 h-6" />
                </button>

                <div className="text-center">
                    <div className="flex items-center justify-center gap-2 mb-1">
                        <Sparkles className="w-4 h-4 text-accent" />
                        <h1 className="text-sm font-bold text-accent uppercase tracking-wider">Day {dayNum}</h1>
                    </div>
                    <p className="font-semibold text-gray-900">{dayData?.title}</p>
                </div>

                <div className="w-10"></div> {/* Spacer for balance */}
            </header>

            {/* Progress Bar */}
            <div className="h-2 bg-surface-elevated w-full">
                <div
                    className="h-full progress-bar-fill transition-all duration-500 ease-out shadow-sm"
                    style={{ width: `${progress}%` }}
                ></div>
            </div>

            {/* Main Content */}
            <main className="flex-1 flex flex-col max-w-2xl mx-auto w-full p-4 sm:p-6 md:p-12 justify-center">
                <div className="mb-8">
                    <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-accent-light text-accent text-sm font-medium rounded-full mb-4">
                        Question {currentStep + 1} of {questions.length}
                    </span>
                    <h2 className="text-xl sm:text-2xl md:text-3xl font-bold text-gray-900 leading-tight mt-3">
                        {currentQuestionText}
                    </h2>
                    {/* Timing Hint and Practical Suggestion */}
                    {typeof currentQuestion === 'object' && (
                        <div className="mt-4 space-y-2">
                            {currentQuestion.timing_hint && (
                                <div className="flex items-start gap-2 text-sm text-gray-600">
                                    <span className="font-semibold text-accent">When:</span>
                                    <span>{currentQuestion.timing_hint}</span>
                                </div>
                            )}
                            {currentQuestion.hint && (
                                <div className="flex items-start gap-2 text-sm text-gray-600 bg-accent-lighter/30 p-3 rounded-lg border border-accent-light">
                                    <span className="font-semibold text-accent">Hint:</span>
                                    <span>{currentQuestion.hint}</span>
                                </div>
                            )}
                        </div>
                    )}
                </div>

                <textarea
                    className="w-full flex-1 min-h-[200px] p-6 text-lg bg-white border-2 border-theme rounded-2xl text-gray-800 placeholder:text-gray-300 focus:ring-2 focus:ring-accent focus:border-accent outline-none resize-none transition-all shadow-sm"
                    placeholder="Type your thoughts here..."
                    value={answers[currentStep] || ''}
                    onChange={(e) => handleAnswerChange(e.target.value)}
                    autoFocus
                />

                {/* Save Status Indicator */}
                <div className="h-6 mt-4 flex items-center justify-end text-xs text-accent gap-1.5 opacity-0 transition-opacity duration-500" style={{ opacity: answers[currentStep] ? 1 : 0 }}>
                    <Save className="w-3 h-3" />
                    Draft saved
                </div>
            </main>

            {/* Footer Navigation */}
            <footer className="px-4 py-4 sm:px-6 sm:py-6 border-t border-theme bg-white/80 backdrop-blur-sm sticky bottom-0 shadow-lg">
                <div className="max-w-2xl mx-auto flex items-center justify-between">
                    <button
                        onClick={handlePrev}
                        disabled={currentStep === 0}
                        className={`flex items-center gap-2 px-6 py-3 rounded-xl font-medium transition ${currentStep === 0
                            ? 'text-gray-300 cursor-not-allowed'
                            : 'text-accent hover:bg-accent-light'
                            }`}
                    >
                        <ChevronLeft className="w-5 h-5" />
                        Previous
                    </button>

                    <button
                        onClick={handleNext}
                        disabled={submitting || !answers[currentStep]?.trim()}
                        className={`flex items-center gap-2 px-8 py-3 rounded-xl font-bold text-white transition shadow-lg ${!answers[currentStep]?.trim()
                            ? 'bg-gray-300 cursor-not-allowed shadow-none'
                            : 'bg-button-gradient hover:translate-y-[-1px] shadow-theme'
                            }`}
                    >
                        {submitting ? (
                            <Loader className="animate-spin w-5 h-5" />
                        ) : currentStep === questions.length - 1 ? (
                            <>Complete <CheckCircle className="w-5 h-5" /></>
                        ) : (
                            <>Next <ChevronRight className="w-5 h-5" /></>
                        )}
                    </button>
                </div>
            </footer>
        </div>
    );
}

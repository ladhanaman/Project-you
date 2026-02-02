// src/components/BentoHome.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, Target, TrendingUp, Lightbulb, Sparkles, CheckCircle, Circle, Star } from 'lucide-react';
import { useStore } from '../store/useStore.js';
import { getDashboardSummary } from '../services/apiService.js';
import JourneyProgressCard from './JourneyProgressCard.jsx';
import { ARCHETYPE_IMAGES } from '../data/archetypeImages';


// Bento Grid Homepage Component
export default function BentoHome() {
    const navigate = useNavigate();
    const { user } = useStore();
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [dashboardData, setDashboardData] = useState(null);

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        try {
            setLoading(true);
            setError(null);
            const data = await getDashboardSummary();
            setDashboardData(data);
        } catch (err) {
            console.error('Error fetching dashboard data:', err);
            setError(err.message || 'Failed to load dashboard');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 via-purple-50/30 to-pink-50/30">
                <div className="text-center">
                    <div className="w-16 h-16 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                    <p className="text-gray-600">Loading your dashboard...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 via-purple-50/30 to-pink-50/30 p-4">
                <div className="bg-white rounded-2xl shadow-xl border border-red-200 p-8 max-w-md text-center">
                    <div className="text-red-600 text-5xl mb-4">⚠️</div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-4">Error Loading Dashboard</h2>
                    <p className="text-gray-600 mb-6">{error}</p>
                    <button
                        onClick={fetchDashboardData}
                        className="bg-indigo-600 text-white font-medium py-3 px-6 rounded-xl hover:bg-indigo-700 transition"
                    >
                        Try Again
                    </button>
                </div>
            </div>
        );
    }

    const priData = dashboardData?.pri_scores;
    const journeyData = dashboardData?.journey;
    const archetypeData = dashboardData?.archetype;
    const userName = dashboardData?.user?.first_name || user?.first_name || 'Explorer';

    const progressPercentage = journeyData?.completion_percentage || 0;

    // Animation delay helper
    const getDelay = (index) => ({
        animationDelay: `${index * 100}ms`,
        animationFillMode: 'both' // Ensures opacity:0 is respected before animation starts
    });

    return (
        <div className="min-h-[calc(100vh-80px)] bg-gradient-to-br from-gray-50 via-purple-50/30 to-pink-50/30 px-4 py-4 sm:px-5 sm:py-5">
            {/* Custom Animation Styles */}
            <style>{`
                @keyframes fade-slide-up {
                    from { opacity: 0; transform: translateY(20px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                .animate-fade-slide-up {
                    animation: fade-slide-up 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards; // Apple's easing curve
                    opacity: 0; // Start hidden
                }
            `}</style>

            <div className="max-w-5xl mx-auto">
                {/* Bento Grid Layout - Premium Spacing */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 lg:gap-5 auto-rows-auto">

                    {/* Row 1: Welcome Hero + PRI Scores */}
                    <div className="lg:col-span-2 animate-fade-slide-up" style={getDelay(0)}>
                        <div className="bg-gradient-to-br from-indigo-600 via-purple-600 to-purple-500 rounded-3xl p-6 sm:p-8 text-white shadow-xl h-full flex flex-col justify-center min-h-[180px] sm:min-h-[220px] relative overflow-hidden group">
                            {/* Subtle animated shine effect */}
                            <div className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none" />

                            <h2 className="text-3xl sm:text-4xl font-bold mb-2 tracking-tight">
                                Welcome, {userName}.
                            </h2>
                            <h2 className="text-2xl sm:text-3xl font-bold mb-4 text-purple-100/90">
                                The journey begins with you.
                            </h2>
                            <p className="text-base sm:text-lg text-purple-100/80 mb-8 max-w-lg leading-relaxed">
                                Explore your path, define your purpose, and unlock your potential with clarity and confidence.
                            </p>
                            <div>
                                <button
                                    onClick={() => {
                                        if (priData?.has_completed_assessment) {
                                            navigate('/journey');
                                        } else {
                                            navigate('/assessment/1');
                                        }
                                    }}
                                    className="inline-flex items-center gap-2 bg-white text-indigo-600 px-6 py-3 rounded-full font-bold hover:bg-purple-50 transition-all hover:scale-105 shadow-lg hover:shadow-xl text-sm sm:text-base"
                                >
                                    {priData?.has_completed_assessment ? 'Continue Your Journey' : 'Start Assessment'}
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* PRI Scores Card */}
                    <div className="bg-white/80 backdrop-blur-xl rounded-3xl p-6 sm:p-8 shadow-xl shadow-indigo-100/20 border border-white/60 animate-fade-slide-up hover:scale-[1.02] transition-transform duration-300" style={getDelay(1)}>
                        <h3 className="text-lg font-bold text-gray-900 mb-6 flex items-center gap-2">
                            <Target size={20} className="text-indigo-600" />
                            PRI Scores
                        </h3>
                        {priData?.has_completed_assessment ? (
                            <div className="grid grid-cols-3 gap-4">
                                <PRIScoreCircle
                                    score={priData.purpose_score || 0}
                                    label="Purpose"
                                    sublabel="Meaning"
                                    letter="P"
                                />
                                <PRIScoreCircle
                                    score={priData.relevance_score || 0}
                                    label="Relevance"
                                    sublabel="Impact"
                                    letter="R"
                                />
                                <PRIScoreCircle
                                    score={priData.identity_score || 0}
                                    label="Identity"
                                    sublabel="Self"
                                    letter="I"
                                />
                            </div>
                        ) : (
                            <div className="flex flex-col items-center justify-center h-40 text-center">
                                <p className="text-sm text-gray-500 mb-4 font-medium">Unlock your personalized scores</p>
                                <button
                                    onClick={() => navigate('/assessment/1')}
                                    className="text-sm text-indigo-600 hover:text-indigo-700 font-semibold underline decoration-2 underline-offset-4"
                                >
                                    Begin Assessment →
                                </button>
                            </div>
                        )}
                    </div>

                    {/* Row 2: Journey Progress - New Design */}
                    <div className="lg:col-span-2 animate-fade-slide-up" style={getDelay(2)}>
                        {/* We wrap custom components in our glass container styles if possible, or assume the component handles it. 
                            Since JourneyProgressCard is custom, let's wrap it in a glass container or update it later. 
                            For now, let's trust it fits, or wrap the wrapper. */}
                        <div className="h-full rounded-3xl shadow-xl shadow-purple-100/20 border border-white/60 overflow-hidden">
                            <JourneyProgressCard
                                journeyData={journeyData}
                                progressPercentage={progressPercentage}
                            />
                        </div>
                    </div>

                    {/* Archetype Badge */}
                    <div className="animate-fade-slide-up" style={getDelay(3)}>
                        {archetypeData?.name ? (
                            <div className="bg-gradient-to-br from-blue-400 to-indigo-500 rounded-3xl p-6 sm:p-8 shadow-xl text-white flex flex-col items-center justify-center text-center min-h-[180px] sm:min-h-[220px] overflow-hidden relative group h-full hover:scale-[1.02] transition-transform duration-300">
                                {/* Glossy Overlay */}
                                <div className="absolute inset-0 bg-gradient-to-tr from-white/0 via-white/5 to-white/20 pointer-events-none" />

                                {/* Background Glow */}
                                <div className="absolute top-0 right-0 w-32 h-32 bg-white/20 rounded-full blur-3xl -mr-10 -mt-10 animate-pulse" />

                                <div className="w-24 h-24 mb-4 relative z-10 transition-transform group-hover:scale-110 duration-500 ease-out">
                                    <div className="w-full h-full bg-white/20 backdrop-blur-md rounded-full flex items-center justify-center text-4xl border border-white/30 shadow-inner relative z-10">
                                        <Star className="w-10 h-10 text-white fill-white" />
                                    </div>
                                </div>
                                <h3 className="text-2xl font-bold mb-1 relative z-10 tracking-wide">{archetypeData.name}</h3>
                                <p className="text-blue-100 font-medium relative z-10">
                                    Level {archetypeData.level || 1} • {archetypeData.subtitle || 'Seeker'}
                                </p>
                            </div>
                        ) : (
                            <div className="bg-white/80 backdrop-blur-xl rounded-3xl p-6 sm:p-8 shadow-xl border border-white/60 flex flex-col items-center justify-center text-center h-full min-h-[200px]">
                                <div className="w-16 h-16 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-full flex items-center justify-center mb-4 text-3xl shadow-sm">
                                    ❓
                                </div>
                                <h3 className="text-lg font-bold mb-2 text-gray-800">Your Archetype</h3>
                                <button
                                    onClick={() => navigate('/assessment/1')}
                                    className="text-sm bg-indigo-50 text-indigo-600 px-4 py-2 rounded-lg font-semibold hover:bg-indigo-100 transition"
                                >
                                    Discover Now
                                </button>
                            </div>
                        )}
                    </div>

                    {/* Quote Card */}
                    <div className="animate-fade-slide-up" style={getDelay(4)}>
                        <div className="bg-white/60 backdrop-blur-md rounded-3xl p-8 shadow-lg border border-white/50 flex flex-col justify-center h-full min-h-[160px] hover:bg-white/80 transition-colors duration-300">
                            <Sparkles className="text-amber-400 w-8 h-8 mb-4 opacity-80" />
                            <p className="text-xl font-serif italic text-gray-700 mb-3 leading-relaxed">
                                "The only journey is the one within."
                            </p>
                            <p className="text-sm font-bold text-gray-400 uppercase tracking-widest">— Rainer Maria Rilke</p>
                        </div>
                    </div>

                    {/* Quick Actions Grid */}
                    <div className="lg:col-span-2 animate-fade-slide-up" style={getDelay(5)}>
                        <div className="grid grid-cols-2 gap-3 sm:gap-4 h-full">
                            <QuickActionCard
                                icon={FileText}
                                label="View Report"
                                onClick={() => priData?.latest_submission_id && navigate(`/results/${priData.latest_submission_id}`)}
                                gradient="from-indigo-500 to-purple-600"
                                disabled={!priData?.has_completed_assessment}
                            />
                            <QuickActionCard
                                icon={Target}
                                label="Today's Focus"
                                onClick={() => {
                                    if (journeyData?.has_active_session && journeyData.current_day) {
                                        navigate(`/journey/day/${journeyData.current_day}`);
                                    } else if (priData?.latest_submission_id) {
                                        navigate(`/results/${priData.latest_submission_id}?tab=journey`);
                                    }
                                }}
                                light
                                disabled={!journeyData?.has_active_session && !priData?.latest_submission_id}
                            />
                            <QuickActionCard
                                icon={TrendingUp}
                                label="Track Progress"
                                onClick={() => {/* TODO: Open progress modal */ }}
                                light
                            />
                            <QuickActionCard
                                icon={Lightbulb}
                                label="Insights"
                                onClick={() => {/* TODO: Navigate to insights */ }}
                                light
                            />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

// PRI Score Circle Component - Responsive, matches ResultsPage design
function PRIScoreCircle({ score, label, sublabel, color, letter }) {
    const radius = 28; // Reduced from 35
    const circumference = 2 * Math.PI * radius;
    const strokeDashoffset = circumference - (score / 100) * circumference;

    // Determine color based on score thresholds (like ResultsPage)
    const getScoreColor = () => {
        if (score >= 70) return '#10b981'; // emerald-500 (HIGH)
        if (score >= 40) return '#f59e0b'; // amber-500 (MEDIUM)
        return '#f43f5e'; // rose-500 (LOW)
    };

    const scoreColor = getScoreColor();

    return (
        <div className="flex flex-col items-center">
            <div className="relative w-16 h-16 sm:w-20 sm:h-20 mb-2">
                <svg className="w-full h-full transform -rotate-90">
                    {/* Background circle */}
                    <circle
                        cx="50%"
                        cy="50%"
                        r={radius}
                        stroke="#e5e7eb"
                        strokeWidth="5"
                        fill="none"
                    />
                    {/* Progress circle */}
                    <circle
                        cx="50%"
                        cy="50%"
                        r={radius}
                        stroke={scoreColor}
                        strokeWidth="5"
                        fill="none"
                        strokeDasharray={circumference}
                        strokeDashoffset={strokeDashoffset}
                        strokeLinecap="round"
                        className="transition-all duration-1000"
                    />
                </svg>
                {/* Letter display (P, R, or I) */}
                <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-2xl sm:text-3xl font-bold text-gray-400">
                        {letter}
                    </span>
                </div>
            </div>
            <p className="text-xs sm:text-sm font-semibold text-gray-900 mb-0.5 sm:mb-1 text-center">{label}</p>
            <p className="text-[10px] sm:text-xs text-gray-500 text-center leading-tight px-1 max-w-[90px] sm:max-w-none">
                {sublabel}
            </p>
        </div>
    );
}

// Quick Action Card Component - Responsive
function QuickActionCard({ icon: Icon, label, onClick, gradient, light, disabled }) {
    return (
        <button
            onClick={onClick}
            disabled={disabled}
            className={`rounded-2xl p-4 flex flex-col items-center justify-center gap-2 transition-all min-h-[110px] sm:min-h-[130px] w-full ${disabled ? 'opacity-50 cursor-not-allowed grayscale' :
                gradient
                    ? `bg-gradient-to-br ${gradient} text-white shadow-xl shadow-purple-900/10 hover:scale-[1.03] hover:shadow-2xl`
                    : 'bg-white/80 backdrop-blur-sm text-gray-700 shadow-lg border border-white/60 hover:scale-[1.03] hover:bg-white/95'
                }`}
        >
            <div className={`w-10 h-10 sm:w-12 sm:h-12 rounded-xl sm:rounded-2xl flex items-center justify-center ${gradient ? 'bg-white/20' : 'bg-white'
                }`}>
                <Icon size={24} className={gradient ? 'text-white' : 'text-indigo-600'} />
            </div>
            <span className="text-sm sm:text-base font-semibold text-center leading-tight">{label}</span>
        </button>
    );
}

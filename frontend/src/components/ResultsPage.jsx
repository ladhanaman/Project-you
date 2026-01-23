// src/components/ResultsPage.jsx
import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useStore } from '../store/useStore.js';
import { getSubmission, getReportDownloadUrl, retryReportGeneration, getReflectionSession } from '../services/apiService.js';
import { Download, Loader, CheckCircle, AlertCircle, Award, Target, BookOpen, Briefcase, Home, TrendingUp, TrendingDown, RefreshCw, Clock, Map } from 'lucide-react';
import MainLayout from './MainLayout.jsx';
import { useWebSocket } from '../hooks/useWebSocket.js';

// PRI Components
import PRIScoreChart from './PRIScoreChart.jsx';
import ArchetypeCard from './ArchetypeCard.jsx';
import ReportViewer from './ReportViewer.jsx';
import ReflectionJourney from './ReflectionJourney.jsx';

// Simple inline loading skeleton
const ResultsSkeleton = () => (
    <MainLayout>
        <div className="max-w-5xl mx-auto px-4 py-8">
            <div className="animate-pulse">
                <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
                <div className="h-64 bg-gray-200 rounded mb-6"></div>
                <div className="h-32 bg-gray-200 rounded"></div>
            </div>
        </div>
    </MainLayout>
);

export default function ResultsPage() {
    const { submissionId } = useParams();
    const navigate = useNavigate();
    const { user, submissionDetails, setSubmissionDetails } = useStore();
    const [isPolling, setIsPolling] = useState(true);
    const [pollError, setPollError] = useState(null);
    const [isRetrying, setIsRetrying] = useState(false);

    // PRI specific state
    const [reflectionSession, setReflectionSession] = useState(null);
    const [activeTab, setActiveTab] = useState('report'); // 'report' or 'journey'

    // WebSocket for real-time updates
    const { status: wsStatus, connected: wsConnected } = useWebSocket(submissionId);

    // Update submission details when WebSocket sends status update
    // Update submission details when WebSocket sends status update
    useEffect(() => {
        if (!wsStatus) return;

        console.log('[ResultsPage] WebSocket status update:', wsStatus);

        setSubmissionDetails((prev) => {
            // Safety check: if previous state is null or status matches, don't update
            if (!prev || prev.report_status === wsStatus) {
                return prev;
            }
            return {
                ...prev,
                report_status: wsStatus
            };
        });

        // If status is terminal, stop polling and ensure we have latest data
        if (wsStatus === 'completed' || wsStatus === 'failed' || wsStatus === 'pending_ai') {
            setIsPolling(false);

            // If completed, fetch fresh data to get the generated report content
            if (wsStatus === 'completed') {
                getSubmission(parseInt(submissionId))
                    .then(details => {
                        console.log('[ResultsPage] Fetched fresh details after WebSocket completion');
                        setSubmissionDetails(details);
                    })
                    .catch(err => console.error("Failed to fetch final details", err));
            }
        }
    }, [wsStatus, submissionId, setSubmissionDetails]);

    // Handle retry for pending_ai submissions
    const handleRetry = async () => {
        setIsRetrying(true);
        setPollError(null);
        try {
            await retryReportGeneration(parseInt(submissionId));
            // Start polling again after retry
            setIsPolling(true);
        } catch (err) {
            setPollError(err.message);
        } finally {
            setIsRetrying(false);
        }
    };

    const pollSubmission = useCallback(async () => {
        if (!submissionId) return;

        try {
            const details = await getSubmission(parseInt(submissionId));
            setSubmissionDetails(details);

            if (details.report_status === 'completed' || details.report_status === 'failed' || details.report_status === 'pending_ai') {
                setIsPolling(false);

                // If completed and it's a PRI submission, fetch reflection session
                if (details.report_status === 'completed' && (details.archetype || details.pri_report_md)) {
                    try {
                        const session = await getReflectionSession(parseInt(submissionId));
                        setReflectionSession(session);
                    } catch (e) {
                        console.error("Failed to fetch reflection session", e);
                    }
                }
            }
        } catch (err) {
            setPollError(err.message);
        }
    }, [submissionId, setSubmissionDetails]);

    useEffect(() => {
        let isMounted = true;
        // Use slower polling when WebSocket is connected (as fallback)
        let pollInterval = wsConnected ? 10000 : 5000; // 10s with WS, 5s without
        const maxInterval = 30000;
        const maxAttempts = wsConnected ? 10 : 20; // Fewer attempts with WebSocket

        // Separate polling for reflection session
        let sessionPollInterval = null;
        let sessionPollAttempts = 0;
        const maxSessionAttempts = 6; // Poll for 30 seconds (5s * 6)

        const pollReflectionSession = async () => {
            if (!isMounted || !submissionId) return false;

            try {
                const session = await getReflectionSession(parseInt(submissionId));
                if (isMounted && session) {
                    setReflectionSession(session);
                    return true; // Success
                }
            } catch (e) {
                // Only log if it's a real error, not just 404/pending
                if (e.response && e.response.status !== 404) {
                    console.log('Reflection session check failed:', e.message);
                }
                return false; // Not ready yet
            }
            return false;
        };

        const startSessionPolling = () => {
            // Try immediately first
            pollReflectionSession().then(success => {
                if (success || !isMounted) return;

                // If not successful, start polling
                sessionPollInterval = setInterval(async () => {
                    sessionPollAttempts++;

                    const success = await pollReflectionSession();

                    if (success || sessionPollAttempts >= maxSessionAttempts) {
                        clearInterval(sessionPollInterval);
                        if (!success) {
                            console.warn('Reflection session polling stopped after max attempts');
                        }
                    }
                }, 5000); // Poll every 5 seconds
            });
        };

        const poll = async () => {
            if (!isMounted || !submissionId) return;

            try {
                const details = await getSubmission(parseInt(submissionId));
                if (!isMounted) return;

                setSubmissionDetails(details);

                if (details.report_status === 'completed' || details.report_status === 'failed' || details.report_status === 'pending_ai') {
                    setIsPolling(false);

                    // If completed and it's a PRI submission, start polling for reflection session
                    if (details.report_status === 'completed' && (details.archetype || details.pri_report_md)) {
                        startSessionPolling();
                    }
                } else {
                    // Increase interval (exponential backoff)
                    pollInterval = Math.min(pollInterval * 1.2, maxInterval);

                    // Schedule next poll only if still processing
                    if (isPolling && isMounted) {
                        setTimeout(poll, pollInterval);
                    }
                }
            } catch (err) {
                if (isMounted) {
                    setPollError(err.message);
                    // Backoff on error too
                    pollInterval = Math.min(pollInterval * 1.5, maxInterval);

                    // Retry with backoff
                    if (isPolling && isMounted) {
                        setTimeout(poll, pollInterval);
                    }
                }
            }
        };

        // Start polling
        poll();

        return () => {
            isMounted = false;
            if (sessionPollInterval) {
                clearInterval(sessionPollInterval);
            }
        };
    }, [isPolling, submissionId, setSubmissionDetails]);

    const handleDownloadPDF = () => {
        if (submissionId) {
            const url = getReportDownloadUrl(parseInt(submissionId));
            const token = localStorage.getItem('token');

            fetch(url, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache'
                }
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Failed to download report');
                    }
                    return response.blob();
                })
                .then(blob => {
                    const blobUrl = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = blobUrl;
                    a.download = `project-you-report-${submissionId}.pdf`;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(blobUrl);
                    document.body.removeChild(a);
                })
                .catch(err => {
                    console.error('PDF download failed:', err);
                    setPollError('Failed to download PDF. Please try again.');
                });
        }
    };

    const getStatusBadge = () => {
        const status = submissionDetails?.report_status || 'processing';

        switch (status) {
            case 'completed':
                return (
                    <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-green-100 text-green-700 text-sm font-medium">
                        <CheckCircle size={16} />
                        Report Ready
                    </span>
                );
            case 'failed':
                return (
                    <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-red-100 text-red-700 text-sm font-medium">
                        <AlertCircle size={16} />
                        Report Failed
                    </span>
                );
            case 'pending_ai':
                return (
                    <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-amber-100 text-amber-700 text-sm font-medium">
                        <Clock size={16} />
                        Pending Generation
                    </span>
                );
            default:
                return (
                    <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-blue-100 text-blue-700 text-sm font-medium">
                        <Loader size={16} className="animate-spin" />
                        Generating Report...
                    </span>
                );
        }
    };

    if (!submissionDetails) {
        return <ResultsSkeleton />;
    }

    // Determine if this is a PRI assessment or legacy
    const isPRIAssessment = !!(submissionDetails.archetype || submissionDetails.pri_report_md);

    return (
        <MainLayout>
            <div className="max-w-4xl mx-auto">
                <div className="text-center mb-12">
                    <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 mb-2">
                        {isPRIAssessment ? "Meet Yourself Report" : "Assessment Complete"}
                    </h1>
                    <p className="text-slate-500 text-lg">
                        {isPRIAssessment
                            ? `Welcome to your authentic self, ${user?.full_name?.split(' ')[0] || 'friend'}.`
                            : `Here are your results, ${user?.full_name}.`
                        }
                    </p>
                </div>

                <div className="flex justify-center mb-10">
                    {getStatusBadge()}
                </div>

                {!isPRIAssessment && (
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
                        <ScoreCard
                            title="Fundamentals"
                            score={submissionDetails.fundamentals_score}
                            maxScore={100}
                        />
                        <ScoreCard
                            title="Applied Knowledge"
                            score={submissionDetails.applied_score}
                            maxScore={100}
                        />
                        <ScoreCard
                            title="Industry Orientation"
                            score={submissionDetails.industry_score}
                            maxScore={100}
                        />
                        <ScoreCard
                            title="Total Score"
                            score={submissionDetails.total_score}
                            maxScore={300}
                            percentage={Math.round((submissionDetails.total_score / 300) * 100)}
                            isTotal
                        />
                    </div>
                )}

                {(submissionDetails?.report_status === 'completed' || submissionDetails?.report_status === 'failed') && (
                    <>
                        {isPRIAssessment ? (
                            <PRIReportView
                                submissionDetails={submissionDetails}
                                reflectionSession={reflectionSession}
                                activeTab={activeTab}
                                setActiveTab={setActiveTab}
                                handleDownloadPDF={handleDownloadPDF}
                                navigate={navigate}
                                user={user}
                            />
                        ) : (
                            <LegacyReportContent submissionDetails={submissionDetails} />
                        )}
                    </>
                )}

                {isPolling && submissionDetails?.report_status === 'processing' && (
                    <div className="bg-white rounded-2xl border border-slate-200 p-8 mb-8 text-center shadow-sm">
                        <Loader className="animate-spin mx-auto mb-4 text-slate-400" size={32} />
                        <h3 className="text-lg font-semibold text-slate-800 mb-2">
                            {isPRIAssessment ? "Analyzing Your Psyche" : "Generating Report"}
                        </h3>
                        <p className="text-slate-500">
                            {isPRIAssessment
                                ? "We're calculating your Purpose, Relevance, and Identity scores to generate your personalized archetype..."
                                : "Analyzing your responses to generate detailed insights..."}
                        </p>
                    </div>
                )}

                {submissionDetails?.report_status === 'pending_ai' && (
                    <div className="bg-gradient-to-r from-amber-50 to-orange-50 rounded-2xl border border-amber-200 p-8 mb-8 text-center shadow-sm">
                        <div className="mx-auto w-16 h-16 bg-amber-100 rounded-full flex items-center justify-center mb-4">
                            <Clock className="w-8 h-8 text-amber-600" />
                        </div>
                        <h3 className="text-xl font-semibold text-slate-800 mb-2">
                            Your Report is Being Prepared
                        </h3>
                        <p className="text-slate-600 mb-6 max-w-md mx-auto">
                            We're experiencing high demand right now. Click below to generate your personalized report with AI-powered insights.
                        </p>
                        <button
                            onClick={handleRetry}
                            disabled={isRetrying}
                            className="inline-flex items-center gap-2 px-6 py-3 bg-amber-600 hover:bg-amber-700 disabled:bg-amber-400 text-white font-medium rounded-xl transition shadow-sm hover:shadow-md"
                        >
                            {isRetrying ? (
                                <>
                                    <Loader className="animate-spin" size={18} />
                                    Generating...
                                </>
                            ) : (
                                <>
                                    <RefreshCw size={18} />
                                    Generate Report Now
                                </>
                            )}
                        </button>
                    </div>
                )}

                {pollError && (
                    <div className="bg-red-50 border border-red-100 text-red-600 px-6 py-4 rounded-xl mb-8">
                        <p className="font-medium">Error loading report details</p>
                        <p className="text-sm mt-1">{pollError}</p>
                    </div>
                )}

                {!isPRIAssessment && (
                    <div className="flex flex-col sm:flex-row gap-4 justify-center">
                        {submissionDetails?.pdf_generated && (
                            <button
                                onClick={handleDownloadPDF}
                                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-8 py-3.5 bg-button-gradient text-white font-medium rounded-xl transition shadow-sm hover:shadow-md"
                            >
                                <Download size={18} />
                                Download PDF Report
                            </button>
                        )}
                        <button
                            onClick={() => navigate('/dashboard')}
                            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-8 py-3.5 bg-white hover:bg-accent-lighter text-gray-900 font-medium rounded-xl transition shadow-sm hover:shadow-md border border-theme"
                        >
                            <Home size={18} />
                            Back to Dashboard
                        </button>
                    </div>
                )}
            </div>
        </MainLayout>
    );
}

function ScoreCard({ title, score, maxScore, percentage, isTotal = false }) {
    const pct = percentage ?? Math.round((score / maxScore) * 100);

    return (
        <div className={`rounded-2xl p-6 flex flex-col items-center justify-center text-center transition-all ${isTotal
            ? 'bg-slate-900 text-white shadow-md'
            : 'bg-white border border-slate-200 shadow-sm'
            }`}>
            <p className={`text-xs font-semibold uppercase tracking-wider mb-3 ${isTotal ? 'text-slate-400' : 'text-slate-500'}`}>
                {title}
            </p>
            <div className="flex items-baseline gap-1 mb-2">
                <span className="text-3xl font-bold">{score}</span>
                <span className={`text-sm ${isTotal ? 'text-slate-500' : 'text-slate-400'}`}>/{maxScore}</span>
            </div>
            <div className={`text-xs font-medium px-2 py-1 rounded-full ${isTotal ? 'bg-slate-800 text-slate-300' : 'bg-slate-50 text-slate-600'
                }`}>
                {pct}%
            </div>
        </div>
    );
}

function SectionInsights({ title, insights, icon }) {
    return (
        <div className="bg-white border border-theme rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center gap-3 mb-6">
                <div className="p-2 bg-accent-lighter rounded-lg border border-accent-light">
                    {icon}
                </div>
                <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Opportunities */}
                {insights.opportunities && insights.opportunities.length > 0 && (
                    <div>
                        <div className="flex items-center gap-2 mb-3">
                            <TrendingUp className="text-green-600" size={18} />
                            <h4 className="font-semibold text-green-700">Opportunities</h4>
                        </div>
                        <ul className="list-disc pl-5 space-y-2">
                            {insights.opportunities.map((item, i) => (
                                <li key={i} className="text-slate-600 leading-relaxed text-sm">{item}</li>
                            ))}
                        </ul>
                    </div>
                )}

                {/* Work Towards */}
                {insights.work_towards && insights.work_towards.length > 0 && (
                    <div>
                        <div className="flex items-center gap-2 mb-3">
                            <TrendingDown className="text-orange-600" size={18} />
                            <h4 className="font-semibold text-orange-700">Work Towards</h4>
                        </div>
                        <ul className="list-disc pl-5 space-y-2">
                            {insights.work_towards.map((item, i) => (
                                <li key={i} className="text-slate-600 leading-relaxed text-sm">{item}</li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>
        </div>
    );
}

function PRIReportView({ submissionDetails, reflectionSession, activeTab, setActiveTab, handleDownloadPDF, navigate, user }) {
    return (
        <div className="space-y-6">
            {/* Archetype Card - Full Width */}
            <ArchetypeCard
                archetype={submissionDetails.archetype}
                displayArchetype={submissionDetails.display_archetype}
            />

            {/* Score Chart - Full Width */}
            {(submissionDetails.purpose_score !== null && submissionDetails.purpose_score !== undefined) && (
                <PRIScoreChart scores={{
                    purpose: submissionDetails.purpose_score || 0,
                    relevance: submissionDetails.relevance_score || 0,
                    identity: submissionDetails.identity_score || 0
                }} />
            )}

            {/* Tabs for Report vs Journey */}
            <div className="flex justify-center border-b border-gray-200 mt-8 overflow-x-auto">
                <nav className="flex space-x-8 min-w-max px-4" aria-label="Tabs">
                    <button
                        onClick={() => setActiveTab('report')}
                        className={`
                            flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors
                            ${activeTab === 'report'
                                ? 'border-accent text-accent'
                                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}
                        `}
                    >
                        <BookOpen className="w-4 h-4" />
                        Full Report
                    </button>
                    <button
                        onClick={() => setActiveTab('journey')}
                        className={`
                            flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors
                            ${activeTab === 'journey'
                                ? 'border-accent text-accent'
                                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}
                        `}
                    >
                        <Map className="w-4 h-4" />
                        7-Day Reflection Journey
                    </button>
                </nav>
            </div>

            {/* Tab Content */}
            <div className="min-h-[400px]">
                {activeTab === 'report' ? (
                    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 sm:p-8">
                        <ReportViewer markdownContent={submissionDetails.pri_report_md} />
                    </div>
                ) : (
                    <ReflectionJourney session={reflectionSession} />
                )}
            </div>

            {/* Actions */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center pt-8 border-t border-gray-100">
                <button
                    onClick={handleDownloadPDF}
                    className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 bg-button-gradient text-white font-medium rounded-xl transition shadow-sm hover:shadow-md"
                >
                    <Download size={18} />
                    Download PDF Report
                </button>
                <button
                    onClick={() => navigate('/dashboard')}
                    className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 bg-white hover:bg-accent-lighter text-gray-900 font-medium rounded-xl transition shadow-sm hover:shadow-md border border-theme"
                >
                    <Home size={18} />
                    Back to Dashboard
                </button>
            </div>
        </div>
    );
}

// Extracted Legacy Content for cleaner main component
function LegacyReportContent({ submissionDetails }) {
    return (
        <div className="space-y-6">
            {/* Industry Readiness Level */}
            {submissionDetails.industry_readiness_level && (
                <div className="bg-white border border-theme rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow text-center">
                    <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-2">Industry Readiness Level</h3>
                    <div className="text-2xl font-bold text-slate-900 mb-2">{submissionDetails.industry_readiness_level}</div>
                    {submissionDetails.readiness_level_justification && (
                        <p className="text-slate-600 text-sm max-w-2xl mx-auto">{submissionDetails.readiness_level_justification}</p>
                    )}
                </div>
            )}

            {/* Section Insights */}
            {submissionDetails.fundamentals_insights && (
                <SectionInsights
                    title="Section 1: Fundamentals"
                    insights={submissionDetails.fundamentals_insights}
                    icon={<Award className="text-blue-600" size={20} />}
                />
            )}
            {submissionDetails.applied_insights && (
                <SectionInsights
                    title="Section 2: Applied Knowledge"
                    insights={submissionDetails.applied_insights}
                    icon={<Target className="text-green-600" size={20} />}
                />
            )}
            {submissionDetails.industry_insights && (
                <SectionInsights
                    title="Section 3: Industry Orientation"
                    insights={submissionDetails.industry_insights}
                    icon={<Briefcase className="text-accent" size={20} />}
                />
            )}

            {/* 4-Week Learning Plan */}
            {submissionDetails.learning_plan_weeks && submissionDetails.learning_plan_weeks.length > 0 && (
                <div className="bg-white border border-theme rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="p-2 bg-accent-lighter rounded-lg border border-accent-light">
                            <BookOpen className="text-slate-700" size={20} />
                        </div>
                        <h3 className="text-lg font-semibold text-slate-900">Personalized 4-Week Learning Plan</h3>
                    </div>
                    <div className="space-y-6">
                        {submissionDetails.learning_plan_weeks.map((week, index) => (
                            <div key={index} className="border-l-4 border-blue-500 bg-slate-50 p-5 rounded-r-lg">
                                <div className="font-semibold text-slate-900 text-lg mb-3">Week {index + 1}: {week.focus_area}</div>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
                                    <div className="text-sm text-slate-600">
                                        <strong className="block text-slate-800 mb-1">Tasks:</strong>
                                        {week.tasks}
                                    </div>
                                    <div className="text-sm text-slate-600">
                                        <strong className="block text-slate-800 mb-1">Goal:</strong>
                                        {week.expected_outcome}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

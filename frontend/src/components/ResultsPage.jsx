// src/components/ResultsPage.jsx
import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useStore } from '../store/useStore.js';
import { getSubmission, getReportDownloadUrl, retryReportGeneration } from '../services/apiService.js';
import { Download, Loader, CheckCircle, AlertCircle, Award, Target, BookOpen, Briefcase, Home, TrendingUp, TrendingDown, RefreshCw, Clock } from 'lucide-react';
import MainLayout from './MainLayout.jsx';
import { ResultsSkeleton } from './Skeleton.jsx';

export default function ResultsPage() {
    const { submissionId } = useParams();
    const navigate = useNavigate();
    const { user, submissionDetails, setSubmissionDetails } = useStore();
    const [isPolling, setIsPolling] = useState(true);
    const [pollError, setPollError] = useState(null);
    const [isRetrying, setIsRetrying] = useState(false);

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
            }
        } catch (err) {
            setPollError(err.message);
        }
    }, [submissionId, setSubmissionDetails]);

    useEffect(() => {
        let isMounted = true;
        let pollInterval = 3000; // Start at 3s (faster than old 5s)
        const maxInterval = 30000; // Cap at 30s
        const maxAttempts = 20; // Stop after ~100 seconds total

        const poll = async () => {
            if (!isMounted || !submissionId) return;

            try {
                const details = await getSubmission(parseInt(submissionId));
                if (!isMounted) return;

                setSubmissionDetails(details);

                if (details.report_status === 'completed' || details.report_status === 'failed' || details.report_status === 'pending_ai') {
                    setIsPolling(false);
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
                    a.download = `thinkbinary-report-${submissionId}.pdf`;
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

    return (
        <MainLayout>
            <div className="max-w-4xl mx-auto">
                <div className="text-center mb-12">
                    <h1 className="text-3xl font-bold text-slate-900 mb-2">Assessment Complete</h1>
                    <p className="text-slate-500 text-lg">Here are your results, {user?.full_name}.</p>
                </div>

                <div className="flex justify-center mb-10">
                    {getStatusBadge()}
                </div>

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

                {(submissionDetails?.report_status === 'completed' || submissionDetails?.report_status === 'failed') && (
                    <div className="space-y-6 mb-12">
                        {/* Industry Readiness Level */}
                        {submissionDetails.industry_readiness_level && (
                            <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow text-center">
                                <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-2">Industry Readiness Level</h3>
                                <div className="text-2xl font-bold text-slate-900 mb-2">{submissionDetails.industry_readiness_level}</div>
                                {submissionDetails.readiness_level_justification && (
                                    <p className="text-slate-600 text-sm max-w-2xl mx-auto">{submissionDetails.readiness_level_justification}</p>
                                )}
                            </div>
                        )}

                        {/* Section 1: Fundamentals */}
                        {submissionDetails.fundamentals_insights && (
                            <SectionInsights
                                title="Section 1: Fundamentals"
                                insights={submissionDetails.fundamentals_insights}
                                icon={<Award className="text-blue-600" size={20} />}
                            />
                        )}

                        {/* Section 2: Applied Knowledge */}
                        {submissionDetails.applied_insights && (
                            <SectionInsights
                                title="Section 2: Applied Knowledge"
                                insights={submissionDetails.applied_insights}
                                icon={<Target className="text-green-600" size={20} />}
                            />
                        )}

                        {/* Section 3: Industry Orientation */}
                        {submissionDetails.industry_insights && (
                            <SectionInsights
                                title="Section 3: Industry Orientation"
                                insights={submissionDetails.industry_insights}
                                icon={<Briefcase className="text-purple-600" size={20} />}
                            />
                        )}

                        {/* 4-Week Learning Plan */}
                        {submissionDetails.learning_plan_weeks && submissionDetails.learning_plan_weeks.length > 0 && (
                            <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
                                <div className="flex items-center gap-3 mb-6">
                                    <div className="p-2 bg-slate-50 rounded-lg border border-slate-100">
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

                                            {/* Deliverables & Validation (New Fields) */}
                                            {(week.deliverables || week.validation) && (
                                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-3 border-t border-slate-200 mt-3">
                                                    {week.deliverables && week.deliverables.length > 0 && (
                                                        <div className="text-sm">
                                                            <strong className="block text-slate-800 mb-1">Deliverables:</strong>
                                                            <ul className="list-disc pl-4 text-slate-600">
                                                                {week.deliverables.map((d, i) => <li key={i}>{d}</li>)}
                                                            </ul>
                                                        </div>
                                                    )}
                                                    {week.validation && week.validation.length > 0 && (
                                                        <div className="text-sm">
                                                            <strong className="block text-slate-800 mb-1">Validation:</strong>
                                                            <ul className="list-disc pl-4 text-slate-600">
                                                                {week.validation.map((v, i) => <li key={i}>{v}</li>)}
                                                            </ul>
                                                        </div>
                                                    )}
                                                </div>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Project Recommendations (Enhanced) */}
                        {submissionDetails.project_recommendations && submissionDetails.project_recommendations.length > 0 && (
                            <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
                                <div className="flex items-center gap-3 mb-6">
                                    <div className="p-2 bg-slate-50 rounded-lg border border-slate-100">
                                        <Target className="text-slate-700" size={20} />
                                    </div>
                                    <h3 className="text-lg font-semibold text-slate-900">Project Recommendations</h3>
                                </div>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    {submissionDetails.project_recommendations.map((project, index) => {
                                        // Handle both string (legacy) and object (new) formats
                                        const isObject = typeof project === 'object' && project !== null;
                                        const title = isObject ? project.title : `Project ${index + 1}`;
                                        const description = isObject ? project.description : project;
                                        const tags = isObject ? project.addresses_tags : [];
                                        const time = isObject ? project.time_estimate : null;

                                        return (
                                            <div key={index} className="bg-slate-50 rounded-xl p-5 border border-slate-100 flex flex-col h-full">
                                                <h4 className="font-semibold text-slate-900 mb-2">{title}</h4>
                                                <p className="text-sm text-slate-600 mb-4 flex-grow">{description}</p>

                                                {tags && tags.length > 0 && (
                                                    <div className="flex flex-wrap gap-2 mb-3">
                                                        {tags.map((tag, tIndex) => (
                                                            <span key={tIndex} className="text-xs px-2 py-1 bg-white border border-slate-200 rounded-md text-slate-500">
                                                                #{tag}
                                                            </span>
                                                        ))}
                                                    </div>
                                                )}

                                                {time && (
                                                    <div className="text-xs text-slate-500 font-medium pt-3 border-t border-slate-200 mt-auto">
                                                        ⏱ Estimated time: {time}
                                                    </div>
                                                )}
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        )}

                        {/* Role Fit (Enhanced) */}
                        {submissionDetails.role_fit && (
                            <div className="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-2xl p-6 shadow-sm">
                                <div className="flex items-center gap-3 mb-4">
                                    <div className="p-2 bg-white rounded-lg border border-blue-200">
                                        <Briefcase className="text-blue-600" size={20} />
                                    </div>
                                    <h3 className="text-lg font-semibold text-slate-900">Suggested Role Fit</h3>
                                </div>

                                {(() => {
                                    // Parse role_fit if it's a JSON string, or use as is if string/object
                                    let roles = submissionDetails.role_fit;
                                    try {
                                        if (typeof roles === 'string' && (roles.startsWith('[') || roles.startsWith('{'))) {
                                            roles = JSON.parse(roles);
                                        }
                                    } catch (e) {
                                        console.warn("Could not parse role_fit JSON", e);
                                    }

                                    if (Array.isArray(roles)) {
                                        return (
                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                {roles.map((role, idx) => (
                                                    <div key={idx} className="bg-white/60 p-4 rounded-xl border border-blue-100">
                                                        <h4 className="font-semibold text-blue-900 mb-1">
                                                            {role.job_title || role.title || "Recommended Role"}
                                                        </h4>
                                                        <p className="text-sm text-slate-700 leading-relaxed">
                                                            {role.role_description || role.description || JSON.stringify(role)}
                                                        </p>
                                                    </div>
                                                ))}
                                            </div>
                                        );
                                    } else {
                                        // Legacy string format
                                        return <p className="text-slate-700 leading-relaxed">{String(roles)}</p>;
                                    }
                                })()}
                            </div>
                        )}
                    </div>
                )}

                {isPolling && submissionDetails?.report_status === 'processing' && (
                    <div className="bg-white rounded-2xl border border-slate-200 p-8 mb-8 text-center shadow-sm">
                        <Loader className="animate-spin mx-auto mb-4 text-slate-400" size={32} />
                        <h3 className="text-lg font-semibold text-slate-800 mb-2">Generating Report</h3>
                        <p className="text-slate-500">
                            Analyzing your responses to generate detailed insights...
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

                <div className="flex gap-4 justify-center">
                    {submissionDetails?.pdf_generated && (
                        <button
                            onClick={handleDownloadPDF}
                            className="inline-flex items-center gap-2 px-8 py-3.5 bg-slate-900 hover:bg-slate-800 text-white font-medium rounded-xl transition shadow-sm hover:shadow-md"
                        >
                            <Download size={18} />
                            Download PDF Report
                        </button>
                    )}
                    <button
                        onClick={() => navigate('/dashboard')}
                        className="inline-flex items-center gap-2 px-8 py-3.5 bg-white hover:bg-slate-50 text-slate-900 font-medium rounded-xl transition shadow-sm hover:shadow-md border border-slate-200"
                    >
                        <Home size={18} />
                        Back to Dashboard
                    </button>
                </div>
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
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center gap-3 mb-6">
                <div className="p-2 bg-slate-50 rounded-lg border border-slate-100">
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

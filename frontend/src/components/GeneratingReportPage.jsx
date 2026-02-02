// src/components/GeneratingReportPage.jsx
import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useStore } from '../store/useStore.js';
import { getSubmission, retryReportGeneration } from '../services/apiService.js';
import { Loader, Clock, RefreshCw } from 'lucide-react';
import MainLayout from './MainLayout.jsx';
import { useWebSocket } from '../hooks/useWebSocket.js';

export default function GeneratingReportPage() {
    const { submissionId } = useParams();
    const navigate = useNavigate();
    const { setSubmissionDetails } = useStore();
    const [isPolling, setIsPolling] = useState(true);
    const [pollError, setPollError] = useState(null);
    const [isRetrying, setIsRetrying] = useState(false);
    const [status, setStatus] = useState('processing');
    const [isPRIAssessment, setIsPRIAssessment] = useState(true); // Default assumption, will update on fetch

    // WebSocket for real-time updates
    const { status: wsStatus, connected: wsConnected } = useWebSocket(submissionId);

    // Initial fetch to determine type and current status
    useEffect(() => {
        if (submissionId) {
            getSubmission(parseInt(submissionId))
                .then(details => {
                    setStatus(details.report_status);
                    setSubmissionDetails(details);
                    setIsPRIAssessment(!!(details.archetype || details.pri_report_md || details.answers)); // Crude check, mostly to separate from legacy

                    if (details.report_status === 'completed') {
                        navigate(`/results/${submissionId}`, { replace: true });
                    } else if (details.report_status === 'failed') {
                        // Stay here to show error or redirect to results to show failure? 
                        // Let's redirect to results and let results handle failure state
                        navigate(`/results/${submissionId}`, { replace: true });
                    }
                })
                .catch(err => setPollError(err.message));
        }
    }, [submissionId, navigate, setSubmissionDetails]);

    // Update status when WebSocket sends update
    useEffect(() => {
        if (!wsStatus) return;

        setStatus(wsStatus);

        if (wsStatus === 'completed' || wsStatus === 'failed') {
            setIsPolling(false);
            // Small delay to let user see "Completed" before switching? 
            // Or instant. Instant is better for "no flicker" but might be jarring if they are reading.
            // Let's go instant for now as per user request for "direct open".
            navigate(`/results/${submissionId}`, { replace: true });
        }
    }, [wsStatus, submissionId, navigate]);

    // Polling fallback
    useEffect(() => {
        let isMounted = true;
        let pollInterval = wsConnected ? 10000 : 3000; // Fast poll (3s) if no WS
        const maxInterval = 10000;

        const poll = async () => {
            if (!isMounted || !submissionId || !isPolling) return;

            try {
                const details = await getSubmission(parseInt(submissionId));
                if (!isMounted) return;

                setStatus(details.report_status);
                setSubmissionDetails(details);

                if (details.report_status === 'completed' || details.report_status === 'failed') {
                    setIsPolling(false);
                    navigate(`/results/${submissionId}`, { replace: true });
                } else {
                    // Schedule next poll
                    if (isPolling && isMounted) {
                        setTimeout(poll, pollInterval);
                    }
                }
            } catch (err) {
                if (isMounted) {
                    console.error("Poll error", err);
                    // Retry with backoff
                    if (isPolling && isMounted) {
                        setTimeout(poll, 5000);
                    }
                }
            }
        };

        // Start polling if we are polling and status isn't terminal
        if (isPolling && status !== 'completed' && status !== 'failed') {
            poll();
        }

        return () => {
            isMounted = false;
        };
    }, [isPolling, submissionId, navigate, setSubmissionDetails, wsConnected, status]);

    const handleRetry = async () => {
        setIsRetrying(true);
        setPollError(null);
        try {
            await retryReportGeneration(parseInt(submissionId));
            setStatus('processing');
            setIsPolling(true);
        } catch (err) {
            setPollError(err.message);
        } finally {
            setIsRetrying(false);
        }
    };

    return (
        <MainLayout>
            <div className="max-w-4xl mx-auto px-4 py-12">
                <div className="text-center mb-12">
                    <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 mb-2">
                        {isPRIAssessment ? "Generating Your Report" : "Processing Results"}
                    </h1>
                </div>

                {status === 'pending_ai' ? (
                    <div className="bg-gradient-to-r from-amber-50 to-orange-50 rounded-2xl border border-amber-200 p-12 text-center shadow-sm max-w-2xl mx-auto">
                        <div className="mx-auto w-20 h-20 bg-amber-100 rounded-full flex items-center justify-center mb-6">
                            <Clock className="w-10 h-10 text-amber-600" />
                        </div>
                        <h3 className="text-2xl font-semibold text-slate-800 mb-4">
                            Your Report is Being Prepared
                        </h3>
                        <p className="text-slate-600 mb-8 max-w-lg mx-auto text-lg">
                            We're experiencing high demand right now. Click below to generate your personalized report with AI-powered insights.
                        </p>
                        <button
                            onClick={handleRetry}
                            disabled={isRetrying}
                            className="inline-flex items-center gap-2 px-8 py-4 bg-amber-600 hover:bg-amber-700 disabled:bg-amber-400 text-white font-medium rounded-xl transition shadow-sm hover:shadow-md text-lg"
                        >
                            {isRetrying ? (
                                <>
                                    <Loader className="animate-spin" size={24} />
                                    Generating...
                                </>
                            ) : (
                                <>
                                    <RefreshCw size={24} />
                                    Generate Report Now
                                </>
                            )}
                        </button>
                        {pollError && (
                            <p className="text-red-600 mt-4">{pollError}</p>
                        )}
                    </div>
                ) : (
                    <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center shadow-sm max-w-2xl mx-auto">
                        <Loader className="animate-spin mx-auto mb-6 text-indigo-600" size={48} />
                        <h3 className="text-xl font-semibold text-slate-800 mb-3">
                            {isPRIAssessment ? "Analyzing Your Psyche" : "Generating Report"}
                        </h3>
                        <p className="text-slate-500 text-lg">
                            {isPRIAssessment
                                ? "We're calculating your Purpose, Relevance, and Identity scores to generate your personalized archetype..."
                                : "Analyzing your responses to generate detailed insights..."}
                        </p>

                        <div className="mt-8 w-full bg-gray-100 rounded-full h-2.5 dark:bg-gray-700 overflow-hidden">
                            <div className="bg-indigo-600 h-2.5 rounded-full animate-progress-indeterminate"></div>
                        </div>
                    </div>
                )}
            </div>
        </MainLayout>
    );
}

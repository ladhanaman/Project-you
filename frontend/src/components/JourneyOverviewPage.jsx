// src/components/JourneyOverviewPage.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getReflectionSession, getPRIReport, getSubmission } from '../services/apiService.js';
import { Sparkles, Home, ArrowLeft } from 'lucide-react';
import { useStore } from '../store/useStore.js';
import ReflectionJourney from './ReflectionJourney.jsx';

export default function JourneyOverviewPage() {
    const navigate = useNavigate();
    const { user } = useStore();
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [session, setSession] = useState(null);
    const [submissionId, setSubmissionId] = useState(null);

    useEffect(() => {
        fetchJourneyData();
    }, []);

    const fetchJourneyData = async () => {
        try {
            setLoading(true);
            setError(null);

            // Get user's latest submission to find the journey session
            const response = await fetch('/api/submissions', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            const submissions = await response.json();

            if (submissions && submissions.length > 0) {
                const latestSubmission = submissions[0];
                setSubmissionId(latestSubmission.id);

                // Fetch reflection session
                const sessionData = await getReflectionSession(latestSubmission.id);
                setSession(sessionData);
            } else {
                setError('No assessment found. Please complete your PRI assessment first.');
            }
        } catch (err) {
            console.error('Error fetching journey data:', err);
            setError(err.message || 'Failed to load your journey. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-gray-50 via-purple-50/30 to-pink-50/30 flex items-center justify-center p-4">
                <div className="text-center">
                    <div className="w-16 h-16 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                    <p className="text-gray-600">Loading your journey...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-gray-50 via-purple-50/30 to-pink-50/30 flex items-center justify-center p-4">
                <div className="bg-white rounded-2xl shadow-xl border border-red-200 p-8 max-w-md text-center">
                    <div className="text-red-600 text-5xl mb-4">⚠️</div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-4">Journey Not Available</h2>
                    <p className="text-gray-600 mb-6">{error}</p>
                    <div className="flex gap-3 justify-center">
                        <button
                            onClick={fetchJourneyData}
                            className="bg-indigo-600 text-white font-medium py-3 px-6 rounded-xl hover:bg-indigo-700 transition"
                        >
                            Try Again
                        </button>
                        <button
                            onClick={() => navigate('/home')}
                            className="bg-gray-100 text-gray-700 font-medium py-3 px-6 rounded-xl hover:bg-gray-200 transition"
                        >
                            Back to Home
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 via-purple-50/30 to-pink-50/30">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
                {/* Header */}
                <div className="mb-6">
                    <button
                        onClick={() => navigate('/home')}
                        className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 font-medium mb-4 transition"
                    >
                        <ArrowLeft size={20} />
                        Back to Home
                    </button>

                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-2">
                                Your Journey
                            </h1>
                            <p className="text-gray-600">
                                Complete your personalized 7-day reflection journey
                            </p>
                        </div>
                    </div>
                </div>

                {/* Journey Content */}
                <ReflectionJourney session={session} />
            </div>
        </div>
    );
}

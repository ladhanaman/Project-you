// src/components/ForgotPassword.jsx
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Mail, ArrowLeft, CheckCircle, AlertCircle } from 'lucide-react';
import { requestPasswordReset } from '../services/apiService.js';

export default function ForgotPassword() {
    const [email, setEmail] = useState('');
    const [sent, setSent] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [errorType, setErrorType] = useState(''); // 'network' or 'server'

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setErrorType('');
        setLoading(true);

        try {
            await requestPasswordReset(email);
            setSent(true);
        } catch (err) {
            const errorMessage = err.message || 'Failed to send reset link';
            setError(errorMessage);

            // Categorize error type
            if (errorMessage.includes('connect') || errorMessage.includes('network')) {
                setErrorType('network');
            } else {
                setErrorType('server');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleRetry = () => {
        setError('');
        setErrorType('');
    };

    if (sent) {
        return (
            <div className="min-h-screen bg-gradient-theme flex items-center justify-center p-4">
                <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full text-center">
                    <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <CheckCircle className="w-8 h-8 text-green-600" />
                    </div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-4">Check Your Email</h2>
                    <p className="text-gray-600 mb-6">
                        If an account exists with <strong>{email}</strong>, we've sent a password reset link.
                    </p>
                    <p className="text-sm text-gray-500 mb-6">
                        Didn't receive an email? Check your spam folder or try again.
                    </p>
                    <Link
                        to="/"
                        className="inline-flex items-center gap-2 text-accent hover:text-accent-dark font-medium"
                    >
                        <ArrowLeft size={18} />
                        Back to Login
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-theme flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full">
                <div className="text-center mb-8">
                    <div className="w-16 h-16 bg-accent-lighter rounded-full flex items-center justify-center mx-auto mb-4">
                        <Mail className="w-8 h-8 text-accent" />
                    </div>
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">Forgot Password?</h1>
                    <p className="text-gray-600">
                        Enter your email and we'll send you a reset link
                    </p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                    {error && (
                        <div className={`border px-4 py-3 rounded-xl flex items-start gap-2 ${errorType === 'network' ? 'bg-orange-50 border-orange-200 text-orange-700' :
                                'bg-red-50 border-red-200 text-red-700'
                            }`}>
                            <AlertCircle size={20} className="flex-shrink-0 mt-0.5" />
                            <div className="flex-1">
                                <span className="block">{error}</span>
                                {errorType === 'network' && (
                                    <button
                                        type="button"
                                        onClick={handleRetry}
                                        className="mt-2 text-sm font-medium underline hover:no-underline"
                                    >
                                        Try again
                                    </button>
                                )}
                            </div>
                        </div>
                    )}

                    <div>
                        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                            Email Address
                        </label>
                        <input
                            id="email"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent"
                            placeholder="you@example.com"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-button-gradient text-white font-medium py-3 px-6 rounded-xl hover:shadow-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {loading ? 'Sending...' : 'Send Reset Link'}
                    </button>
                </form>

                <div className="mt-6 text-center">
                    <Link
                        to="/"
                        className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 font-medium"
                    >
                        <ArrowLeft size={18} />
                        Back to Login
                    </Link>
                </div>
            </div>
        </div>
    );
}

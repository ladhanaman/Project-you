// src/components/ResetPassword.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Lock, CheckCircle, AlertCircle, Check, X, Eye, EyeOff, RefreshCw } from 'lucide-react';
import { resetPassword } from '../services/apiService.js';

// Password strength checker
const checkPasswordStrength = (password) => {
    if (!password) return { score: 0, label: '', color: 'gray' };

    let score = 0;
    const checks = {
        length: password.length >= 8,
        uppercase: /[A-Z]/.test(password),
        lowercase: /[a-z]/.test(password),
        number: /[0-9]/.test(password),
        special: /[^A-Za-z0-9]/.test(password)
    };

    score = Object.values(checks).filter(Boolean).length;

    const strengths = {
        0: { score: 0, label: '', color: 'gray' },
        1: { score: 1, label: 'Very Weak', color: 'red' },
        2: { score: 2, label: 'Weak', color: 'orange' },
        3: { score: 3, label: 'Fair', color: 'yellow' },
        4: { score: 4, label: 'Good', color: 'blue' },
        5: { score: 5, label: 'Strong', color: 'green' }
    };

    return { ...strengths[score], checks };
};

export default function ResetPassword() {
    const { token } = useParams();
    const navigate = useNavigate();
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [loading, setLoading] = useState(false);
    const [validatingToken, setValidatingToken] = useState(true);
    const [tokenValid, setTokenValid] = useState(false);
    const [error, setError] = useState('');
    const [errorType, setErrorType] = useState(''); // 'token', 'validation', 'network', 'server'
    const [success, setSuccess] = useState(false);
    const [passwordStrength, setPasswordStrength] = useState({ score: 0, label: '', color: 'gray', checks: {} });

    // Validate token on component mount
    useEffect(() => {
        const validateToken = async () => {
            if (!token || token.length < 10) {
                setTokenValid(false);
                setError('Invalid reset link');
                setErrorType('token');
                setValidatingToken(false);
                return;
            }

            // Token looks valid (basic format check)
            // Backend will do the real validation when form is submitted
            setTokenValid(true);
            setValidatingToken(false);
        };

        validateToken();
    }, [token]);

    // Update password strength as user types
    useEffect(() => {
        setPasswordStrength(checkPasswordStrength(password));
    }, [password]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setErrorType('');

        // Validate passwords match
        if (password !== confirmPassword) {
            setError('Passwords do not match');
            setErrorType('validation');
            return;
        }

        // Validate password strength requirements
        const strength = checkPasswordStrength(password);
        if (password.length < 8) {
            setError('Password must be at least 8 characters long');
            setErrorType('validation');
            return;
        }

        // Recommend stronger password if too weak
        if (strength.score < 3) {
            setError('Password is too weak. Please include uppercase, lowercase, numbers, and special characters.');
            setErrorType('validation');
            return;
        }

        setLoading(true);

        try {
            await resetPassword(token, password);
            setSuccess(true);
            setTimeout(() => {
                navigate('/');
            }, 3000);
        } catch (err) {
            const errorMessage = err.message || 'Failed to reset password';
            setError(errorMessage);

            // Categorize error type
            if (errorMessage.includes('token') || errorMessage.includes('expired') || errorMessage.includes('Invalid')) {
                setErrorType('token');
            } else if (errorMessage.includes('connect') || errorMessage.includes('network')) {
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
        setPassword('');
        setConfirmPassword('');
    };

    if (success) {
        return (
            <div className="min-h-screen bg-gradient-theme flex items-center justify-center p-4">
                <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full text-center">
                    <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <CheckCircle className="w-8 h-8 text-green-600" />
                    </div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-4">Password Reset Successful!</h2>
                    <p className="text-gray-600 mb-6">
                        Your password has been reset. Redirecting to login...
                    </p>
                    <Link
                        to="/"
                        className="inline-block bg-button-gradient text-white font-medium py-3 px-6 rounded-xl hover:shadow-lg transition"
                    >
                        Go to Login
                    </Link>
                </div>
            </div>
        );
    }

    // Loading state while validating token
    if (validatingToken) {
        return (
            <div className="min-h-screen bg-gradient-theme flex items-center justify-center p-4">
                <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full text-center">
                    <div className="w-16 h-16 bg-accent-lighter rounded-full flex items-center justify-center mx-auto mb-4 animate-pulse">
                        <Lock className="w-8 h-8 text-accent" />
                    </div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-4">Verifying Link...</h2>
                    <p className="text-gray-600">Please wait while we validate your reset link</p>
                </div>
            </div>
        );
    }

    // Invalid token error state
    if (!tokenValid && errorType === 'token') {
        return (
            <div className="min-h-screen bg-gradient-theme flex items-center justify-center p-4">
                <div className="bg-white rounded-2xl shadow-xl border border-red-200 p-8 max-w-md w-full">
                    <div className="text-center mb-6">
                        <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                            <AlertCircle className="w-8 h-8 text-red-600" />
                        </div>
                        <h2 className="text-2xl font-bold text-gray-900 mb-2">Invalid Reset Link</h2>
                        <p className="text-gray-600 mb-6">
                            {error || 'This password reset link is invalid or has expired.'}
                        </p>
                    </div>

                    <div className="space-y-3">
                        <Link
                            to="/forgot-password"
                            className="w-full inline-flex items-center justify-center gap-2 bg-button-gradient text-white font-medium py-3 px-6 rounded-xl hover:shadow-lg transition"
                        >
                            <RefreshCw size={18} />
                            Request New Reset Link
                        </Link>
                        <Link
                            to="/"
                            className="w-full inline-flex items-center justify-center gap-2 bg-white hover:bg-gray-50 text-gray-700 font-medium py-3 px-6 rounded-xl transition border border-gray-200"
                        >
                            Back to Login
                        </Link>
                    </div>

                    <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-xl">
                        <p className="text-sm text-blue-800">
                            <strong>Note:</strong> Reset links expire after 1 hour for security. Please request a new link if yours has expired.
                        </p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-theme flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full">
                <div className="text-center mb-8">
                    <div className="w-16 h-16 bg-accent-lighter rounded-full flex items-center justify-center mx-auto mb-4">
                        <Lock className="w-8 h-8 text-accent" />
                    </div>
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">Reset Password</h1>
                    <p className="text-gray-600">
                        Enter your new password below
                    </p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Error Display with Type-Specific Styling */}
                    {error && (
                        <div className={`border px-4 py-3 rounded-xl flex items-start gap-2 ${errorType === 'token' ? 'bg-red-50 border-red-200 text-red-700' :
                                errorType === 'network' ? 'bg-orange-50 border-orange-200 text-orange-700' :
                                    errorType === 'validation' ? 'bg-yellow-50 border-yellow-200 text-yellow-800' :
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
                                {errorType === 'token' && (
                                    <Link
                                        to="/forgot-password"
                                        className="mt-2 inline-block text-sm font-medium underline hover:no-underline"
                                    >
                                        Request new reset link
                                    </Link>
                                )}
                            </div>
                        </div>
                    )}

                    {/* New Password Field with Show/Hide Toggle */}
                    <div>
                        <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                            New Password
                        </label>
                        <div className="relative">
                            <input
                                id="password"
                                type={showPassword ? 'text' : 'password'}
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                minLength={8}
                                className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent"
                                placeholder="Min. 8 characters"
                            />
                            <button
                                type="button"
                                onClick={() => setShowPassword(!showPassword)}
                                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 focus:outline-none"
                                aria-label={showPassword ? 'Hide password' : 'Show password'}
                            >
                                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                            </button>
                        </div>

                        {/* Password Strength Indicator */}
                        {password && (
                            <div className="mt-3">
                                <div className="flex items-center gap-2 mb-2">
                                    <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                                        <div
                                            className={`h-full transition-all duration-300 ${passwordStrength.color === 'red' ? 'bg-red-500' :
                                                    passwordStrength.color === 'orange' ? 'bg-orange-500' :
                                                        passwordStrength.color === 'yellow' ? 'bg-yellow-500' :
                                                            passwordStrength.color === 'blue' ? 'bg-blue-500' :
                                                                passwordStrength.color === 'green' ? 'bg-green-500' :
                                                                    'bg-gray-300'
                                                }`}
                                            style={{ width: `${(passwordStrength.score / 5) * 100}%` }}
                                        />
                                    </div>
                                    <span className={`text-sm font-medium ${passwordStrength.color === 'red' ? 'text-red-600' :
                                            passwordStrength.color === 'orange' ? 'text-orange-600' :
                                                passwordStrength.color === 'yellow' ? 'text-yellow-600' :
                                                    passwordStrength.color === 'blue' ? 'text-blue-600' :
                                                        passwordStrength.color === 'green' ? 'text-green-600' :
                                                            'text-gray-500'
                                        }`}>
                                        {passwordStrength.label}
                                    </span>
                                </div>

                                {/* Password Requirements Checklist */}
                                <div className="grid grid-cols-2 gap-2 text-xs">
                                    <div className={`flex items-center gap-1 ${passwordStrength.checks.length ? 'text-green-600' : 'text-gray-400'}`}>
                                        {passwordStrength.checks.length ? <Check size={14} /> : <X size={14} />}
                                        <span>8+ characters</span>
                                    </div>
                                    <div className={`flex items-center gap-1 ${passwordStrength.checks.uppercase ? 'text-green-600' : 'text-gray-400'}`}>
                                        {passwordStrength.checks.uppercase ? <Check size={14} /> : <X size={14} />}
                                        <span>Uppercase (A-Z)</span>
                                    </div>
                                    <div className={`flex items-center gap-1 ${passwordStrength.checks.lowercase ? 'text-green-600' : 'text-gray-400'}`}>
                                        {passwordStrength.checks.lowercase ? <Check size={14} /> : <X size={14} />}
                                        <span>Lowercase (a-z)</span>
                                    </div>
                                    <div className={`flex items-center gap-1 ${passwordStrength.checks.number ? 'text-green-600' : 'text-gray-400'}`}>
                                        {passwordStrength.checks.number ? <Check size={14} /> : <X size={14} />}
                                        <span>Number (0-9)</span>
                                    </div>
                                    <div className={`flex items-center gap-1 ${passwordStrength.checks.special ? 'text-green-600' : 'text-gray-400'}`}>
                                        {passwordStrength.checks.special ? <Check size={14} /> : <X size={14} />}
                                        <span>Special (!@#$)</span>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Confirm Password Field with Show/Hide Toggle */}
                    <div>
                        <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-2">
                            Confirm New Password
                        </label>
                        <div className="relative">
                            <input
                                id="confirmPassword"
                                type={showConfirmPassword ? 'text' : 'password'}
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                required
                                minLength={8}
                                className={`w-full px-4 py-3 pr-12 border rounded-xl focus:outline-none focus:ring-2 focus:border-transparent ${confirmPassword && (password === confirmPassword ?
                                        'border-green-300 focus:ring-green-500' :
                                        password.length > 0 && confirmPassword.length >= password.length ?
                                            'border-red-300 focus:ring-red-500' :
                                            'border-gray-300 focus:ring-accent'
                                    )
                                    }`}
                                placeholder="Re-enter password"
                            />
                            <button
                                type="button"
                                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 focus:outline-none"
                                aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
                            >
                                {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                            </button>
                        </div>
                        {/* Password Match Indicator */}
                        {confirmPassword && password && (
                            <p className={`mt-2 text-sm flex items-center gap-1 ${password === confirmPassword ? 'text-green-600' : 'text-red-600'
                                }`}>
                                {password === confirmPassword ? (
                                    <><Check size={16} /> Passwords match</>
                                ) : (
                                    <><X size={16} /> Passwords do not match</>
                                )}
                            </p>
                        )}
                    </div>

                    <button
                        type="submit"
                        disabled={loading || !password || !confirmPassword || password !== confirmPassword || passwordStrength.score < 3}
                        className="w-full bg-button-gradient text-white font-medium py-3 px-6 rounded-xl hover:shadow-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {loading ? (
                            <span className="flex items-center justify-center gap-2">
                                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                                Resetting...
                            </span>
                        ) : 'Reset Password'}
                    </button>
                </form>

                <div className="mt-6 text-center">
                    <Link
                        to="/"
                        className="text-gray-600 hover:text-gray-900 font-medium"
                    >
                        Back to Login
                    </Link>
                </div>
            </div>
        </div>
    );
}

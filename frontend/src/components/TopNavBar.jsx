import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Menu, X, Home, Map, FileText, User, LogOut } from 'lucide-react';
import { useStore } from '../store/useStore.js';
import { getDashboardSummary } from '../services/apiService.js';

export default function TopNavBar() {
    const location = useLocation();
    const navigate = useNavigate();
    const { user, logout } = useStore();
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const [userMenuOpen, setUserMenuOpen] = useState(false);
    const [submissionId, setSubmissionId] = useState(null);

    // Fetch submission ID for Report link
    useEffect(() => {
        const fetchSubmissionId = async () => {
            try {
                const data = await getDashboardSummary();
                if (data?.pri_scores?.latest_submission_id) {
                    setSubmissionId(data.pri_scores.latest_submission_id);
                }
            } catch (err) {
                console.log('Could not fetch submission ID for nav');
            }
        };
        fetchSubmissionId();
    }, []);

    const isActive = (path) => location.pathname === path || location.pathname.startsWith(path);

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    // Navigation links
    const navLinks = [
        { name: 'Home', path: '/home', icon: Home },
        { name: 'Journey', path: '/journey', icon: Map },
        {
            name: 'Report',
            // If no submission, just go home. Simple.
            path: submissionId ? `/results/${submissionId}` : '/home',
            icon: FileText
        },
        { name: 'Profile', path: '/profile', icon: User }
    ];

    return (
        <>
            {/* Top Navigation Bar - Floating Glass Design */}
            <div className="fixed top-4 left-0 right-0 z-50 px-4 sm:px-6 pointer-events-none">
                <nav className="max-w-5xl mx-auto bg-white/80 backdrop-blur-xl border border-white/40 shadow-xl rounded-2xl pointer-events-auto transition-all duration-300">
                    <div className="px-4 sm:px-6">
                        <div className="flex justify-between items-center h-20">
                            {/* Left: Logo */}
                            <div className="flex items-center">
                                <Link to="/home" className="flex items-center gap-2">
                                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center text-white font-bold text-sm">
                                        Y
                                    </div>
                                    <span className="text-xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                                        Project You
                                    </span>
                                </Link>
                            </div>

                            {/* Center: Desktop Navigation Links */}
                            <div className="hidden md:flex items-center gap-1 absolute left-1/2 transform -translate-x-1/2">
                                {navLinks.map((link) => {
                                    const Icon = link.icon;
                                    // Only mark active if we are actually on that path
                                    // Special case for Report: Don't mark active if we are on Home, even if path is /home
                                    const active = (isActive(link.path) || (link.name === 'Report' && location.pathname.startsWith('/report/generating'))) && (link.name !== 'Report' || submissionId);

                                    return (
                                        <Link
                                            key={link.name}
                                            to={link.path}
                                            className={`
                                            flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all
                                            ${active
                                                    ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-md'
                                                    : 'text-gray-700 hover:bg-gray-100'
                                                }
                                        `}
                                        >
                                            <Icon size={18} />
                                            {link.name}
                                        </Link>
                                    );
                                })}
                            </div>

                            {/* Right: User Menu */}
                            <div className="flex items-center gap-3">
                                {/* User Avatar & Dropdown (Desktop) */}
                                {user && (
                                    <div className="hidden md:block relative">
                                        <button
                                            onClick={() => setUserMenuOpen(!userMenuOpen)}
                                            className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-100 transition"
                                        >
                                            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white font-semibold text-sm">
                                                {user.first_name?.[0] || user.email?.[0]?.toUpperCase() || 'U'}
                                            </div>
                                            <span className="text-sm font-medium text-gray-700">
                                                {user.first_name || 'User'}
                                            </span>
                                        </button>

                                        {/* User Dropdown Menu */}
                                        {userMenuOpen && (
                                            <>
                                                {/* Backdrop */}
                                                <div
                                                    className="fixed inset-0 z-10"
                                                    onClick={() => setUserMenuOpen(false)}
                                                />

                                                {/* Dropdown */}
                                                <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-lg border border-gray-200 py-2 z-20">
                                                    <div className="px-4 py-3 border-b border-gray-100">
                                                        <p className="text-sm font-semibold text-gray-900">
                                                            {user.first_name || user.full_name || 'User'}
                                                        </p>
                                                        <p className="text-xs text-gray-500 truncate">{user.email}</p>
                                                    </div>

                                                    <Link
                                                        to="/profile"
                                                        onClick={() => setUserMenuOpen(false)}
                                                        className="flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                                                    >
                                                        <User size={16} />
                                                        Profile Settings
                                                    </Link>

                                                    <button
                                                        onClick={handleLogout}
                                                        className="w-full flex items-center gap-3 px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                                                    >
                                                        <LogOut size={16} />
                                                        Logout
                                                    </button>
                                                </div>
                                            </>
                                        )}
                                    </div>
                                )}

                                {/* Mobile Hamburger */}
                                <button
                                    onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                                    className="md:hidden p-2 rounded-lg hover:bg-gray-100 transition"
                                >
                                    {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
                                </button>
                            </div>
                        </div>
                    </div>
                </nav>
            </div>

            {/* Mobile Menu Drawer */}
            {mobileMenuOpen && (
                <>
                    {/* Backdrop */}
                    <div
                        className="md:hidden fixed inset-0 bg-black/40 backdrop-blur-sm z-40"
                        onClick={() => setMobileMenuOpen(false)}
                    />

                    {/* Drawer */}
                    <div className="md:hidden fixed top-28 left-4 right-4 bg-white/95 backdrop-blur-xl border border-gray-100 shadow-2xl rounded-2xl z-50 max-h-[calc(100vh-8rem)] overflow-y-auto ring-1 ring-black/5">
                        {/* User Info */}
                        {user && (
                            <div className="p-4 border-b border-gray-100 flex items-center gap-3">
                                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white font-semibold">
                                    {user.first_name?.[0] || user.email?.[0]?.toUpperCase() || 'U'}
                                </div>
                                <div>
                                    <p className="text-sm font-semibold text-gray-900">
                                        {user.first_name || user.full_name || 'User'}
                                    </p>
                                    <p className="text-xs text-gray-500">{user.email}</p>
                                </div>
                            </div>
                        )}

                        {/* Navigation Links */}
                        <div className="p-2">
                            {navLinks.map((link) => {
                                const Icon = link.icon;
                                const active = isActive(link.path);

                                return (
                                    <Link
                                        key={link.path}
                                        to={link.path}
                                        onClick={() => setMobileMenuOpen(false)}
                                        className={`
                                            flex items-center gap-3 px-4 py-3 rounded-lg font-medium text-sm transition-all mb-1
                                            ${active
                                                ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white'
                                                : 'text-gray-700 hover:bg-gray-100'
                                            }
                                        `}
                                    >
                                        <Icon size={20} />
                                        {link.name}
                                    </Link>
                                );
                            })}
                        </div>

                        {/* Logout */}
                        <div className="p-2 border-t border-gray-100">
                            <button
                                onClick={handleLogout}
                                className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm text-red-600 hover:bg-red-50 font-medium"
                            >
                                <LogOut size={20} />
                                Logout
                            </button>
                        </div>
                    </div>
                </>
            )}
        </>
    );
}

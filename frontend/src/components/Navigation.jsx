// src/components/Navigation.jsx
import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Home, FileText, Map, User, LogOut, ChevronDown, ChevronRight, Menu, X } from 'lucide-react';
import { useStore } from '../store/useStore.js';
import ThemeSwitcher from './ThemeSwitcher.jsx';

// Desktop sidebar navigation component
export function DesktopNav({ user, journeyData, onLogout }) {
    const location = useLocation();
    const [journeyExpanded, setJourneyExpanded] = useState(false);

    const isActive = (path) => location.pathname === path;
    const isJourneyActive = location.pathname.startsWith('/journey/day');

    return (
        <aside className="hidden lg:flex lg:flex-col w-72 bg-white border-r border-gray-200 min-h-screen">
            {/* Logo & User Section */}
            <div className="p-6 border-b border-gray-200">
                <h1 className="text-2xl font-bold bg-button-gradient bg-clip-text text-transparent mb-4">
                    Project You
                </h1>
                {user && (
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white font-semibold">
                            {user.email?.[0]?.toUpperCase() || 'U'}
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="text-sm font-semibold text-gray-900 truncate">
                                {user.first_name || user.full_name || 'User'}
                            </p>
                            <p className="text-xs text-gray-500 truncate">{user.email}</p>
                        </div>
                    </div>
                )}
            </div>

            {/* Navigation Links */}
            <nav className="flex-1 overflow-y-auto p-4">
                <div className="space-y-1">
                    <NavItem
                        to="/dashboard"
                        icon={Home}
                        label="Dashboard"
                        active={isActive('/dashboard')}
                    />

                    {journeyData?.submissionId && (
                        <NavItem
                            to={`/results/${journeyData.submissionId}`}
                            icon={FileText}
                            label="My Report"
                            active={isActive(`/results/${journeyData.submissionId}`)}
                            badge={journeyData.hasUnread ? 'NEW' : null}
                        />
                    )}

                    {/* 7-Day Journey Expandable Menu */}
                    {journeyData?.hasJourney && (
                        <div>
                            <button
                                onClick={() => setJourneyExpanded(!journeyExpanded)}
                                className={`w-full flex items-center justify-between px-4 py-3 rounded-xl transition-all ${isJourneyActive
                                        ? 'bg-button-gradient text-white shadow-md'
                                        : 'text-gray-700 hover:bg-gray-100'
                                    }`}
                            >
                                <div className="flex items-center gap-3">
                                    <Map size={20} />
                                    <span className="font-medium">7-Day Journey</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    {journeyData.completedDays > 0 && (
                                        <span className={`text-xs px-2 py-0.5 rounded-full ${isJourneyActive
                                                ? 'bg-white/20 text-white'
                                                : 'bg-green-100 text-green-700'
                                            }`}>
                                            {journeyData.completedDays}/7
                                        </span>
                                    )}
                                    {journeyExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                                </div>
                            </button>

                            {journeyExpanded && (
                                <div className="ml-4 mt-1 space-y-1 border-l-2 border-gray-200 pl-4">
                                    {[1, 2, 3, 4, 5, 6, 7].map((day) => {
                                        const dayData = journeyData.days?.[day];
                                        const isCompleted = dayData?.completed;
                                        const isCurrent = day === journeyData.currentDay;
                                        const isUnlocked = day <= (journeyData.currentDay || 1);

                                        return (
                                            <Link
                                                key={day}
                                                to={isUnlocked ? `/journey/day/${day}` : '#'}
                                                className={`flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-all ${isActive(`/journey/day/${day}`)
                                                        ? 'bg-indigo-50 text-indigo-700 font-medium'
                                                        : isUnlocked
                                                            ? 'text-gray-600 hover:bg-gray-50'
                                                            : 'text-gray-400 cursor-not-allowed'
                                                    }`}
                                                onClick={(e) => !isUnlocked && e.preventDefault()}
                                            >
                                                <span>Day {day}</span>
                                                <span className="flex items-center gap-1">
                                                    {isCompleted && <span className="text-green-500">✓</span>}
                                                    {isCurrent && !isCompleted && (
                                                        <span className="w-2 h-2 bg-indigo-500 rounded-full animate-pulse" />
                                                    )}
                                                    {!isUnlocked && <span className="text-xs">🔒</span>}
                                                </span>
                                            </Link>
                                        );
                                    })}
                                </div>
                            )}
                        </div>
                    )}

                    <NavItem
                        to="/profile"
                        icon={User}
                        label="Profile"
                        active={isActive('/profile')}
                    />
                </div>
            </nav>

            {/* Bottom Actions */}
            <div className="p-4 border-t border-gray-200 space-y-3">
                <ThemeSwitcher />
                <button
                    onClick={onLogout}
                    className="w-full flex items-center gap-3 px-4 py-3 text-red-600 hover:bg-red-50 rounded-xl transition"
                >
                    <LogOut size={20} />
                    <span className="font-medium">Logout</span>
                </button>
            </div>
        </aside>
    );
}

// Mobile navigation component
export function MobileNav({ user, journeyData, onLogout }) {
    const [isOpen, setIsOpen] = useState(false);
    const location = useLocation();
    const [journeyExpanded, setJourneyExpanded] = useState(false);

    const isActive = (path) => location.pathname === path;
    const isJourneyActive = location.pathname.startsWith('/journey/day');

    // Close drawer when route changes
    useEffect(() => {
        setIsOpen(false);
    }, [location.pathname]);

    // Lock body scroll when drawer is open
    useEffect(() => {
        if (isOpen) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }
        return () => {
            document.body.style.overflow = '';
        };
    }, [isOpen]);

    return (
        <>
            {/* Mobile Header */}
            <header className="lg:hidden fixed top-0 left-0 right-0 h-16 bg-white/95 backdrop-blur-md border-b border-gray-200 shadow-sm z-50 flex items-center justify-between px-4">
                <button
                    onClick={() => setIsOpen(true)}
                    className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                    aria-label="Open navigation menu"
                >
                    <Menu className="w-6 h-6 text-gray-700" />
                </button>

                <h1 className="text-xl font-bold text-gray-900">Project You</h1>

                {user && (
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white font-semibold text-sm">
                        {user.email?.[0]?.toUpperCase() || 'U'}
                    </div>
                )}
            </header>

            {/* Backdrop Overlay */}
            <div
                className={`lg:hidden fixed inset-0 bg-black/40 backdrop-blur-sm z-40 transition-opacity duration-300 ${isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
                    }`}
                onClick={() => setIsOpen(false)}
            />

            {/* Drawer Menu */}
            <nav
                className={`lg:hidden fixed top-0 left-0 bottom-0 w-[80%] max-w-[320px] bg-white shadow-2xl z-50 overflow-y-auto transform transition-transform duration-300 ease-out ${isOpen ? 'translate-x-0' : '-translate-x-full'
                    }`}
                aria-label="Main navigation"
                role="navigation"
            >
                {/* Drawer Header */}
                <div className="h-16 flex items-center justify-between px-4 border-b border-gray-200">
                    <h2 className="text-lg font-semibold text-gray-900">Navigation</h2>
                    <button
                        onClick={() => setIsOpen(false)}
                        className="p-2 rounded-lg hover:bg-gray-100"
                        aria-label="Close menu"
                    >
                        <X className="w-6 h-6 text-gray-700" />
                    </button>
                </div>

                {/* User Info */}
                {user && (
                    <div className="p-4 border-b border-gray-200 flex items-center gap-3">
                        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white font-semibold">
                            {user.email?.[0]?.toUpperCase() || 'U'}
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="text-sm font-semibold text-gray-900 truncate">
                                {user.first_name || user.full_name || 'User'}
                            </p>
                            <p className="text-xs text-gray-500 truncate">{user.email}</p>
                        </div>
                    </div>
                )}

                {/* Navigation Items */}
                <div className="py-4 px-2">
                    <div className="space-y-1">
                        <NavItem
                            to="/dashboard"
                            icon={Home}
                            label="Dashboard"
                            active={isActive('/dashboard')}
                            mobile
                        />

                        {journeyData?.submissionId && (
                            <NavItem
                                to={`/results/${journeyData.submissionId}`}
                                icon={FileText}
                                label="My Report"
                                active={isActive(`/results/${journeyData.submissionId}`)}
                                badge={journeyData.hasUnread ? 'NEW' : null}
                                mobile
                            />
                        )}

                        {/* 7-Day Journey Expandable */}
                        {journeyData?.hasJourney && (
                            <div>
                                <button
                                    onClick={() => setJourneyExpanded(!journeyExpanded)}
                                    className={`w-full flex items-center justify-between px-4 py-3 rounded-xl transition-all ${isJourneyActive
                                            ? 'bg-button-gradient text-white'
                                            : 'text-gray-700 hover:bg-gray-100 active:scale-[0.98]'
                                        }`}
                                >
                                    <div className="flex items-center gap-3">
                                        <Map size={20} />
                                        <span className="font-medium">7-Day Journey</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        {journeyData.completedDays > 0 && (
                                            <span className={`text-xs px-2 py-0.5 rounded-full ${isJourneyActive
                                                    ? 'bg-white/20 text-white'
                                                    : 'bg-green-100 text-green-700'
                                                }`}>
                                                {journeyData.completedDays}/7
                                            </span>
                                        )}
                                        {journeyExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                                    </div>
                                </button>

                                {journeyExpanded && (
                                    <div className="ml-4 mt-1 space-y-1 border-l-2 border-gray-200 pl-4">
                                        {[1, 2, 3, 4, 5, 6, 7].map((day) => {
                                            const dayData = journeyData.days?.[day];
                                            const isCompleted = dayData?.completed;
                                            const isCurrent = day === journeyData.currentDay;
                                            const isUnlocked = day <= (journeyData.currentDay || 1);

                                            return (
                                                <Link
                                                    key={day}
                                                    to={isUnlocked ? `/journey/day/${day}` : '#'}
                                                    className={`flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-all active:scale-[0.98] ${isActive(`/journey/day/${day}`)
                                                            ? 'bg-indigo-50 text-indigo-700 font-medium'
                                                            : isUnlocked
                                                                ? 'text-gray-600 hover:bg-gray-50'
                                                                : 'text-gray-400 cursor-not-allowed'
                                                        }`}
                                                    onClick={(e) => !isUnlocked && e.preventDefault()}
                                                >
                                                    <span>Day {day}</span>
                                                    <span className="flex items-center gap-1">
                                                        {isCompleted && <span className="text-green-500">✓</span>}
                                                        {isCurrent && !isCompleted && (
                                                            <span className="w-2 h-2 bg-indigo-500 rounded-full animate-pulse" />
                                                        )}
                                                        {!isUnlocked && <span className="text-xs">🔒</span>}
                                                    </span>
                                                </Link>
                                            );
                                        })}
                                    </div>
                                )}
                            </div>
                        )}

                        <NavItem
                            to="/profile"
                            icon={User}
                            label="Profile"
                            active={isActive('/profile')}
                            mobile
                        />
                    </div>
                </div>

                {/* Bottom Actions */}
                <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 bg-gray-50 space-y-3">
                    <ThemeSwitcher />
                    <button
                        onClick={onLogout}
                        className="w-full flex items-center gap-3 px-4 py-3 text-red-600 hover:bg-red-50 rounded-xl transition active:scale-[0.98]"
                    >
                        <LogOut size={20} />
                        <span className="font-medium">Logout</span>
                    </button>
                </div>
            </nav>
        </>
    );
}

// Reusable Navigation Item Component
function NavItem({ to, icon: Icon, label, active, badge, mobile }) {
    return (
        <Link
            to={to}
            className={`flex items-center justify-between px-4 py-3 rounded-xl transition-all ${mobile ? 'active:scale-[0.98]' : ''
                } ${active
                    ? 'bg-button-gradient text-white shadow-md'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
        >
            <div className="flex items-center gap-3">
                <Icon size={20} />
                <span className="font-medium">{label}</span>
            </div>
            {badge && (
                <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${active
                        ? 'bg-white/20 text-white'
                        : 'bg-red-500 text-white'
                    }`}>
                    {badge}
                </span>
            )}
        </Link>
    );
}

// Main Navigation Wrapper that handles both desktop and mobile
export default function Navigation() {
    const { user, logout } = useStore();
    const navigate = useNavigate();
    const [journeyData, setJourneyData] = useState({
        hasJourney: false,
        submissionId: null,
        currentDay: 1,
        completedDays: 0,
        days: {},
        hasUnread: false
    });

    // Fetch journey data from API or store
    useEffect(() => {
        // TODO: Fetch this from backend API
        // For now, check localStorage for submission data
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
            try {
                const userData = JSON.parse(storedUser);
                // This would come from API in real implementation
                setJourneyData({
                    hasJourney: false, // Set to true when user has completed PRI assessment
                    submissionId: null,
                    currentDay: 1,
                    completedDays: 0,
                    days: {},
                    hasUnread: false
                });
            } catch (e) {
                console.error('Error parsing user data:', e);
            }
        }
    }, [user]);

    const handleLogout = async () => {
        await logout();
        navigate('/');
    };

    return (
        <>
            <DesktopNav user={user} journeyData={journeyData} onLogout={handleLogout} />
            <MobileNav user={user} journeyData={journeyData} onLogout={handleLogout} />
        </>
    );
}

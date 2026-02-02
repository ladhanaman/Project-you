// src/components/AppLayout.jsx
import React from 'react';
import TopNavBar from './TopNavBar.jsx';

/**
 * Main app layout wrapper that includes top navigation
 * Used for authenticated routes
 */
export default function AppLayout({ children }) {
    return (
        <div className="min-h-screen bg-gray-50">
            {/* Top Navigation Bar */}
            <TopNavBar />

            {/* Main Content Area - Add top padding for fixed floating nav */}
            <main className="pt-32">
                {children}
            </main>
        </div>
    );
}

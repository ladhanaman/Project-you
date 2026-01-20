// src/components/MainLayout.jsx
import React from 'react';

export default function MainLayout({ children, showHeader = false, onLogout }) {
    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
            <div className="max-w-5xl mx-auto px-4 py-8">
                {children}
            </div>
        </div>
    );
}

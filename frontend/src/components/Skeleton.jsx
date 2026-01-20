// src/components/Skeleton.jsx
import React from 'react';

/**
 * Reusable Skeleton Loading Components
 * Modern shimmer effect skeletons that replace spinners for better UX
 */

// Base skeleton with shimmer animation
export function Skeleton({ className = '', ...props }) {
    return (
        <div
            className={`animate-pulse bg-gradient-to-r from-slate-200 via-slate-100 to-slate-200 bg-[length:200%_100%] rounded ${className}`}
            style={{ animation: 'shimmer 1.5s ease-in-out infinite' }}
            {...props}
        />
    );
}

// Text line skeleton
export function SkeletonText({ lines = 1, className = '' }) {
    return (
        <div className={`space-y-2 ${className}`}>
            {Array.from({ length: lines }).map((_, i) => (
                <Skeleton
                    key={i}
                    className={`h-4 ${i === lines - 1 && lines > 1 ? 'w-3/4' : 'w-full'}`}
                />
            ))}
        </div>
    );
}

// Card skeleton for dashboard test cards
export function SkeletonCard() {
    return (
        <div className="bg-white rounded-2xl shadow-lg border border-slate-200 p-8">
            <div className="flex items-start gap-4 mb-6">
                <Skeleton className="w-14 h-14 rounded-xl" />
                <div className="flex-1">
                    <Skeleton className="h-6 w-3/4 mb-2" />
                    <Skeleton className="h-4 w-1/2" />
                </div>
            </div>
            <SkeletonText lines={3} className="mb-6" />
            <Skeleton className="h-12 w-full rounded-lg" />
        </div>
    );
}

// Dashboard loading skeleton
export function DashboardSkeleton() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
            <div className="max-w-5xl mx-auto px-4 py-8">
                {/* Header skeleton */}
                <div className="flex items-center justify-between mb-8">
                    <div>
                        <Skeleton className="h-9 w-64 mb-2" />
                        <Skeleton className="h-5 w-48" />
                    </div>
                    <Skeleton className="h-10 w-24 rounded-lg" />
                </div>

                {/* Cards grid */}
                <div className="grid md:grid-cols-2 gap-6">
                    <SkeletonCard />
                    <SkeletonCard />
                </div>
            </div>
        </div>
    );
}

// Results page loading skeleton
export function ResultsSkeleton() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
            <div className="max-w-4xl mx-auto px-4 py-8">
                {/* Header */}
                <div className="text-center mb-8">
                    <Skeleton className="h-10 w-80 mx-auto mb-4" />
                    <Skeleton className="h-5 w-48 mx-auto" />
                </div>

                {/* Score cards */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                    {[1, 2, 3, 4].map((i) => (
                        <div key={i} className="bg-white rounded-xl p-4 shadow-md">
                            <Skeleton className="h-4 w-20 mb-2" />
                            <Skeleton className="h-8 w-16" />
                        </div>
                    ))}
                </div>

                {/* Content sections */}
                <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
                    <Skeleton className="h-6 w-48 mb-4" />
                    <SkeletonText lines={4} />
                </div>

                <div className="bg-white rounded-2xl shadow-lg p-6">
                    <Skeleton className="h-6 w-48 mb-4" />
                    <div className="grid md:grid-cols-2 gap-4">
                        <SkeletonText lines={3} />
                        <SkeletonText lines={3} />
                    </div>
                </div>
            </div>
        </div>
    );
}

// Assessment loading skeleton
export function AssessmentSkeleton() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl shadow-xl p-8 max-w-2xl w-full">
                {/* Progress bar */}
                <div className="mb-8">
                    <Skeleton className="h-2 w-full rounded-full mb-4" />
                    <div className="flex justify-between">
                        <Skeleton className="h-4 w-24" />
                        <Skeleton className="h-4 w-32" />
                    </div>
                </div>

                {/* Question */}
                <Skeleton className="h-6 w-full mb-6" />
                <SkeletonText lines={2} className="mb-8" />

                {/* Options */}
                <div className="space-y-3 mb-8">
                    {[1, 2, 3, 4].map((i) => (
                        <Skeleton key={i} className="h-14 w-full rounded-lg" />
                    ))}
                </div>

                {/* Navigation buttons */}
                <div className="flex justify-between">
                    <Skeleton className="h-12 w-28 rounded-lg" />
                    <Skeleton className="h-12 w-28 rounded-lg" />
                </div>
            </div>
        </div>
    );
}

export default Skeleton;

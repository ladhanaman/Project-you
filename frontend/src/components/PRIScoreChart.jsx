import React from 'react';

const PRIScoreChart = ({ scores }) => {
    const { purpose, relevance, identity } = scores;

    // PRI scores come from backend as 0-1 scale
    // Convert to percentage (0-100) for display
    const purposePercent = Math.round((purpose || 0) * 100);
    const relevancePercent = Math.round((relevance || 0) * 100);
    const identityPercent = Math.round((identity || 0) * 100);

    // Helper to determine color based on score (0-100%)
    // PRI thresholds: LOW < 40%, MEDIUM 40-70%, HIGH >= 70%
    const getColor = (score) => {
        if (score >= 70) return 'text-emerald-500'; // High
        if (score >= 40) return 'text-amber-500';   // Medium
        return 'text-rose-500';                     // Low
    };

    const getLabel = (score) => {
        if (score >= 70) return 'HIGH';
        if (score >= 40) return 'MEDIUM';
        return 'LOW';
    };

    // Helper to calculate circle stroke dasharray
    // Radius = 40, Circumference = 2 * pi * 40 ≈ 251.2
    const CIRCUMFERENCE = 251.2;
    const getStrokeDashoffset = (score) => {
        return CIRCUMFERENCE - (score / 100) * CIRCUMFERENCE;
    };

    const ScoreCircle = ({ label, score, description, letter }) => (
        <div className="flex flex-col items-center p-4">
            <div className="relative w-32 h-32 flex items-center justify-center">
                {/* Background Circle */}
                <svg className="w-full h-full transform -rotate-90">
                    <circle
                        cx="64"
                        cy="64"
                        r="40"
                        stroke="currentColor"
                        strokeWidth="8"
                        fill="transparent"
                        className="text-gray-200"
                    />
                    {/* Progress Circle */}
                    <circle
                        cx="64"
                        cy="64"
                        r="40"
                        stroke="currentColor"
                        strokeWidth="8"
                        fill="transparent"
                        strokeDasharray={CIRCUMFERENCE}
                        strokeDashoffset={getStrokeDashoffset(score)}
                        className={`${getColor(score)} transition-all duration-1000 ease-out`}
                        strokeLinecap="round"
                    />
                </svg>
                {/* Letter Display (P, R, or I) */}
                <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-5xl font-bold text-gray-400">
                        {letter}
                    </div>
                </div>
            </div>
            <div className="text-center mt-3">
                <div className="text-sm font-semibold text-slate-900">{label}</div>
                <div className="text-xs text-slate-500 mt-1 max-w-[140px]">{description}</div>
            </div>
        </div>
    );

    return (
        <div className="bg-white rounded-2xl border border-slate-200 p-8 mb-6">
            <h3 className="text-xl font-bold text-slate-900 mb-6 text-center">Your PRI Profile</h3>
            <div className="flex justify-around items-start">
                <ScoreCircle
                    label="Purpose"
                    score={purposePercent}
                    description="Meaning, direction, and the 'why' behind your actions"
                    letter="P"
                />
                <ScoreCircle
                    label="Relevance"
                    score={relevancePercent}
                    description="Visibility, utility, and external validation"
                    letter="R"
                />
                <ScoreCircle
                    label="Identity"
                    score={identityPercent}
                    description="Authenticity, self-alignment, and role fit"
                    letter="I"
                />
            </div>
        </div>
    );
};

export default PRIScoreChart;

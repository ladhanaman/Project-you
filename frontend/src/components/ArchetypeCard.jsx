import React from 'react';
import { Award, Star, Compass } from 'lucide-react';

const ArchetypeCard = ({ archetype, displayArchetype }) => {
    return (
        <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl shadow-lg text-white p-8 relative overflow-hidden">
            {/* Decorative background elements */}
            <div className="absolute top-0 right-0 -mt-10 -mr-10 w-40 h-40 bg-white opacity-10 rounded-full blur-2xl"></div>
            <div className="absolute bottom-0 left-0 -mb-10 -ml-10 w-40 h-40 bg-purple-400 opacity-10 rounded-full blur-2xl"></div>

            <div className="relative z-10 flex flex-col md:flex-row items-center md:items-start gap-6 text-center md:text-left">
                {/* Icon Badge */}
                <div className="flex-shrink-0">
                    <div className="w-20 h-20 bg-white/20 rounded-2xl flex items-center justify-center backdrop-blur-sm border border-white/30">
                        <Compass className="w-10 h-10 text-white" />
                    </div>
                </div>

                {/* Content */}
                <div className="flex-1">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 border border-white/20 text-xs font-medium uppercase tracking-wider mb-3">
                        <Star className="w-3 h-3 text-slate-300 fill-slate-400" />
                        Your Core Archetype
                    </div>

                    <h2 className="text-3xl font-bold mb-2">
                        {displayArchetype || "Discovering..."}
                    </h2>

                    <p className="text-slate-300 text-lg max-w-2xl">
                        {archetype || "Your archetype represents the unique combination of your Purpose, Relevance, and Identity patterns."}
                    </p>
                </div>

                {/* Optional Action Button */}
                {/* <div className="mt-6 md:mt-0">
            <button className="bg-white text-indigo-600 hover:bg-indigo-50 px-6 py-2 rounded-lg font-semibold transition-colors shadow-sm">
                Explore Details
            </button>
        </div> */}
            </div>
        </div>
    );
};

export default ArchetypeCard;

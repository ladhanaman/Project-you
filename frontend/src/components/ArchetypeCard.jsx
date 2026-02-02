import React from 'react';
import { Award, Star, Compass } from 'lucide-react';
import { ARCHETYPE_IMAGES } from '../data/archetypeImages';

const ArchetypeCard = ({ archetype, displayArchetype, variant = 'glass' }) => {
    // Get the image based on displayArchetype, fallback to a default if not found
    const avatarImage = ARCHETYPE_IMAGES[displayArchetype];

    // Style variants
    const styles = {
        glass: "glass-panel-dark rounded-xl p-6 sm:p-8 relative overflow-hidden min-h-[250px] flex items-center transition-all duration-500 hover:shadow-purple-500/20",
        classic: "bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl shadow-lg text-white p-6 sm:p-8 relative overflow-hidden min-h-[250px] flex items-center"
    };

    return (
        <div className={styles[variant] || styles.glass}>
            {/* Decorative background elements (adjusted for variant) */}
            <div className={`absolute top-0 right-0 -mt-10 -mr-10 w-40 h-40 rounded-full blur-3xl animate-pulse ${variant === 'classic' ? 'bg-white opacity-10' : 'bg-white opacity-5'}`}></div>
            <div className={`absolute bottom-0 left-0 -mb-10 -ml-10 w-40 h-40 rounded-full blur-3xl ${variant === 'classic' ? 'bg-purple-400 opacity-10' : 'bg-purple-500 opacity-20'}`}></div>

            <div className="relative z-10 flex flex-col md:flex-row items-center md:items-center gap-6 text-center md:text-left w-full">
                {/* Avatar Image */}
                <div className="flex-shrink-0 animate-slide-up-fade" style={{ animationDelay: '0.1s' }}>
                    <div className={`w-20 h-20 rounded-2xl flex items-center justify-center backdrop-blur-md border shadow-inner group transition-transform duration-500 hover:scale-105 hover:rotate-3 ${variant === 'classic' ? 'bg-white/20 border-white/30' : 'bg-gradient-to-br from-white/10 to-white/5 border-white/20'}`}>
                        <Star className="w-10 h-10 text-white fill-white/50 drop-shadow-[0_0_10px_rgba(255,255,255,0.5)]" />
                    </div>
                </div>

                {/* Content */}
                <div className="flex-1 animate-slide-up-fade" style={{ animationDelay: '0.2s' }}>
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 border border-white/10 text-xs font-medium uppercase tracking-wider mb-3 text-slate-200">
                        <Star className="w-3 h-3 text-yellow-300 fill-yellow-300" />
                        Your Core Archetype
                    </div>

                    <h2 className="text-2xl sm:text-4xl font-bold mb-3 text-white drop-shadow-sm">
                        {displayArchetype || "Discovering..."}
                    </h2>

                    <p className="text-slate-300 text-lg max-w-2xl leading-relaxed font-light">
                        {archetype || "Your archetype represents the unique combination of your Purpose, Relevance, and Identity patterns."}
                    </p>
                </div>
            </div>
        </div>
    );
};

export default ArchetypeCard;

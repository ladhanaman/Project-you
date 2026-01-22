import React, { useState, useRef, useEffect } from 'react';
import { Palette, Check } from 'lucide-react';
import { useTheme, THEMES } from '../contexts/ThemeContext';

export default function ThemeSwitcher() {
    const { theme, setTheme } = useTheme();
    const [isOpen, setIsOpen] = useState(false);
    const dropdownRef = useRef(null);

    const themes = [
        {
            id: THEMES.CLASSIC,
            name: 'Classic',
            desc: 'Professional slate'
        },
        {
            id: THEMES.INDIGO,
            name: 'Indigo',
            desc: 'Vibrant purple'
        },
        {
            id: THEMES.OCEAN,
            name: 'Ocean',
            desc: 'Calm blue'
        },
        {
            id: THEMES.SUNSET,
            name: 'Sunset',
            desc: 'Warm orange'
        },
    ];

    // Close dropdown when clicking outside
    useEffect(() => {
        function handleClickOutside(event) {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        }

        if (isOpen) {
            document.addEventListener('mousedown', handleClickOutside);
            return () => document.removeEventListener('mousedown', handleClickOutside);
        }
    }, [isOpen]);

    const currentTheme = themes.find(t => t.id === theme);

    return (
        <div className="relative" ref={dropdownRef}>
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:text-gray-900 hover:bg-white/80 rounded-lg transition border border-gray-200 backdrop-blur-sm"
                aria-label="Change theme"
            >
                <Palette className="w-5 h-5" />
                <span className="hidden sm:inline">Theme</span>
            </button>

            {isOpen && (
                <div className="absolute right-0 mt-2 w-56 bg-white/95 backdrop-blur-md rounded-xl shadow-xl border border-gray-200 p-2 z-50 animate-fade-in">
                    <div className="px-3 py-2 border-b border-gray-100 mb-2">
                        <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Choose Theme</p>
                    </div>
                    {themes.map((t) => (
                        <button
                            key={t.id}
                            onClick={() => {
                                setTheme(t.id);
                                setIsOpen(false);
                            }}
                            className={`w-full flex items-center justify-between gap-3 px-3 py-2.5 rounded-lg transition group ${theme === t.id
                                ? 'bg-accent-lighter border border-accent-light'
                                : 'hover:bg-gray-50'
                                }`}
                        >
                            <div className="text-left">
                                <div className={`font-semibold text-sm ${theme === t.id ? 'text-gray-900' : 'text-gray-700'}`}>
                                    {t.name}
                                </div>
                                <div className="text-xs text-gray-500">{t.desc}</div>
                            </div>
                            {theme === t.id && (
                                <Check className="w-4 h-4 text-accent" />
                            )}
                        </button>
                    ))}
                </div>
            )}
        </div>
    );
}

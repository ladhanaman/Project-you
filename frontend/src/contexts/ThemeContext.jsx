import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const THEMES = {
    CLASSIC: 'classic',
    INDIGO: 'indigo',
    OCEAN: 'ocean',
    SUNSET: 'sunset',
};

export function ThemeProvider({ children }) {
    const [theme, setTheme] = useState(() => {
        // Load from localStorage or default to indigo (current theme)
        return localStorage.getItem('app-theme') || THEMES.INDIGO;
    });

    useEffect(() => {
        // Apply theme to <html> element
        document.documentElement.setAttribute('data-theme', theme);
        // Save to localStorage
        localStorage.setItem('app-theme', theme);
    }, [theme]);

    const value = {
        theme,
        setTheme,
        themes: THEMES,
    };

    return (
        <ThemeContext.Provider value={value}>
            {children}
        </ThemeContext.Provider>
    );
}

export function useTheme() {
    const context = useContext(ThemeContext);
    if (!context) {
        throw new Error('useTheme must be used within ThemeProvider');
    }
    return context;
}

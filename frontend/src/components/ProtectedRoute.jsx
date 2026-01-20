// src/components/ProtectedRoute.jsx
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useStore } from '../store/useStore';

export default function ProtectedRoute({ children }) {
    const { token } = useStore();

    if (!token) {
        return <Navigate to="/" replace />;
    }

    return children;
}

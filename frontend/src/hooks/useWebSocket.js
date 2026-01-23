// src/hooks/useWebSocket.js
import { useEffect, useState, useCallback } from 'react';

export function useWebSocket(submissionId) {
    const [status, setStatus] = useState(null);
    const [connected, setConnected] = useState(false);
    const [ws, setWs] = useState(null);

    useEffect(() => {
        if (!submissionId) return;

        const token = localStorage.getItem('token');
        if (!token) return;

        // Determine WebSocket protocol based on current protocol
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host.includes('localhost')
            ? 'localhost:8000'
            : window.location.host;

        const wsUrl = `${protocol}//${host}/ws/submission/${submissionId}?token=${encodeURIComponent(token)}`;

        console.log('[WebSocket] Connecting to:', wsUrl);
        const websocket = new WebSocket(wsUrl);

        websocket.onopen = () => {
            console.log('[WebSocket] Connected');
            setConnected(true);
        };

        websocket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log('[WebSocket] Message received:', data);

                if (data.type === 'report_status' &&
                    data.submission_id === parseInt(submissionId)) {
                    console.log('[WebSocket] Status update for submission:', submissionId, data.status);
                    setStatus(data.status);
                }
            } catch (error) {
                console.error('[WebSocket] Error parsing message:', error);
            }
        };

        websocket.onerror = (error) => {
            console.error('[WebSocket] Error:', error);
            setConnected(false);
        };

        websocket.onclose = () => {
            console.log('[WebSocket] Disconnected');
            setConnected(false);
        };

        setWs(websocket);

        return () => {
            console.log('[WebSocket] Cleaning up connection');
            websocket.close();
        };
    }, [submissionId]);

    return { status, connected };
}

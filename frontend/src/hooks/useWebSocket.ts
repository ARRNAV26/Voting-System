import { useEffect, useRef, useCallback, useState } from 'react';
import { WebSocketMessage, VoteUpdateMessage, SuggestionUpdateMessage } from '../types';
import { API_BASE_URL } from '../lib/api';

interface UseWebSocketOptions {
  onVoteUpdate?: (data: VoteUpdateMessage) => void;
  onSuggestionUpdate?: (data: SuggestionUpdateMessage) => void;
  onNewSuggestion?: (data: any) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: any) => void;
}

export const useWebSocket = (userId?: number, options: UseWebSocketOptions = {}) => {
  const ws = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const connect = useCallback(() => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      return;
    }

    // Construct WebSocket URL from API base URL
    const apiHost = API_BASE_URL.replace('/api', '');
    const wsProtocol = apiHost.startsWith('https') ? 'wss' : 'ws';
    const wsBaseUrl = apiHost.replace(/^https?/, wsProtocol);
    const wsPath = userId ? `/api/ws/${userId}` : '/api/ws';
    const wsUrl = `${wsBaseUrl}${wsPath}`;

    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      setIsConnected(true);
      setError(null);
      options.onConnect?.();
    };

    ws.current.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        
        switch (message.type) {
          case 'vote_update':
            options.onVoteUpdate?.(message.data as VoteUpdateMessage);
            break;
          case 'suggestion_update':
            options.onSuggestionUpdate?.(message.data as SuggestionUpdateMessage);
            break;
          case 'new_suggestion':
            options.onNewSuggestion?.(message.data);
            break;
          case 'connection_established':
            console.log('WebSocket connected:', message.message);
            break;
          case 'error':
            setError(message.data?.message || 'WebSocket error');
            options.onError?.(message.data);
            break;
          default:
            console.log('Unknown WebSocket message type:', message.type);
        }
      } catch (err) {
        console.error('Error parsing WebSocket message:', err);
        setError('Failed to parse message');
      }
    };

    ws.current.onclose = () => {
      setIsConnected(false);
      options.onDisconnect?.();
    };

    ws.current.onerror = (event) => {
      setError('WebSocket connection error');
      options.onError?.(event);
    };
  }, [userId, options]);

  const disconnect = useCallback(() => {
    if (ws.current) {
      ws.current.close();
      ws.current = null;
    }
  }, []);

  const sendMessage = useCallback((message: any) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    }
  }, []);

  const ping = useCallback(() => {
    sendMessage({
      type: 'ping',
      timestamp: Date.now()
    });
  }, [sendMessage]);

  useEffect(() => {
    if (userId) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [userId, connect, disconnect]);

  // Auto-reconnect on disconnect
  useEffect(() => {
    if (!isConnected && userId) {
      const timeout = setTimeout(() => {
        connect();
      }, 1000);

      return () => clearTimeout(timeout);
    }
  }, [isConnected, userId, connect]);

  return {
    isConnected,
    error,
    sendMessage,
    ping,
    connect,
    disconnect
  };
};

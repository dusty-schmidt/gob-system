// /home/ds/sambashare/GOB/frontend/src/components/LogViewerPlugin.tsx
import React, { useState, useEffect, useRef } from 'react';
import { useChatStore } from '../store/chatStore';
import './LogViewerPlugin.css';

interface LogItem {
  // Define the structure of a log item based on what the API returns
  // This is a guess for now and may need to be adjusted
  id: string;
  type: string;
  heading: string;
  content: string;
  timestamp: string;
}

const LogViewerPlugin: React.FC = () => {
  const [logs, setLogs] = useState<LogItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { activeContextId } = useChatStore();
  const contentRef = useRef<HTMLDivElement>(null);

  const fetchLogs = async (contextId: string) => {
    if (!contextId) return;
    setIsLoading(true);
    try {
      // First, fetch the dynamic API token
      const tokenResponse = await fetch('/api_get_token');
      if (!tokenResponse.ok) throw new Error('Failed to fetch API token');
      const tokenData = await tokenResponse.json();
      const apiKey = tokenData.token;

      if (!apiKey) throw new Error('API key is missing');

      const response = await fetch(`/api_log_get?context_id=${contextId}&length=200`, {
        headers: {
          'X-API-KEY': apiKey,
        },
      });

      if (!response.ok) throw new Error('Failed to fetch logs');
      const data = await response.json();
      setLogs(data.log.items || []);
    } catch (error) {
      console.error('Error fetching logs:', error);
      // setLogs([{ type: 'error', heading: 'Error', content: 'Could not load logs.' }]);
    }
    setIsLoading(false);
  };

  useEffect(() => {
    if (activeContextId) {
      fetchLogs(activeContextId);
      const interval = setInterval(() => fetchLogs(activeContextId), 5000); // Poll every 5 seconds
      return () => clearInterval(interval);
    }
  }, [activeContextId]);

  useEffect(() => {
    // Auto-scroll to the bottom
    if (contentRef.current) {
      contentRef.current.scrollTop = contentRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div className="plugin-header">SYSTEM_LOG</div>
      <div ref={contentRef} className="plugin-content log-content">
        {isLoading && logs.length === 0 && <div>Loading logs...</div>}
        {logs.map((log, index) => (
          <div key={log.id || index} className={`log-item log-type-${log.type}`}>
            <span className="log-timestamp">{new Date(log.timestamp).toLocaleTimeString()}</span>
            <span className="log-heading">{log.heading}:</span>
            <span className="log-content">{log.content}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default LogViewerPlugin;

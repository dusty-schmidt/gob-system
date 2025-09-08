// /home/ds/sambashare/GOB/frontend/src/components/SystemMonitorPlugin.tsx
import React, { useState, useEffect } from 'react';
import { useChatStore } from '../store/chatStore';
import './SystemMonitorPlugin.css';

interface SystemState {
  connectionStatus: string;
  uptime: number; // Assuming uptime is in seconds
}

const SystemMonitorPlugin: React.FC = () => {
  const [state, setState] = useState<SystemState | null>(null);
  const { activeContextId } = useChatStore();

  const fetchState = async () => {
    try {
      const response = await fetch('/state');
      if (!response.ok) throw new Error('Failed to fetch state');
      const data = await response.json();
      setState({
        connectionStatus: data.connectionStatus || 'Unknown',
        uptime: data.uptime || 0,
      });
    } catch (error) {
      console.error('Error fetching system state:', error);
      setState({ connectionStatus: 'Error', uptime: 0 });
    }
  };

  useEffect(() => {
    fetchState();
    const interval = setInterval(fetchState, 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const handleControlClick = async (action: 'start' | 'stop' | 'restart') => {
    try {
      if (action === 'restart') {
        await fetch('/restart', { method: 'POST' });
        // The backend will restart, the frontend will reconnect on the next poll
      } else {
        const paused = action === 'stop';
        await fetch('/pause', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ paused, context: activeContextId || 'default' }),
        });
        // Refresh state immediately after pausing/unpausing
        fetchState();
      }
    } catch (error) {
      console.error(`Error performing action: ${action}`, error);
    }
  };

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / (24 * 3600));
    seconds %= (24 * 3600);
    const hours = Math.floor(seconds / 3600);
    seconds %= 3600;
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${days}d ${hours}h ${minutes}m ${secs}s`;
  };

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div className="plugin-header">SYSTEM_MONITOR</div>
      <div className="plugin-content monitor-content">
        <div className="monitor-item">
          <span className="monitor-label">Status:</span>
          <span className={`monitor-value status-${state?.connectionStatus.toLowerCase()}`}>
            {state?.connectionStatus || 'Loading...'}
          </span>
        </div>
        <div className="monitor-item">
          <span className="monitor-label">Uptime:</span>
          <span className="monitor-value">
            {state ? formatUptime(state.uptime) : 'Loading...'}
          </span>
        </div>
        <div className="monitor-controls">
          <button onClick={() => handleControlClick('start')} disabled={!activeContextId}>Start</button>
          <button onClick={() => handleControlClick('stop')} disabled={!activeContextId}>Stop</button>
          <button onClick={() => handleControlClick('restart')}>Restart</button>
        </div>
      </div>
    </div>
  );
};

export default SystemMonitorPlugin;
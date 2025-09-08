// /home/ds/sambashare/GOB/frontend/src/components/ChatbotPlugin.tsx
import React, { useState, useEffect, useRef } from 'react';
import { useChatStore } from '../store/chatStore';

interface Message {
  sender: 'user' | 'agent';
  text: string;
}

const ChatbotPlugin: React.FC = () => {
  const [history, setHistory] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const contentRef = useRef<HTMLDivElement>(null);
  const { activeContextId } = useChatStore();

  // --- API Calls ---

  const fetchHistory = async (contextId: string) => {
    if (!contextId) return;
    setIsLoading(true);
    setHistory([]); // Clear history while loading new context
    try {
      const response = await fetch('/history_get', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ context: contextId }),
      });
      if (!response.ok) throw new Error('Failed to fetch history');
      const data = await response.json();
      
      const parsedHistory: Message[] = data.history.split('\n').map((line: string) => {
        if (line.startsWith('User:')) {
          return { sender: 'user', text: line.replace('User:', '').trim() };
        }
        return { sender: 'agent', text: line.replace('Agent:', '').trim() };
      }).filter((msg: Message) => msg.text);

      setHistory(parsedHistory);
    } catch (error) {
      console.error('Error fetching history:', error);
      setHistory([{ sender: 'agent', text: 'Error: Could not load history.' }]);
    }
    setIsLoading(false);
  };

  const sendMessage = async (text: string) => {
    if (!text.trim() || !activeContextId) return;

    const userMessage: Message = { sender: 'user', text };
    setHistory(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, context: activeContextId }),
      });
      if (!response.ok) throw new Error('Failed to send message');
      const data = await response.json();
      
      const agentMessage: Message = { sender: 'agent', text: data.message };
      setHistory(prev => [...prev, agentMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      setHistory(prev => [...prev, { sender: 'agent', text: 'Error: Could not get response.' }]);
    }
    setIsLoading(false);
  };

  // --- Effects ---

  useEffect(() => {
    if (activeContextId) {
      fetchHistory(activeContextId);
    }
  }, [activeContextId]);

  useEffect(() => {
    // Auto-scroll to the bottom of the chat history
    if (contentRef.current) {
      contentRef.current.scrollTop = contentRef.current.scrollHeight;
    }
  }, [history]);


  // --- Event Handlers ---

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value);
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !isLoading) {
      sendMessage(input);
    }
  };

  // --- Render ---

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div className="plugin-header">AGENT_CHAT</div>
      <div ref={contentRef} className="plugin-content" style={{ flexGrow: 1, overflowY: 'auto' }}>
        {history.map((msg, index) => (
          <div key={index}>
            <span style={{ color: msg.sender === 'user' ? '#d4d4d4' : '#a4a4a4' }}>
              {msg.sender === 'user' ? '> ' : ''}
            </span>
            {msg.text}
          </div>
        ))}
        {isLoading && <div>...</div>}
      </div>
      <input
        type="text"
        value={input}
        onChange={handleInputChange}
        onKeyPress={handleKeyPress}
        disabled={isLoading || !activeContextId}
        style={{
          background: 'transparent',
          border: 'none',
          borderTop: '1px solid var(--color-border-dark)',
          color: 'var(--color-text-dark)',
          padding: '8px',
          fontFamily: 'inherit',
          fontSize: 'inherit',
          outline: 'none',
        }}
        placeholder={activeContextId ? "Type your message..." : "Create a new chat to begin..."}
      />
    </div>
  );
};

export default ChatbotPlugin;

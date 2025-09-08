// /home/ds/sambashare/GOB/frontend/srcs/components/Sidebar.tsx
import React, { useEffect } from 'react';
import { useChatStore } from '../store/chatStore';
import './Sidebar.css';

const Sidebar: React.FC = () => {
  const { 
    contexts, 
    activeContextId, 
    fetchChatContexts, 
    setActiveContextId,
    createNewChat 
  } = useChatStore();

  useEffect(() => {
    fetchChatContexts();
  }, [fetchChatContexts]);

  return (
    <div id="sidebar-content">
      <h3>GOB Control</h3>
      <div className="sidebar-actions">
        <button onClick={createNewChat}>New Chat</button>
      </div>
      <ul className="chat-list">
        {contexts.map((context) => (
          <li
            key={context.id}
            className={context.id === activeContextId ? 'active' : ''}
            onClick={() => setActiveContextId(context.id)}
          >
            {context.name || `Chat #${context.no}`}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Sidebar;

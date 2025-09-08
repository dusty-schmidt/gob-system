// /home/ds/sambashare/GOB/frontend/src/App.tsx
import React, { useState } from 'react';
import GridLayout from 'react-grid-layout';
import './App.css';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';
import ChatbotPlugin from './components/ChatbotPlugin';
import SystemMonitorPlugin from './components/SystemMonitorPlugin';
import LogViewerPlugin from './components/LogViewerPlugin';
import Sidebar from './components/Sidebar';

const App: React.FC = () => {
  const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);

  const layout = [
    { i: 'monitor', x: 0, y: 0, w: 12, h: 2 },
    { i: 'chat', x: 0, y: 2, w: 7, h: 8 },
    { i: 'logs', x: 7, y: 2, w: 5, h: 8 },
  ];

  const toggleSidebar = () => {
    setSidebarCollapsed(!isSidebarCollapsed);
    // This is a trick to get react-grid-layout to recalculate its width
    window.dispatchEvent(new Event('resize'));
  };

  return (
    <div className="App">
      <div id="sidebar" className={isSidebarCollapsed ? 'collapsed' : ''}>
        <Sidebar />
      </div>
      <div id="main-content">
        <button className="sidebar-toggle" onClick={toggleSidebar}>
          {isSidebarCollapsed ? '>' : '<'}
        </button>
        <GridLayout
          className="layout"
          layout={layout}
          cols={12}
          rowHeight={50}
          width={isSidebarCollapsed ? window.innerWidth : window.innerWidth - 250}
          isDraggable={true}
          isResizable={true}
        >
          <div key="monitor">
            <SystemMonitorPlugin />
          </div>
          <div key="logs">
            <LogViewerPlugin />
          </div>
          <div key="chat">
            <ChatbotPlugin />
          </div>
        </GridLayout>
      </div>
    </div>
  );
};

export default App;
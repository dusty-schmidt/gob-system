// /home/ds/sambashare/GOB/frontend/src/store/chatStore.ts
import { create } from 'zustand';

interface ChatContext {
  id: string;
  name: string;
  no: number;
}

interface ChatState {
  contexts: ChatContext[];
  activeContextId: string | null;
  fetchChatContexts: () => Promise<void>;
  setActiveContextId: (id: string) => void;
  createNewChat: () => Promise<void>;
}

export const useChatStore = create<ChatState>((set, get) => ({
  contexts: [],
  activeContextId: null,

  fetchChatContexts: async () => {
    try {
      const response = await fetch('/state');
      if (!response.ok) throw new Error('Failed to fetch state');
      const data = await response.json();
      
      const contexts = data.contexts || [];
      set({ contexts });

      // If there's no active context, set the first one as active
      if (!get().activeContextId && contexts.length > 0) {
        set({ activeContextId: contexts[0].id });
      }
    } catch (error) {
      console.error('Error fetching chat contexts:', error);
    }
  },

  setActiveContextId: (id: string) => {
    set({ activeContextId: id });
  },

  createNewChat: async () => {
    try {
        // The '/reset_chat' endpoint likely creates a new chat context if none is provided
        const response = await fetch('/reset_chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({}), 
        });
        if (!response.ok) throw new Error('Failed to create new chat');
        
        // After creating, fetch the updated list of contexts
        await get().fetchChatContexts();

    } catch (error) {
        console.error('Error creating new chat:', error);
    }
  }
}));

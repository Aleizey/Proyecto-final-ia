import { useState, useCallback } from 'react';

const API_BASE = import.meta.env.VITE_APP_BACKEND_URL || 'http://localhost:8000';

export function useChat() {
  const [conversations, setConversations] = useState([]);
  const [currentThreadId, setCurrentThreadId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingConversations, setLoadingConversations] = useState(false);

  const loadConversations = useCallback(async () => {
    setLoadingConversations(true);
    try {
      const response = await fetch(`${API_BASE}/conversations`);
      const data = await response.json();
      setConversations(data.conversations || []);
    } catch (e) {
      console.error('Error loading conversations:', e);
    }
    setLoadingConversations(false);
  }, []);

  const loadConversationHistory = useCallback(async (threadId) => {
    try {
      const response = await fetch(`${API_BASE}/conversations/${threadId}`);
      const data = await response.json();
      const formattedMessages = data.messages.map(msg => ({
        type: msg.type === 'HumanMessage' ? 'user' : 'ai',
        content: msg.content
      }));
      setMessages(formattedMessages);
    } catch (e) {
      console.error('Error loading history:', e);
      setMessages([]);
    }
  }, []);

  const createConversation = useCallback(async (shouldClearMessages = true) => {
    try {
      const response = await fetch(`${API_BASE}/conversations`, { method: 'POST' });
      const data = await response.json();
      setCurrentThreadId(data.thread_id);
      if (shouldClearMessages) {
        setMessages([]);
      }
      loadConversations();
      return data.thread_id;
    } catch (e) {
      console.error('Error creating conversation:', e);
      return null;
    }
  }, [loadConversations]);

  const deleteConversation = useCallback(async (threadId) => {
    try {
      await fetch(`${API_BASE}/conversations/${threadId}`, { method: 'DELETE' });
      if (currentThreadId === threadId) {
        setCurrentThreadId(null);
        setMessages([]);
      }
      loadConversations();
    } catch (e) {
      console.error('Error deleting conversation:', e);
    }
  }, [currentThreadId, loadConversations]);

  const sendMessage = useCallback(async (message, threadId) => {
    setLoading(true);
    
    let currentThread = threadId;
    let isNewConversation = false;
    if (!currentThread) {
      const response = await fetch(`${API_BASE}/conversations`, { method: 'POST' });
      const data = await response.json();
      currentThread = data.thread_id;
      setCurrentThreadId(currentThread);
      isNewConversation = true;
      loadConversations();
    }

    const userMessage = { type: 'user', content: message };
    setMessages(prev => [...prev, userMessage]);

    try {
      const response = await fetch(`${API_BASE}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, thread_id: currentThread }),
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let aiResponse = '';
      let reasoning = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value);
        const lines = chunk.split("\n").filter(line => line.trim());
        for (const line of lines) {
          try {
            const data = JSON.parse(line);
            aiResponse = data.content || '';
            reasoning = data.reasoning || '';
          } catch (e) {}
        }
      }

      setMessages(prev => [...prev, { type: 'ai', content: aiResponse, reasoning }]);
      return currentThread;
    } catch (e) {
      console.error('Error sending message:', e);
      return null;
    } finally {
      setLoading(false);
    }
  }, [loadConversations]);

  const selectConversation = useCallback((threadId) => {
    setCurrentThreadId(threadId);
  }, []);

  return {
    conversations,
    currentThreadId,
    messages,
    loading,
    loadingConversations,
    loadConversations,
    loadConversationHistory,
    createConversation,
    deleteConversation,
    sendMessage,
    selectConversation,
  };
}
import { useState } from 'react';
import { useChatStore } from '../store/useStore';
import { aiService } from '../services/api';
import { ChatMessage } from '../types';

export function useAIChat() {
  const { messages, addMessage, isLoading, setLoading, model, setMessages } = useChatStore();
  const [error, setError] = useState<string | null>(null);

  const sendMessage = async (content: string, contextPaperIds?: number[]) => {
    if (!content.trim()) return;

    // Add user message
    const userMessage: ChatMessage = { role: 'user', content };
    addMessage(userMessage);
    setLoading(true);
    setError(null);

    try {
      const response = await aiService.chat(
        [...messages, userMessage],
        model,
        contextPaperIds
      );

      // Add assistant response
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.response,
      };
      addMessage(assistantMessage);
    } catch (err: any) {
      setError(err.message || 'Failed to send message');
      
      // Add error message
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: `Error: ${err.message || 'Failed to get response'}`,
      };
      addMessage(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
    setError(null);
  };

  return {
    messages,
    isLoading,
    error,
    model,
    sendMessage,
    clearChat,
  };
}

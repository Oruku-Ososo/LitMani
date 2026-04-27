import axios from 'axios';

const API_BASE_URL = '/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// AI Service
export const aiService = {
  chat: async (messages: any[], model?: string, contextPaperIds?: number[]) => {
    const response = await apiClient.post('/ai/chat', {
      messages,
      model,
      context_paper_ids: contextPaperIds,
    });
    return response.data;
  },

  summarize: async (paperId: number, length: string = 'medium', style: string = 'academic') => {
    const response = await apiClient.post('/ai/summarize', {
      paper_id: paperId,
      length,
      style,
    });
    return response.data;
  },

  suggestTags: async (paperId?: number, text?: string) => {
    const response = await apiClient.post('/ai/suggest-tags', {
      paper_id: paperId,
      text,
    });
    return response.data;
  },

  generateCitation: async (paperId: number, style: string = 'apa') => {
    const response = await apiClient.post('/ai/generate-citation', {
      paper_id: paperId,
      style,
    });
    return response.data;
  },

  listModels: async () => {
    const response = await apiClient.get('/ai/models');
    return response.data;
  },
};

// Paper Service (placeholder - would need full implementation)
export const paperService = {
  getAll: async () => {
    const response = await apiClient.get('/papers');
    return response.data;
  },

  getById: async (id: number) => {
    const response = await apiClient.get(`/papers/${id}`);
    return response.data;
  },

  create: async (data: any) => {
    const response = await apiClient.post('/papers', data);
    return response.data;
  },

  update: async (id: number, data: any) => {
    const response = await apiClient.put(`/papers/${id}`, data);
    return response.data;
  },

  delete: async (id: number) => {
    const response = await apiClient.delete(`/papers/${id}`);
    return response.data;
  },
};

// Collection Service (placeholder)
export const collectionService = {
  getAll: async () => {
    const response = await apiClient.get('/collections');
    return response.data;
  },

  create: async (data: any) => {
    const response = await apiClient.post('/collections', data);
    return response.data;
  },
};

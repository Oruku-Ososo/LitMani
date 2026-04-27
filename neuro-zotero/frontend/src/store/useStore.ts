import { create } from 'zustand';
import { Paper, Collection } from '../types';

interface LibraryState {
  papers: Paper[];
  collections: Collection[];
  selectedPaperId: number | null;
  selectedCollectionId: number | null;
  searchQuery: string;
  
  // Actions
  setPapers: (papers: Paper[]) => void;
  setCollections: (collections: Collection[]) => void;
  setSelectedPaper: (id: number | null) => void;
  setSelectedCollection: (id: number | null) => void;
  setSearchQuery: (query: string) => void;
  addPaper: (paper: Paper) => void;
  updatePaper: (id: number, paper: Partial<Paper>) => void;
  deletePaper: (id: number) => void;
}

export const useLibraryStore = create<LibraryState>((set) => ({
  papers: [],
  collections: [],
  selectedPaperId: null,
  selectedCollectionId: null,
  searchQuery: '',
  
  setPapers: (papers) => set({ papers }),
  setCollections: (collections) => set({ collections }),
  setSelectedPaper: (id) => set({ selectedPaperId: id }),
  setSelectedCollection: (id) => set({ selectedCollectionId: id }),
  setSearchQuery: (query) => set({ searchQuery: query }),
  
  addPaper: (paper) => set((state) => ({ 
    papers: [...state.papers, paper] 
  })),
  
  updatePaper: (id, updatedPaper) => set((state) => ({
    papers: state.papers.map(p => 
      p.id === id ? { ...p, ...updatedPaper } : p
    )
  })),
  
  deletePaper: (id) => set((state) => ({
    papers: state.papers.filter(p => p.id !== id)
  })),
}));

// AI Chat Store
import { ChatMessage } from '../types';

interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  model: string;
  
  // Actions
  addMessage: (message: ChatMessage) => void;
  setMessages: (messages: ChatMessage[]) => void;
  setLoading: (loading: boolean) => void;
  setModel: (model: string) => void;
  clearChat: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  isLoading: false,
  model: 'llama2',
  
  addMessage: (message) => set((state) => ({
    messages: [...state.messages, message]
  })),
  
  setMessages: (messages) => set({ messages }),
  setLoading: (loading) => set({ isLoading: loading }),
  setModel: (model) => set({ model }),
  clearChat: () => set({ messages: [] }),
}));

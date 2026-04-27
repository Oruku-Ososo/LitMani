import { useState } from 'react';
import { aiService } from '../services/api';

export function usePaperAI() {
  const [isSummarizing, setIsSummarizing] = useState(false);
  const [summary, setSummary] = useState<any>(null);
  const [tags, setTags] = useState<string[]>([]);
  const [citation, setCitation] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const summarizePaper = async (paperId: number, length: string = 'medium') => {
    setIsSummarizing(true);
    setError(null);
    
    try {
      const result = await aiService.summarize(paperId, length);
      setSummary(result);
      return result;
    } catch (err: any) {
      setError(err.message || 'Failed to summarize paper');
      throw err;
    } finally {
      setIsSummarizing(false);
    }
  };

  const getSuggestedTags = async (paperId?: number, text?: string) => {
    setError(null);
    
    try {
      const result = await aiService.suggestTags(paperId, text);
      setTags(result.tags);
      return result.tags;
    } catch (err: any) {
      setError(err.message || 'Failed to get tag suggestions');
      throw err;
    }
  };

  const generateCitation = async (paperId: number, style: string = 'apa') => {
    setError(null);
    
    try {
      const result = await aiService.generateCitation(paperId, style);
      setCitation(result);
      return result;
    } catch (err: any) {
      setError(err.message || 'Failed to generate citation');
      throw err;
    }
  };

  const clearResults = () => {
    setSummary(null);
    setTags([]);
    setCitation(null);
    setError(null);
  };

  return {
    isSummarizing,
    summary,
    tags,
    citation,
    error,
    summarizePaper,
    getSuggestedTags,
    generateCitation,
    clearResults,
  };
}

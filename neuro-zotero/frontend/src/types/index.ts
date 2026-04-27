export interface Paper {
  id: number;
  title: string;
  authors?: Author[];
  abstract?: string;
  doi?: string;
  journal?: string;
  publication_date?: string;
  tags?: string[];
  file_path?: string;
  created_at: string;
  updated_at?: string;
}

export interface Author {
  name: string;
  affiliation?: string;
  email?: string;
}

export interface Collection {
  id: number;
  name: string;
  description?: string;
  color?: string;
  icon?: string;
  parent_id?: number;
  paper_count?: number;
  created_at: string;
}

export interface Annotation {
  id: number;
  paper_id: number;
  page_number: number;
  annotation_type: 'highlight' | 'underline' | 'note' | 'strikeout';
  content?: string;
  color?: string;
  comment?: string;
  created_at: string;
}

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export interface AISummary {
  summary: string;
  key_points: string[];
  model_used: string;
}

export interface TagSuggestion {
  tags: string[];
  confidence_scores: number[];
  model_used: string;
}

export interface Citation {
  citation: string;
  style: string;
  bibtex?: string;
}

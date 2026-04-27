import { useState } from 'react';
import { BookOpen, MessageSquare, Search, Folder, Plus } from 'lucide-react';
import { useLibraryStore } from '../store/useStore';
import { AIChatPanel } from './AIChatPanel';
import { PaperDetail } from './PaperDetail';
import { Paper } from '../types';

// Mock data for demonstration
const mockPapers: Paper[] = [
  {
    id: 1,
    title: "Attention Is All You Need",
    authors: [{ name: "Vaswani, A." }, { name: "Shazeer, N." }, { name: "Parmar, N." }],
    abstract: "We propose a new simple network architecture, the Transformer, based solely on attention mechanisms...",
    doi: "10.48550/arXiv.1706.03762",
    journal: "arXiv preprint",
    publication_date: "2017-06-12",
    tags: ["transformer", "attention", "nlp"],
    created_at: "2024-01-15T10:00:00Z",
  },
  {
    id: 2,
    title: "BERT: Pre-training of Deep Bidirectional Transformers",
    authors: [{ name: "Devlin, J." }, { name: "Chang, M.W." }, { name: "Lee, K." }],
    abstract: "We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers...",
    doi: "10.48550/arXiv.1810.04805",
    journal: "NAACL-HLT",
    publication_date: "2018-10-11",
    tags: ["bert", "nlp", "pre-training"],
    created_at: "2024-01-16T10:00:00Z",
  },
];

export default function App() {
  const { papers, selectedPaperId, setSelectedPaper, searchQuery, setSearchQuery } = useLibraryStore();
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [selectedPaper, setSelectedPaperDetail] = useState<Paper | null>(null);

  // Initialize with mock data
  useState(() => {
    // In real app, this would fetch from API
  });

  const filteredPapers = papers.filter(paper =>
    paper.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    paper.authors?.some(a => a.name.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <BookOpen className="w-8 h-8 text-primary-600" />
              <h1 className="text-2xl font-bold">NeuroZotero</h1>
              <span className="text-sm text-gray-500 dark:text-gray-400 ml-2">
                AI-Powered Research Manager
              </span>
            </div>
            
            <div className="flex items-center gap-3">
              <button
                onClick={() => setIsChatOpen(!isChatOpen)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
                  isChatOpen 
                    ? 'bg-primary-600 text-white' 
                    : 'bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
              >
                <MessageSquare className="w-4 h-4" />
                <span>AI Assistant</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-6 flex gap-6">
        {/* Sidebar */}
        <aside className="w-64 flex-shrink-0">
          <div className="card">
            <nav className="space-y-2">
              <a href="#" className="flex items-center gap-2 px-3 py-2 rounded-lg bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300">
                <BookOpen className="w-4 h-4" />
                <span>All Papers</span>
              </a>
              <a href="#" className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700">
                <Folder className="w-4 h-4" />
                <span>Collections</span>
              </a>
              <a href="#" className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700">
                <Search className="w-4 h-4" />
                <span>Search</span>
              </a>
            </nav>
            
            <button className="btn-primary w-full mt-4 flex items-center justify-center gap-2">
              <Plus className="w-4 h-4" />
              <span>Add Paper</span>
            </button>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1">
          {/* Search Bar */}
          <div className="mb-6">
            <input
              type="text"
              placeholder="Search papers by title, author, or keyword..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input-field"
            />
          </div>

          {/* Papers List */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold mb-4">
              Your Library ({filteredPapers.length || mockPapers.length} papers)
            </h2>
            
            {(filteredPapers.length > 0 ? filteredPapers : mockPapers).map((paper) => (
              <div
                key={paper.id}
                className="card cursor-pointer hover:shadow-lg transition-shadow"
                onClick={() => {
                  setSelectedPaperDetail(paper);
                }}
              >
                <h3 className="font-semibold text-lg mb-2">{paper.title}</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  {paper.authors?.map(a => a.name).join(', ')}
                </p>
                {paper.abstract && (
                  <p className="text-sm text-gray-700 dark:text-gray-300 line-clamp-2">
                    {paper.abstract}
                  </p>
                )}
                <div className="flex items-center gap-2 mt-3">
                  {paper.tags?.slice(0, 3).map((tag, i) => (
                    <span
                      key={i}
                      className="px-2 py-1 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 rounded text-xs"
                    >
                      #{tag}
                    </span>
                  ))}
                  {paper.publication_date && (
                    <span className="text-xs text-gray-500 dark:text-gray-400 ml-auto">
                      {new Date(paper.publication_date).getFullYear()}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </main>
      </div>

      {/* AI Chat Panel */}
      <AIChatPanel isOpen={isChatOpen} onClose={() => setIsChatOpen(false)} />

      {/* Paper Detail Modal */}
      {selectedPaper && (
        <PaperDetail
          paper={selectedPaper}
          onClose={() => setSelectedPaperDetail(null)}
        />
      )}
    </div>
  );
}

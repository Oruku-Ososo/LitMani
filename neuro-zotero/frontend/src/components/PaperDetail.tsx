import { FileText, Calendar, Tag, Hash } from 'lucide-react';
import { Paper } from '../types';
import { usePaperAI } from '../hooks/usePaperAI';

interface PaperDetailProps {
  paper: Paper;
  onClose: () => void;
}

export function PaperDetail({ paper, onClose }: PaperDetailProps) {
  const { 
    isSummarizing, 
    summary, 
    tags, 
    citation,
    summarizePaper, 
    getSuggestedTags, 
    generateCitation 
  } = usePaperAI();

  const handleSummarize = async () => {
    try {
      await summarizePaper(paper.id);
    } catch (err) {
      console.error('Failed to summarize:', err);
    }
  };

  const handleGetTags = async () => {
    try {
      await getSuggestedTags(paper.id);
    } catch (err) {
      console.error('Failed to get tags:', err);
    }
  };

  const handleGenerateCitation = async () => {
    try {
      await generateCitation(paper.id, 'apa');
    } catch (err) {
      console.error('Failed to generate citation:', err);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <h1 className="text-2xl font-bold mb-2">{paper.title}</h1>
          <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
            {paper.publication_date && (
              <div className="flex items-center gap-1">
                <Calendar className="w-4 h-4" />
                <span>{new Date(paper.publication_date).toLocaleDateString()}</span>
              </div>
            )}
            {paper.doi && (
              <div className="flex items-center gap-1">
                <Hash className="w-4 h-4" />
                <span>{paper.doi}</span>
              </div>
            )}
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Authors */}
          {paper.authors && paper.authors.length > 0 && (
            <section>
              <h2 className="font-semibold mb-2 flex items-center gap-2">
                <FileText className="w-4 h-4" />
                Authors
              </h2>
              <p className="text-gray-700 dark:text-gray-300">
                {paper.authors.map(a => a.name).join(', ')}
              </p>
            </section>
          )}

          {/* Abstract */}
          {paper.abstract && (
            <section>
              <h2 className="font-semibold mb-2">Abstract</h2>
              <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                {paper.abstract}
              </p>
            </section>
          )}

          {/* AI Actions */}
          <section className="border-t border-gray-200 dark:border-gray-700 pt-6">
            <h2 className="font-semibold mb-3">AI Tools</h2>
            <div className="flex gap-2 mb-4">
              <button
                onClick={handleSummarize}
                disabled={isSummarizing}
                className="btn-primary text-sm"
              >
                {isSummarizing ? 'Summarizing...' : '📄 Summarize'}
              </button>
              <button
                onClick={handleGetTags}
                className="btn-secondary text-sm"
              >
                🏷️ Suggest Tags
              </button>
              <button
                onClick={handleGenerateCitation}
                className="btn-secondary text-sm"
              >
                📑 Generate Citation
              </button>
            </div>

            {/* AI Results */}
            {summary && (
              <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg mb-4">
                <h3 className="font-semibold mb-2">Summary</h3>
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  {summary.summary}
                </p>
                {summary.key_points && summary.key_points.length > 0 && (
                  <ul className="mt-2 space-y-1">
                    {summary.key_points.map((point: string, i: number) => (
                      <li key={i} className="text-sm text-gray-700 dark:text-gray-300">
                        • {point}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}

            {tags.length > 0 && (
              <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg mb-4">
                <h3 className="font-semibold mb-2 flex items-center gap-2">
                  <Tag className="w-4 h-4" />
                  Suggested Tags
                </h3>
                <div className="flex flex-wrap gap-2">
                  {tags.map((tag, i) => (
                    <span
                      key={i}
                      className="px-2 py-1 bg-green-200 dark:bg-green-800 text-green-800 dark:text-green-200 rounded text-sm"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {citation && (
              <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
                <h3 className="font-semibold mb-2">Citation ({citation.style.toUpperCase()})</h3>
                <p className="text-sm text-gray-700 dark:text-gray-300 font-mono">
                  {citation.citation}
                </p>
                {citation.bibtex && (
                  <pre className="mt-2 p-2 bg-white dark:bg-gray-800 rounded text-xs overflow-x-auto">
                    {citation.bibtex}
                  </pre>
                )}
              </div>
            )}
          </section>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-200 dark:border-gray-700 flex justify-end">
          <button onClick={onClose} className="btn-secondary">
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

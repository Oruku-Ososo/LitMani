# NeuroZotero - AI-Powered Research Manager

A next-generation research management tool that combines the best features of Zotero with powerful AI capabilities through Ollama and GGUF model integration.

## Features

### Core Features
- 📚 **Reference Management**: Import, organize, and manage research papers, books, and articles
- 🏷️ **Smart Tagging**: AI-powered automatic tagging and categorization
- 🔍 **Semantic Search**: Search your library using natural language
- 📝 **Annotation Tools**: Highlight, annotate, and add notes to PDFs
- 🔄 **Sync & Backup**: Cloud sync and local backup options
- 📑 **Citation Generator**: Generate citations in multiple formats (APA, MLA, Chicago, etc.)

### AI Features (Ollama + GGUF)
- 🤖 **AI Assistant**: Chat with your research library using local LLMs
- 📄 **Paper Summarization**: Automatic summarization of research papers
- 💡 **Research Insights**: AI-powered insights and connections between papers
- ✍️ **Writing Assistant**: Help with writing and editing research papers
- 🔗 **Related Work Discovery**: Find related papers and research gaps
- 🎯 **Smart Recommendations**: Get personalized paper recommendations

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database management
- **SQLite/PostgreSQL**: Database storage
- **Ollama**: Local LLM inference
- **GGUF**: Efficient model format for local AI
- **PyTorch/Llama.cpp**: Model execution engine

### Frontend
- **React 18**: Modern UI framework
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Zustand**: State management
- **React Query**: Data fetching and caching
- **PDF.js**: PDF rendering and annotation

## Project Structure

```
neuro-zotero/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── config.py            # Configuration settings
│   │   └── database.py          # Database setup
│   ├── models/
│   │   ├── paper.py             # Paper model
│   │   ├── collection.py        # Collection model
│   │   ├── annotation.py        # Annotation model
│   │   └── user.py              # User model
│   ├── routes/
│   │   ├── papers.py            # Paper endpoints
│   │   ├── collections.py       # Collection endpoints
│   │   ├── annotations.py       # Annotation endpoints
│   │   ├── ai.py                # AI/LLM endpoints
│   │   └── search.py            # Search endpoints
│   ├── services/
│   │   ├── ollama_service.py    # Ollama integration
│   │   ├── gguf_service.py      # GGUF model handling
│   │   ├── pdf_processor.py     # PDF processing
│   │   └── citation_service.py  # Citation generation
│   └── utils/
│       ├── parsers.py           # File parsers
│       └── embeddings.py        # Embedding generation
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Application pages
│   │   ├── hooks/               # Custom React hooks
│   │   ├── services/            # API services
│   │   ├── store/               # State management
│   │   ├── types/               # TypeScript types
│   │   └── utils/               # Utility functions
│   └── public/                  # Static assets
├── docker-compose.yml           # Docker configuration
├── requirements.txt             # Python dependencies
└── package.json                 # Node.js dependencies
```

## Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- Ollama installed locally
- Git

### Installation

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Frontend Setup
```bash
cd frontend
npm install
```

#### Ollama Setup
```bash
# Install Ollama (https://ollama.ai)
# Pull a model
ollama pull llama2
# Or use GGUF models directly
```

### Running the Application

#### Start Backend
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Start Frontend
```bash
cd frontend
npm run dev
```

#### Using Docker
```bash
docker-compose up -d
```

## API Endpoints

### Papers
- `GET /api/papers` - List all papers
- `POST /api/papers` - Add a new paper
- `GET /api/papers/{id}` - Get paper details
- `PUT /api/papers/{id}` - Update paper
- `DELETE /api/papers/{id}` - Delete paper
- `POST /api/papers/import` - Import papers from file

### Collections
- `GET /api/collections` - List all collections
- `POST /api/collections` - Create collection
- `PUT /api/collections/{id}` - Update collection
- `DELETE /api/collections/{id}` - Delete collection

### AI Features
- `POST /api/ai/chat` - Chat with AI about your library
- `POST /api/ai/summarize` - Summarize a paper
- `POST /api/ai/suggest-tags` - Get AI-suggested tags
- `POST /api/ai/find-related` - Find related papers
- `POST /api/ai/generate-citation` - Generate citation

### Search
- `GET /api/search` - Semantic search
- `GET /api/search/fulltext` - Full-text search

## Configuration

Create a `.env` file in the backend directory:

```env
DATABASE_URL=sqlite:///./neurozotero.db
OLLAMA_BASE_URL=http://localhost:11434
GGUF_MODEL_PATH=./models
SECRET_KEY=your-secret-key-here
DEBUG=True
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - feel free to use this project for your research!

## Acknowledgments

- Inspired by Zotero's excellent reference management
- Powered by Ollama for local LLM inference
- Using GGUF for efficient model storage and loading

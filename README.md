# 📜 Legalese-to-Simplese

> **Transform complex legal documents into clear, understandable insights with AI-powered analysis.**

An intelligent legal document analysis platform that helps individuals and small businesses understand contracts, agreements, and legal documents without expensive legal consultations. Upload your document, get instant AI analysis, risk assessment, and ask questions in plain language.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-00a393?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61dafb?style=flat&logo=react)](https://react.dev/)
[![Python](https://img.shields.io/badge/Python-3.12+-3776ab?style=flat&logo=python)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/Ollama-LLM-000000?style=flat)](https://ollama.ai/)
[![Elasticsearch](https://img.shields.io/badge/Elasticsearch-8.x-005571?style=flat&logo=elasticsearch)](https://www.elastic.co/)

---

## 🎯 What It Does

**Legalese-to-Simplese** democratizes legal document understanding by:

- 📄 **Analyzing Legal Documents** - Upload PDFs, DOCs, or paste text for instant analysis
- 🎯 **Risk Assessment** - Identifies high, medium, and low-risk clauses with explanations
- 💡 **Plain Language Translation** - Converts legal jargon into simple, understandable terms
- 💬 **Interactive Q&A** - Ask questions about your contract and get AI-powered answers
- 🔍 **Smart Search** - Retrieves relevant document sections using semantic search
- ⚡ **Real-time Processing** - Get comprehensive analysis in under 60 seconds

---

## 🏗️ Architecture

![Architecture Diagram](./architecture-diagram.png)

### System Components

**Frontend (React + Vite)**
- Modern, responsive web interface
- Real-time document upload and analysis
- Interactive chat interface for Q&A
- Visual risk assessment dashboard

**API Gateway (FastAPI)**
- RESTful API with automatic documentation
- CORS-enabled for cross-origin requests
- Structured logging and error handling
- File upload and processing pipeline

**Backend Services**
- **Document Controller**: Handles file uploads and orchestrates processing
- **Upload Handler**: Processes PDFs/TXT files and extracts text
- **Q&A Service**: Manages question-answering with context retrieval
- **Distribution Service**: Coordinates document analysis workflow

**AI & Search Layer**
- **LLMs (Ollama)**: 
  - `gpt-oss` for text generation and analysis
  - `nomic-embed-text` for semantic embeddings
- **Elasticsearch**: Vector search for document retrieval and context matching
- **S3 Storage**: Document persistence and backup

**Data Flow**
1. User uploads document via web portal
2. API Gateway routes to Document Controller
3. Upload Handler extracts text and creates embeddings
4. Document chunks stored in Elasticsearch with metadata
5. LLM analyzes document structure, risks, and key terms
6. Results returned to frontend for display
7. Q&A queries search Elasticsearch for relevant context
8. LLM generates answers based on retrieved document sections

---

## ✨ Key Features

### 📊 Document Analysis
- **Automatic Classification**: Identifies document type (rental agreement, employment contract, NDA, etc.)
- **Purpose Extraction**: Summarizes the main objective in plain language
- **Key Highlights**: Extracts critical obligations, rights, and deadlines
- **Risk Scoring**: 1-10 scale with categorized risk breakdown

### 🚨 Risk Assessment
- **High-Risk Identification**: Flags potentially problematic clauses
- **Medium-Risk Warnings**: Highlights areas needing attention
- **Low-Risk Notes**: Documents minor concerns
- **Detailed Explanations**: Each risk includes title and description

### 📖 Key Terms Glossary
- **Legal Jargon Translation**: Explains complex terms in simple language
- **Contextual Definitions**: Terms explained within document context
- **Searchable Reference**: Quick lookup for unfamiliar terminology

### 💬 Interactive Q&A
- **Context-Aware Answers**: AI references actual document content
- **Suggested Questions**: Pre-generated relevant questions
- **Natural Language**: Ask questions as you would to a lawyer
- **Real-time Responses**: Instant answers with typing indicators

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+** - Backend runtime
- **Node.js 18+** - Frontend development
- **Ollama** - Local LLM runtime ([Install Guide](https://ollama.ai/))
- **Elasticsearch 8.x** - Vector search engine
- **Docker** (optional) - For containerized deployment

### Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/legalese-to-simplese.git
cd legalese-to-simplese
```

#### 2. Set Up Ollama Models
```bash
# Install Ollama from https://ollama.ai/

# Pull required models
ollama pull gpt-oss:cloud
ollama pull nomic-embed-text

# Verify models are available
ollama list
```

#### 3. Set Up Elasticsearch
```bash
# Option A: Using Docker
docker run -d \
  --name elasticsearch \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:8.11.0

# Option B: Using Docker Compose (included)
docker-compose up -d elasticsearch

# Verify Elasticsearch is running
curl http://localhost:9200
```

#### 4. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your settings

# Run the backend
uvicorn main:app --reload --port 8000
```

**Note:** You could also use uv to manage dependencies more efficiently

Backend will be available at: http://localhost:8000

API Documentation: http://localhost:8000/docs

#### 5. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Configure environment variables
cp .env.example .env
# Edit .env to point to your backend

# Run the development server
npm run dev
```

Frontend will be available at: http://localhost:5173

---

## 📁 Project Structure

```
legalese-to-simplese/
├── backend/                    # FastAPI backend
│   ├── main.py                # Application entry point
│   ├── routers/               # API route handlers
│   │   ├── upload.py          # Document upload endpoints
│   │   ├── qa.py              # Q&A endpoints
│   │   └── health.py          # Health check endpoints
│   ├── services/              # Business logic layer
│   │   ├── UploadService.py   # Document processing
│   │   ├── qa_service.py      # Question answering
│   │   ├── llm_service.py     # LLM interactions
│   │   ├── elastic_search_service.py  # Elasticsearch operations
│   │   └── logging/           # Structured logging
│   ├── clients/               # External service clients
│   │   ├── ollama.py          # Ollama LLM client
│   │   └── aws_client.py      # AWS services (optional)
│   ├── utils/                 # Utility functions
│   │   └── helper.py          # PDF processing, text extraction
│   ├── DTO/                   # Data transfer objects
│   │   └── DTO.py             # Request/response models
│   ├── tests/                 # Test suite
│   └── requirements.txt       # Python dependencies
│
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── pages/            # Page components
│   │   │   ├── Home/         # Landing page
│   │   │   ├── Upload/       # Document upload page
│   │   │   └── Analysis/     # Analysis results page
│   │   ├── components/       # Reusable components
│   │   │   └── CustomLoadingOverlay/
│   │   ├── contexts/         # React contexts
│   │   │   ├── AnalysisContext.jsx
│   │   │   └── AnalysisProvider.jsx
│   │   ├── assets/           # Static assets
│   │   └── main.jsx          # Application entry point
│   ├── public/               # Public assets
│   ├── .env.example          # Environment variables template
│   └── package.json          # Node dependencies
│
├── docker-compose.yaml       # Docker services configuration
├── architecture-diagram.png  # System architecture diagram
├── INTEGRATION_TASKLIST.md  # Development roadmap
└── README.md                 # This file
```

---

## 🔧 Configuration

### Backend Environment Variables

Create `backend/.env`:

```env
# Elasticsearch Configuration
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_API_KEY=  # Optional for local development

# Application Configuration
LOG_LEVEL=INFO

# AWS Configuration (Optional - for AWS services)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
```

### Frontend Environment Variables

Create `frontend/.env`:

```env
# Backend API Configuration
VITE_API_BASE_URL=http://localhost:8000

# API Endpoints (relative to base URL)
VITE_UPLOAD_ENDPOINT=/api/documents/upload
VITE_QA_ENDPOINT=/api/qa/ask
VITE_HEALTH_ENDPOINT=/api/health
```

---

## 📡 API Endpoints

### Document Management

#### Upload Document
```http
POST /api/documents/upload
Content-Type: multipart/form-data

Parameters:
  - document: File (PDF, DOC, DOCX, TXT)

Response:
{
  "success": true,
  "document_id": "uuid",
  "filename": "contract.pdf",
  "document_analysis": {
    "Document_Type": "Rental Agreement",
    "Main_Purpose": "...",
    "Key_Highlights": [...],
    "Risk_Assessment": {...},
    "Key_Terms": [...],
    "Suggested_Questions": [...]
  },
  "extracted_text": "...",
  "metadata": {...}
}
```

### Question & Answer

#### Ask Question
```http
POST /api/qa/ask
Content-Type: application/json

Body:
{
  "question": "What happens if I pay rent late?",
  "context": "Full document text..."
}

Response:
{
  "question": "What happens if I pay rent late?",
  "answer": "According to the contract, late payments...",
  "status": "success"
}
```

### Health Check

#### Service Health
```http
GET /api/health

Response:
{
  "service": "legalese-to-simplese",
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

---

## 🧪 Testing

### Backend Tests
```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_upload.py -v
```

### Frontend Tests
```bash
cd frontend

# Run tests (when implemented)
npm test

# Run with coverage
npm test -- --coverage
```

---

## 🎨 User Interface

### Home Page
- Hero section with value proposition
- Feature highlights
- How it works section
- Call-to-action buttons

### Upload Page
- Drag-and-drop file upload
- Paste text option
- File type validation
- Real-time processing status
- Security badges

### Analysis Page
- **Summary Tab**: Document overview and risk score
- **Risk Assessment Tab**: Categorized risks with severity levels
- **Key Terms Tab**: Legal terminology glossary
- **Q&A Tab**: Interactive chat interface

---

## 🔒 Security & Privacy

- **No Data Persistence**: Documents are processed in-memory (optional S3 backup)
- **Local LLM**: Uses Ollama for on-premise AI processing
- **CORS Protection**: Configured for specific origins
- **File Validation**: Type and size checks before processing
- **Error Handling**: Sanitized error messages to prevent information leakage

---

## 🚧 Development Roadmap

### ✅ Completed
- [x] Document upload and text extraction
- [x] LLM-based document analysis
- [x] Risk assessment and categorization
- [x] Interactive Q&A with context retrieval
- [x] Elasticsearch integration for semantic search
- [x] Frontend-backend integration
- [x] Real-time loading states and error handling

### 🔄 In Progress
- [ ] Centralized API service layer (frontend)
- [ ] Enhanced error handling and retry mechanisms
- [ ] User authentication and session management

### 📋 Planned
- [ ] Document comparison feature
- [ ] Export analysis reports (PDF, DOCX)
- [ ] Multi-language support
- [ ] Conversation history and saved analyses
- [ ] Advanced analytics dashboard
- [ ] Mobile responsive improvements
- [ ] Batch document processing
- [ ] Custom risk threshold configuration

See [INTEGRATION_TASKLIST.md](./INTEGRATION_TASKLIST.md) for detailed development tasks.

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Guidelines
- Follow existing code style and conventions
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

---

## 🐛 Troubleshooting

### Common Issues

**Backend won't start**
```bash
# Check if port 8000 is already in use
lsof -i :8000

# Verify Python version
python --version  # Should be 3.12+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Frontend can't connect to backend**
```bash
# Verify backend is running
curl http://localhost:8000/api/health

# Check CORS configuration in backend/main.py
# Ensure frontend URL is in allow_origins

# Verify .env file exists and has correct API URL
cat frontend/.env
```

**Ollama models not found**
```bash
# List installed models
ollama list

# Pull missing models
ollama pull gpt-oss:cloud
ollama pull nomic-embed-text

# Verify Ollama is running
curl http://localhost:11434/api/tags
```

**Elasticsearch connection failed**
```bash
# Check if Elasticsearch is running
curl http://localhost:9200

# Restart Elasticsearch
docker restart elasticsearch

# Check logs
docker logs elasticsearch
```

---

## 📚 Documentation

- [Backend README](./backend/README.md) - Detailed backend documentation
- [Frontend README](./frontend/README.md) - Frontend setup and structure
- [Integration Tasklist](./INTEGRATION_TASKLIST.md) - Development tasks and status
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (when running)

---

## 🛠️ Tech Stack

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **Context API** - State management
- **CSS3** - Styling with animations

### Backend
- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation
- **LangChain** - LLM orchestration
- **Ollama** - Local LLM runtime
- **PyPDF2** - PDF text extraction

### Infrastructure
- **Elasticsearch** - Vector search and document storage
- **Docker** - Containerization
- **Uvicorn** - ASGI server
- **S3** (optional) - Document storage

---

## 🙏 Acknowledgments

- **Ollama** - For providing excellent local LLM runtime
- **FastAPI** - For the amazing Python web framework
- **Elasticsearch** - For powerful search capabilities
- **React Team** - For the robust frontend framework
- **LangChain** - For LLM orchestration tools

---

## ⭐ Star History

If you find this project helpful, please consider giving it a star! ⭐

---

<div align="center">

**Made with ❤️ for everyone who's ever been confused by legal documents**

[Report Bug](https://github.com/Gauravpadam/legalese-to-simplese/issues)

</div>

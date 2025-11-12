# Legalese to Simplese - Frontend

React-based frontend for the Legalese to Simplese legal document analysis platform.

## Setup

### Prerequisites
- Node.js 18+ and npm
- Backend API running (see `../backend/README.md`)

### Installation

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables:
```bash
cp .env.example .env
```

3. Update `.env` with your backend API URL:
```env
VITE_API_BASE_URL=http://localhost:8000
```

### Development

Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build

Create a production build:
```bash
npm run build
```

Preview the production build:
```bash
npm run preview
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API base URL | `http://localhost:8000` |
| `VITE_UPLOAD_ENDPOINT` | Document upload endpoint | `/api/documents/upload` |
| `VITE_QA_ENDPOINT` | Q&A endpoint | `/api/qa/ask` |
| `VITE_HEALTH_ENDPOINT` | Health check endpoint | `/api/health` |

## Project Structure

```
frontend/
├── src/
│   ├── assets/          # Static assets (images, etc.)
│   ├── components/      # Reusable components
│   ├── contexts/        # React contexts (AnalysisContext)
│   ├── pages/           # Page components
│   │   ├── Home/        # Landing page
│   │   ├── Upload/      # Document upload page
│   │   └── Analysis/    # Analysis results page
│   ├── services/        # API service layer (to be implemented)
│   ├── App.jsx          # Root component
│   └── main.jsx         # Entry point
├── .env.example         # Environment variables template
└── package.json         # Dependencies
```

## Features

- **Document Upload**: Upload PDF, DOC, DOCX, or TXT files
- **Text Paste**: Paste contract text directly
- **AI Analysis**: Get structured analysis with risk assessment
- **Interactive Q&A**: Ask questions about your contract
- **Risk Visualization**: Visual risk scoring and categorization

## API Integration

The frontend communicates with the backend API for:
- Document upload and analysis
- Interactive Q&A with AI
- Health checks

See `INTEGRATION_TASKLIST.md` for integration status and tasks.

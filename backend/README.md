# Backend (FastAPI)

FastAPI backend skeleton for the Legalese to Simplese project.

## Features
- FastAPI app with CORS
- Modular routers (`routers/`)
- Services layer (`services/`)
- **Document upload and processing** (PDF, DOC/DOCX, TXT → image conversion → AWS Bedrock text extraction)
- **Comprehensive logging service** with structured logging, colored console output, and file rotation
- Utilities (`utils/` with backward-compatible logger and document processing helpers)
- Health check endpoint
- Basic test scaffold with `pytest`

## Structure
```
backend/
  main.py
  routers/
    health.py
    upload.py
  services/
    health_service.py
    logging/
      __init__.py
      logging_service.py
  utils/
    __init__.py
    logger.py
    helper.py
  tests/
    test_health.py
    test_upload.py
  docs/
    logging.md
  requirements.txt
```

## Setup & Run
```bash
# (Optional) create venv
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

# Run dev server
uvicorn main:app --reload --port 8000
```
Visit: http://localhost:8000/api/health

Root endpoint: http://localhost:8000/

API Documentation: http://localhost:8000/docs

## API Endpoints

### Upload Document Processing
- `POST /api/upload/process-document`: Upload and process documents (PDF, DOC/DOCX, TXT)
- `GET /api/upload/supported-formats`: Get supported file formats and limits

### Health Check
- `GET /api/health/`: Application health status

## Testing
```bash
pytest -q
```

## Configuration
The application uses a comprehensive logging service. See `docs/logging.md` for detailed usage.

Basic logging is configured automatically on startup with colored console output for development.

### AWS Configuration
For PDF image-to-text conversion, you'll need AWS credentials configured:
```bash
# Set AWS credentials (one of these methods):
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-west-2

# Or configure using AWS CLI
aws configure

# Or use IAM roles if running on EC2
```

## Next Steps (suggested)
- Add domain-specific routers (e.g. documents, translate)
- Add exception handlers & validation error customization
- Integrate persistence (PostgreSQL + SQLModel / SQLAlchemy)
- Authentication & rate limiting
- Observability (metrics, tracing)
```

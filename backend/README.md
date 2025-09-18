# Backend (FastAPI)

FastAPI backend skeleton for the Legalese to Simplese project.

## Features
- FastAPI app with CORS
- Modular routers (`routers/`)
- Services layer (`services/`)
- **Comprehensive logging service** with structured logging, colored console output, and file rotation
- Utilities (`utils/` with backward-compatible logger)
- Health check endpoint
- Basic test scaffold with `pytest`

## Structure
```
backend/
  main.py
  routers/
    health.py
  services/
    health_service.py
    logging/
      __init__.py
      logging_service.py
  utils/
    __init__.py
    logger.py
  tests/
    test_health.py
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

## Testing
```bash
pytest -q
```

## Configuration
The application uses a comprehensive logging service. See `docs/logging.md` for detailed usage.

Basic logging is configured automatically on startup with colored console output for development.

## Next Steps (suggested)
- Add domain-specific routers (e.g. documents, translate)
- Add exception handlers & validation error customization
- Integrate persistence (PostgreSQL + SQLModel / SQLAlchemy)
- Authentication & rate limiting
- Observability (metrics, tracing)
```

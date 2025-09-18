# Backend (FastAPI)

FastAPI backend skeleton for the Legalese to Simplese project.

## Features
- FastAPI app with CORS
- Modular routers (`routers/`)
- Services layer (`services/`)
- Utilities (`utils/` with logger)
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
  utils/
    __init__.py
    logger.py
  tests/
    test_health.py (created after first test run)
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
Currently static values are embedded in `services/health_service.py` for simplicity. Introduce a settings module later if dynamic configuration is needed.

## Next Steps (suggested)
- Add domain-specific routers (e.g. documents, translate)
- Add exception handlers & validation error customization
- Integrate persistence (PostgreSQL + SQLModel / SQLAlchemy)
- Authentication & rate limiting
- Observability (metrics, tracing)
```

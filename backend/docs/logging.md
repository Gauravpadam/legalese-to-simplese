# Logging Service

The backend includes a comprehensive logging service that provides structured logging, colored console output, file rotation, and JSON formatting capabilities.

## Features

- **Structured Logging**: JSON format support for production environments
- **Colored Console Output**: Better readability during development
- **File Rotation**: Automatic log file rotation with size limits
- **Multiple Loggers**: Named loggers for different modules
- **Context Logging**: Add custom fields to log entries
- **Backward Compatibility**: Works with existing logger usage

## Quick Start

### Basic Usage

```python
from services.logging import get_logger

logger = get_logger("my_module")
logger.info("This is an info message")
logger.error("This is an error message")
logger.debug("This is a debug message")
```

### Configuration

Configure logging in your `main.py` or application startup:

```python
from services.logging import configure_logging

# Development configuration
configure_logging(
    level="INFO",
    enable_console_colors=True,
    enable_json_logging=False
)

# Production configuration
configure_logging(
    level="WARNING",
    log_file="logs/app.log",
    enable_json_logging=True,
    enable_console_colors=False,
    max_file_size=50 * 1024 * 1024,  # 50MB
    backup_count=10
)
```

### Context Logging

Add custom context to your log entries:

```python
from services.logging import log_with_context

log_with_context(
    "api_router",
    "info",
    "User action completed",
    user_id=123,
    action="document_upload",
    duration_ms=1500
)
```

### Backward Compatibility

Existing code using `utils.logger` will continue to work:

```python
from utils.logger import logger

logger.info("This still works!")
```

## Log Levels

- `DEBUG`: Detailed information for debugging
- `INFO`: General information about application flow
- `WARNING`: Warning messages for potential issues
- `ERROR`: Error messages for actual problems
- `CRITICAL`: Critical errors that may cause application failure

## Output Formats

### Console (Development)
```
2025-09-18 12:34:56 | INFO | main | Starting Legalese to Simplese API...
2025-09-18 12:34:56 | INFO | health_service | Health check completed successfully
```

### JSON (Production)
```json
{
  "timestamp": "2025-09-18T12:34:56.123456Z",
  "level": "INFO",
  "logger": "main",
  "message": "Starting Legalese to Simplese API...",
  "module": "main",
  "function": "lifespan",
  "line": 15
}
```

## Best Practices

1. **Use named loggers**: `get_logger("module_name")` instead of root logger
2. **Log at appropriate levels**: Use DEBUG for detailed info, INFO for general flow
3. **Include context**: Add relevant fields when logging user actions or API calls
4. **Avoid logging sensitive data**: Don't log passwords, tokens, or PII
5. **Use structured logging in production**: Enable JSON format for better parsing

## Integration Examples

### FastAPI Middleware

```python
from fastapi import Request
import time

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    logger = get_logger("http")
    logger.info(f"Request started: {request.method} {request.url}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    log_with_context(
        "http",
        "info",
        "Request completed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        duration_ms=round(process_time * 1000, 2)
    )
    
    return response
```

### Service Layer

```python
from services.logging import get_logger

class DocumentService:
    def __init__(self):
        self.logger = get_logger("document_service")
    
    def process_document(self, doc_id: str):
        self.logger.info(f"Processing document {doc_id}")
        try:
            # Process document
            self.logger.info(f"Document {doc_id} processed successfully")
        except Exception as e:
            self.logger.error(f"Failed to process document {doc_id}: {e}")
            raise
```
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.health import router as health_router
from services.logging import configure_logging, get_logger

# Configure logging on startup
configure_logging(
    level="INFO",
    enable_console_colors=True,
    enable_json_logging=False
)

logger = get_logger("main")

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup
#     logger.info("Starting Legalese to Simplese API...")
#     yield
#     # Shutdown
#     logger.info("Shutting down Legalese to Simplese API...")

app = FastAPI(
    title="Legalese to Simplese API", 
    version="0.1.0",
)

# CORS configuration (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix="/api")

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"status": "ok", "message": "Backend is running"}

from datetime import datetime
from services.logging import get_logger

APP_NAME = "Legalese to Simplese API"
ENVIRONMENT = "development"

logger = get_logger("health_service")


def get_health_status() -> dict:
    logger.debug("Health status requested")
    
    health_data = {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "app": APP_NAME,
        "environment": ENVIRONMENT,
    }
    
    logger.info("Health check completed successfully")
    return health_data

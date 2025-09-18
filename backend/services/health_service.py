from datetime import datetime

APP_NAME = "Legalese to Simplese API"
ENVIRONMENT = "development"


def get_health_status() -> dict:
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "app": APP_NAME,
        "environment": ENVIRONMENT,
    }

"""
Legacy logger module - now using the new logging service.
This module is kept for backward compatibility.
"""

from services.logging import get_logger, configure_logging
import logging
from typing import Optional

# Backward compatibility wrapper
class LoggerFactory:
    _configured = False

    @classmethod
    def configure(cls, level: int = logging.INFO):
        if cls._configured:
            return
        # Use new logging service with colored console output
        level_name = logging.getLevelName(level)
        configure_logging(
            level=level_name,
            enable_console_colors=True,
            enable_json_logging=False
        )
        cls._configured = True

    @staticmethod
    def get_logger(name: Optional[str] = None) -> logging.Logger:
        LoggerFactory.configure()
        return get_logger(name if name else "backend")

# Default logger instance for backward compatibility
logger = LoggerFactory.get_logger("backend")

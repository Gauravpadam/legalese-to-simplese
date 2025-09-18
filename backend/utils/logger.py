import logging
import sys
from typing import Optional

_LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

class LoggerFactory:
    _configured = False

    @classmethod
    def configure(cls, level: int = logging.INFO):
        if cls._configured:
            return
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(_LOG_FORMAT))
        root = logging.getLogger()
        root.setLevel(level)
        root.addHandler(handler)
        cls._configured = True

    @staticmethod
    def get_logger(name: Optional[str] = None) -> logging.Logger:
        LoggerFactory.configure()
        return logging.getLogger(name if name else __name__)

logger = LoggerFactory.get_logger("backend")

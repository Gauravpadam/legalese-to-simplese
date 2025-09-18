"""
Logging service module for structured logging across the application.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import json
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)
            
        return json.dumps(log_entry, ensure_ascii=False)


class ColoredConsoleFormatter(logging.Formatter):
    """Colored console formatter for better readability in development."""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        return formatter.format(record)


class LoggingService:
    """Centralized logging service for the application."""
    
    _instance: Optional['LoggingService'] = None
    _initialized = False
    
    def __new__(cls) -> 'LoggingService':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.loggers: Dict[str, logging.Logger] = {}
            self._initialized = True
    
    def configure_logging(
        self,
        level: str = "INFO",
        log_file: Optional[str] = None,
        enable_json_logging: bool = False,
        enable_console_colors: bool = True,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5
    ) -> None:
        """Configure global logging settings."""
        
        # Clear existing handlers
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Set root level
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        root_logger.setLevel(numeric_level)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        if enable_console_colors and not enable_json_logging:
            console_formatter = ColoredConsoleFormatter()
        elif enable_json_logging:
            console_formatter = JSONFormatter()
        else:
            console_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(numeric_level)
        root_logger.addHandler(console_handler)
        
        # File handler (if specified)
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_file_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            
            if enable_json_logging:
                file_formatter = JSONFormatter()
            else:
                file_formatter = logging.Formatter(
                    '%(asctime)s | %(levelname)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
            
            file_handler.setFormatter(file_formatter)
            file_handler.setLevel(numeric_level)
            root_logger.addHandler(file_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get or create a logger with the given name."""
        if name not in self.loggers:
            logger = logging.getLogger(name)
            self.loggers[name] = logger
        return self.loggers[name]
    
    def log_with_context(
        self,
        logger_name: str,
        level: str,
        message: str,
        **context
    ) -> None:
        """Log a message with additional context fields."""
        logger = self.get_logger(logger_name)
        
        # Create a custom LogRecord with extra fields
        record = logger.makeRecord(
            logger.name,
            getattr(logging, level.upper()),
            "",
            0,
            message,
            (),
            None
        )
        record.extra_fields = context
        
        logger.handle(record)


# Global instance
logging_service = LoggingService()


def get_logger(name: str) -> logging.Logger:
    """Convenience function to get a logger."""
    return logging_service.get_logger(name)


def configure_logging(**kwargs) -> None:
    """Convenience function to configure logging."""
    logging_service.configure_logging(**kwargs)


def log_with_context(logger_name: str, level: str, message: str, **context) -> None:
    """Convenience function to log with context."""
    logging_service.log_with_context(logger_name, level, message, **context)
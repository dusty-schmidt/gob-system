# /home/ds/sambashare/GOB/lib/logger.py
"""
Universal Logger for the GOB Framework.

Any component can import this module to get a standardized, 
cyberpunk-themed logger that outputs to both the console and
a dedicated log file in the central /logs directory.
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Store initialized loggers to prevent duplicate handlers
_loggers = {}

class CyberpunkFormatter(logging.Formatter):
    """Custom formatter for a consistent, themed output."""
    
    LOG_FORMAT = "[%(asctime)s] :: %(name)s :: [%(levelname)s] :: %(message)s"
    
    def format(self, record):
        formatter = logging.Formatter(self.LOG_FORMAT, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)

def setup_logger(name: str, level=logging.DEBUG):
    """
    Initializes and returns a logger instance.

    Args:
        name (str): The name for the logger (e.g., 'grid-overwatch-bridge', 'gob-monitor').
                    This name will appear in the log output.
        level: The logging level (e.g., logging.DEBUG, logging.INFO).

    Returns:
        A configured logger instance.
    """
    if name in _loggers:
        return _loggers[name]

    # Define the central logs directory relative to this file's parent (the lib dir)
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"{name}.log"

    # Create a logger instance
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False  # Prevent duplicate logs in parent handlers

    # Create a rotating file handler for persistent storage
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=5  # 5MB per file
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(CyberpunkFormatter())

    # Create a stream handler for real-time console output
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO) # Console logs are less verbose
    stream_handler.setFormatter(CyberpunkFormatter())

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    _loggers[name] = logger
    logger.info(f"Logger '{name}' initialized. Logging to {log_file}")
    return logger

# /home/ds/sambashare/GOB/GOB-V1.0/python/helpers/logger.py
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

_logger = None

def setup_logger():
    """
    Sets up a centralized logger for the GOB application.
    """
    global _logger
    if _logger is not None:
        return _logger

    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "gob_backend.log"

    # Create a logger instance
    logger = logging.getLogger("gob_backend")
    logger.setLevel(logging.DEBUG)

    # Create a formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)'
    )

    # Create a rotating file handler
    # Rotates when the log file reaches 2MB, keeps 5 backup logs.
    file_handler = RotatingFileHandler(
        log_file, maxBytes=2 * 1024 * 1024, backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Create a stream handler to output to the console
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    _logger = logger
    return _logger

def get_logger():
    """
    Returns the singleton logger instance.
    Initializes it if it hasn't been already.
    """
    return setup_logger()

"""
Logging utility for Raspberry Pi Sense HAT Monitor
"""
import logging
import os
from pathlib import Path

# Import config - handle both relative and absolute imports
try:
    from config import Config
except ImportError:
    from logger.config import Config


def setup_logger(name: str = "sense_logger") -> logging.Logger:
    """
    Setup logger with file and console handlers
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, Config.LOG_LEVEL, logging.INFO))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler (always enabled)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if LOG_DIR is configured)
    if Config.LOG_DIR:
        try:
            # Create log directory if it doesn't exist
            log_dir = Path(Config.LOG_DIR)
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # Create file handler
            log_file = log_dir / Config.LOG_FILE
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
            logger.info(f"Logging to file: {log_file}")
        except (PermissionError, OSError) as e:
            logger.warning(f"Could not create log file: {e}. Logging to console only.")
    
    return logger


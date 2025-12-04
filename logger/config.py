"""
Configuration management for Raspberry Pi Sense HAT Monitor
"""
import os


class Config:
    """Application configuration from environment variables"""
    
    # PostgreSQL configuration
    POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")
    POSTGRES_DB = os.environ.get("POSTGRES_DB", "sensehat")
    POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "postgres")
    
    # Logger configuration
    SAMPLE_INTERVAL = float(os.environ.get("SAMPLE_INTERVAL", "5"))
    
    # Device identifier (optional, for multi-Pi setups)
    DEVICE_ID = os.environ.get("DEVICE_ID", None)
    
    # Logging configuration
    LOG_DIR = os.environ.get("LOG_DIR", "/var/log/raspi-sense-monitor")
    LOG_FILE = os.environ.get("LOG_FILE", "sense-logger.log")
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()


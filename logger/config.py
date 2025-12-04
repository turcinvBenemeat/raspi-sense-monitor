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
    
    # Sensor configuration
    ENABLE_SENSEHAT = os.environ.get("ENABLE_SENSEHAT", "auto").lower() in ("true", "1", "yes", "auto")
    ENABLE_SYSTEM_METRICS = os.environ.get("ENABLE_SYSTEM_METRICS", "true").lower() in ("true", "1", "yes")
    
    # Device identifier (optional, for multi-Pi setups)
    DEVICE_ID = os.environ.get("DEVICE_ID", None)  # e.g., "raspberry-pi-1", "raspberry-pi-2"


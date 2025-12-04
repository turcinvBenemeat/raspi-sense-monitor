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


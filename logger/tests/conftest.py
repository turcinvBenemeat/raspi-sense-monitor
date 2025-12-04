"""
Pytest configuration and fixtures
"""
import pytest
import os
from unittest.mock import Mock, MagicMock, patch


@pytest.fixture
def mock_env_vars():
    """Fixture to set test environment variables"""
    env_vars = {
        "POSTGRES_HOST": "test-host",
        "POSTGRES_PORT": "5432",
        "POSTGRES_DB": "test_db",
        "POSTGRES_USER": "test_user",
        "POSTGRES_PASSWORD": "test_password",
        "SAMPLE_INTERVAL": "10",
        "ENABLE_SENSEHAT": "true",
        "ENABLE_SYSTEM_METRICS": "true",
        "DEVICE_ID": "test-device-1",
    }
    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture
def mock_sense_hat():
    """Fixture to mock Sense HAT"""
    mock_sense = MagicMock()
    mock_sense.get_temperature.return_value = 25.5
    mock_sense.get_humidity.return_value = 60.0
    mock_sense.get_pressure.return_value = 1013.25
    mock_sense.get_orientation.return_value = {"pitch": 0.0, "roll": 0.0, "yaw": 0.0}
    mock_sense.get_accelerometer_raw.return_value = {"x": 0.0, "y": 0.0, "z": 1.0}
    mock_sense.get_gyroscope_raw.return_value = {"x": 0.0, "y": 0.0, "z": 0.0}
    mock_sense.get_compass_raw.return_value = {"x": 0.0, "y": 0.0, "z": 0.0}
    return mock_sense


@pytest.fixture
def mock_psutil():
    """Fixture to mock psutil"""
    mock_mem = MagicMock()
    mock_mem.total = 4 * 1024**3  # 4 GB
    mock_mem.used = 2 * 1024**3   # 2 GB
    mock_mem.available = 2 * 1024**3  # 2 GB
    mock_mem.percent = 50.0
    
    mock_disk = MagicMock()
    mock_disk.total = 32 * 1024**3  # 32 GB
    mock_disk.used = 16 * 1024**3   # 16 GB
    mock_disk.free = 16 * 1024**3   # 16 GB
    mock_disk.percent = 50.0
    
    mock_cpu_freq = MagicMock()
    mock_cpu_freq.current = 1500.0
    
    with patch("psutil.cpu_percent", return_value=25.0), \
         patch("psutil.cpu_count", return_value=4), \
         patch("psutil.cpu_freq", return_value=mock_cpu_freq), \
         patch("psutil.virtual_memory", return_value=mock_mem), \
         patch("psutil.disk_usage", return_value=mock_disk), \
         patch("os.getloadavg", return_value=(0.5, 0.6, 0.7)):
        yield


@pytest.fixture
def mock_db_connection():
    """Fixture to mock PostgreSQL connection"""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    mock_conn.closed = False
    return mock_conn, mock_cur


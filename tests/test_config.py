"""
Tests for configuration management
"""
import pytest
import os
import sys
from unittest.mock import patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestConfig:
    """Tests for Config class"""
    
    def test_default_values(self):
        """Test default configuration values"""
        with patch.dict(os.environ, {}, clear=True):
            # Reload config module to get defaults
            import importlib
            import config
            importlib.reload(config)
            
            assert config.Config.POSTGRES_HOST == "localhost"
            assert config.Config.POSTGRES_PORT == "5432"
            assert config.Config.POSTGRES_DB == "sensehat"
            assert config.Config.SAMPLE_INTERVAL == 5.0
    
    def test_env_vars_override(self, mock_env_vars):
        """Test environment variables override defaults"""
        import importlib
        import config
        importlib.reload(config)
        
        assert config.Config.POSTGRES_HOST == "test-host"
        assert config.Config.POSTGRES_DB == "test_db"
        assert config.Config.SAMPLE_INTERVAL == 10.0
        assert config.Config.DEVICE_ID == "test-device-1"
    
    def test_enable_sensehat_values(self):
        """Test ENABLE_SENSEHAT accepts various values"""
        test_cases = [
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("1", True),
            ("yes", True),
            ("auto", True),
            ("false", False),
            ("False", False),
            ("0", False),
            ("no", False),
        ]
        
        for env_value, expected in test_cases:
            with patch.dict(os.environ, {"ENABLE_SENSEHAT": env_value}):
                import importlib
                import config
                importlib.reload(config)
                assert config.Config.ENABLE_SENSEHAT == expected, f"Failed for {env_value}"
    
    def test_enable_system_metrics_values(self):
        """Test ENABLE_SYSTEM_METRICS accepts various values"""
        test_cases = [
            ("true", True),
            ("1", True),
            ("yes", True),
            ("false", False),
            ("0", False),
        ]
        
        for env_value, expected in test_cases:
            with patch.dict(os.environ, {"ENABLE_SYSTEM_METRICS": env_value}):
                import importlib
                import config
                importlib.reload(config)
                assert config.Config.ENABLE_SYSTEM_METRICS == expected


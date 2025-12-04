"""
Tests for sensor readers
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logger.sensors import SenseHatReader, SystemReader
from logger.models import SenseHatData, RaspberryPiData


class TestSenseHatReader:
    """Tests for SenseHatReader"""
    
    @patch('sensors.sensehat.SenseHat')
    def test_sensehat_available(self, mock_sensehat_class, mock_sense_hat):
        """Test Sense HAT reader when available"""
        mock_sensehat_class.return_value = mock_sense_hat
        
        reader = SenseHatReader()
        
        assert reader.is_available() is True
        assert reader.sense is not None
    
    @patch('sensors.sensehat.SenseHat')
    def test_sensehat_not_available_import_error(self, mock_sensehat_class):
        """Test Sense HAT reader when not available (ImportError)"""
        mock_sensehat_class.side_effect = ImportError("No module named 'sense_hat'")
        
        reader = SenseHatReader()
        
        assert reader.is_available() is False
        assert reader.sense is None
    
    @patch('sensors.sensehat.SenseHat')
    def test_sensehat_not_available_os_error(self, mock_sensehat_class):
        """Test Sense HAT reader when not available (OSError)"""
        mock_sensehat_class.side_effect = OSError("I2C device not found")
        
        reader = SenseHatReader()
        
        assert reader.is_available() is False
    
    @patch('sensors.sensehat.SenseHat')
    def test_read_sensehat_data(self, mock_sensehat_class, mock_sense_hat):
        """Test reading Sense HAT data"""
        mock_sensehat_class.return_value = mock_sense_hat
        
        reader = SenseHatReader()
        data = reader.read()
        
        assert isinstance(data, SenseHatData)
        assert data.temperature == 25.5
        assert data.humidity == 60.0
        assert data.pressure == 1013.25
    
    @patch('sensors.sensehat.SenseHat')
    def test_read_when_not_available(self, mock_sensehat_class):
        """Test read raises error when Sense HAT not available"""
        mock_sensehat_class.side_effect = OSError("Device not found")
        
        reader = SenseHatReader()
        
        with pytest.raises(RuntimeError, match="Sense HAT is not available"):
            reader.read()


class TestSystemReader:
    """Tests for SystemReader"""
    
    @patch('os.getloadavg')
    @patch('psutil.disk_usage')
    @patch('psutil.virtual_memory')
    @patch('psutil.cpu_freq')
    @patch('psutil.cpu_count')
    @patch('psutil.cpu_percent')
    @patch('builtins.open')
    def test_read_system_data(self, mock_open, mock_cpu_percent, mock_cpu_count,
                              mock_cpu_freq, mock_mem, mock_disk, mock_loadavg):
        """Test reading system metrics"""
        # Mock CPU temperature file
        mock_file = MagicMock()
        mock_file.read.return_value = "45000\n"  # 45°C in millidegrees
        mock_file.__enter__.return_value = mock_file
        mock_open.return_value = mock_file
        
        # Mock psutil
        mock_cpu_percent.return_value = 25.0
        mock_cpu_count.return_value = 4
        mock_cpu_freq_obj = MagicMock()
        mock_cpu_freq_obj.current = 1500.0
        mock_cpu_freq.return_value = mock_cpu_freq_obj
        
        mock_mem_obj = MagicMock()
        mock_mem_obj.total = 4 * 1024**3
        mock_mem_obj.used = 2 * 1024**3
        mock_mem_obj.available = 2 * 1024**3
        mock_mem_obj.percent = 50.0
        mock_mem.return_value = mock_mem_obj
        
        mock_disk_obj = MagicMock()
        mock_disk_obj.total = 32 * 1024**3
        mock_disk_obj.used = 16 * 1024**3
        mock_disk_obj.free = 16 * 1024**3
        mock_disk_obj.percent = 50.0
        mock_disk.return_value = mock_disk_obj
        
        mock_loadavg.return_value = (0.5, 0.6, 0.7)
        
        reader = SystemReader()
        data = reader.read()
        
        assert isinstance(data, RaspberryPiData)
        assert data.cpu_temp == 45.0
        assert data.cpu_percent == 25.0
        assert data.cpu_count == 4
        assert data.mem_percent == 50.0
        assert data.load_avg_1min == 0.5
    
    @patch('os.getloadavg')
    @patch('psutil.disk_usage')
    @patch('psutil.virtual_memory')
    @patch('psutil.cpu_freq')
    @patch('psutil.cpu_count')
    @patch('psutil.cpu_percent')
    @patch('builtins.open')
    def test_read_system_data_no_cpu_temp(self, mock_open, mock_cpu_percent,
                                         mock_cpu_count, mock_cpu_freq,
                                         mock_mem, mock_disk, mock_loadavg):
        """Test reading system data when CPU temp file doesn't exist"""
        # Mock file not found
        mock_open.side_effect = FileNotFoundError
        
        # Mock psutil
        mock_cpu_percent.return_value = 25.0
        mock_cpu_count.return_value = 4
        mock_cpu_freq.return_value = None  # No CPU freq available
        
        mock_mem_obj = MagicMock()
        mock_mem_obj.total = 4 * 1024**3
        mock_mem_obj.used = 2 * 1024**3
        mock_mem_obj.available = 2 * 1024**3
        mock_mem_obj.percent = 50.0
        mock_mem.return_value = mock_mem_obj
        
        mock_disk_obj = MagicMock()
        mock_disk_obj.total = 32 * 1024**3
        mock_disk_obj.used = 16 * 1024**3
        mock_disk_obj.free = 16 * 1024**3
        mock_disk_obj.percent = 50.0
        mock_disk.return_value = mock_disk_obj
        
        mock_loadavg.return_value = (0.5, 0.6, 0.7)
        
        reader = SystemReader()
        data = reader.read()
        
        assert data.cpu_temp is None
        assert data.cpu_freq_mhz is None


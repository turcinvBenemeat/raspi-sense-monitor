"""
Tests for data models
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models import SenseHatData, RaspberryPiData


class TestSenseHatData:
    """Tests for SenseHatData model"""
    
    def test_create_sensehat_data(self):
        """Test creating SenseHatData instance"""
        data = SenseHatData(
            temperature=25.5,
            humidity=60.0,
            pressure=1013.25,
            pitch=0.0,
            roll=0.0,
            yaw=0.0,
            accel_x=0.0,
            accel_y=0.0,
            accel_z=1.0,
            gyro_x=0.0,
            gyro_y=0.0,
            gyro_z=0.0,
            compass_x=0.0,
            compass_y=0.0,
            compass_z=0.0,
        )
        
        assert data.temperature == 25.5
        assert data.humidity == 60.0
        assert data.pressure == 1013.25
        assert data.accel_z == 1.0
    
    def test_sensehat_data_all_fields(self):
        """Test all fields are present"""
        data = SenseHatData(
            temperature=0.0, humidity=0.0, pressure=0.0,
            pitch=0.0, roll=0.0, yaw=0.0,
            accel_x=0.0, accel_y=0.0, accel_z=0.0,
            gyro_x=0.0, gyro_y=0.0, gyro_z=0.0,
            compass_x=0.0, compass_y=0.0, compass_z=0.0,
        )
        
        # Verify all 15 fields exist
        assert hasattr(data, 'temperature')
        assert hasattr(data, 'humidity')
        assert hasattr(data, 'pressure')
        assert hasattr(data, 'pitch')
        assert hasattr(data, 'roll')
        assert hasattr(data, 'yaw')
        assert hasattr(data, 'accel_x')
        assert hasattr(data, 'accel_y')
        assert hasattr(data, 'accel_z')
        assert hasattr(data, 'gyro_x')
        assert hasattr(data, 'gyro_y')
        assert hasattr(data, 'gyro_z')
        assert hasattr(data, 'compass_x')
        assert hasattr(data, 'compass_y')
        assert hasattr(data, 'compass_z')


class TestRaspberryPiData:
    """Tests for RaspberryPiData model"""
    
    def test_create_raspberry_pi_data(self):
        """Test creating RaspberryPiData instance"""
        data = RaspberryPiData(
            cpu_temp=45.0,
            cpu_percent=25.0,
            cpu_count=4,
            cpu_freq_mhz=1500.0,
            mem_total_gb=4.0,
            mem_used_gb=2.0,
            mem_available_gb=2.0,
            mem_percent=50.0,
            disk_total_gb=32.0,
            disk_used_gb=16.0,
            disk_free_gb=16.0,
            disk_percent=50.0,
            load_avg_1min=0.5,
            load_avg_5min=0.6,
            load_avg_15min=0.7,
        )
        
        assert data.cpu_temp == 45.0
        assert data.cpu_percent == 25.0
        assert data.cpu_count == 4
        assert data.mem_percent == 50.0
    
    def test_raspberry_pi_data_optional_fields(self):
        """Test optional fields can be None"""
        data = RaspberryPiData(
            cpu_temp=None,
            cpu_percent=25.0,
            cpu_count=None,
            cpu_freq_mhz=None,
            mem_total_gb=4.0,
            mem_used_gb=2.0,
            mem_available_gb=2.0,
            mem_percent=50.0,
            disk_total_gb=32.0,
            disk_used_gb=16.0,
            disk_free_gb=16.0,
            disk_percent=50.0,
            load_avg_1min=0.5,
            load_avg_5min=0.6,
            load_avg_15min=0.7,
        )
        
        assert data.cpu_temp is None
        assert data.cpu_count is None
        assert data.cpu_freq_mhz is None


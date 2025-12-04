"""
Tests for database operations
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logger.database import Database, get_database
from logger.models import SenseHatData, RaspberryPiData
from logger.config import Config


class TestDatabase:
    """Tests for Database class"""
    
    @patch('database.db.psycopg2.connect')
    def test_get_connection(self, mock_connect, mock_db_connection):
        """Test database connection"""
        mock_conn, _ = mock_db_connection
        mock_connect.return_value = mock_conn
        
        db = Database()
        conn = db.get_connection()
        
        assert conn == mock_conn
        mock_connect.assert_called_once()
    
    @patch('database.db.psycopg2.connect')
    def test_close_connection(self, mock_connect, mock_db_connection):
        """Test closing database connection"""
        mock_conn, _ = mock_db_connection
        mock_connect.return_value = mock_conn
        
        db = Database()
        db.get_connection()
        db.close()
        
        mock_conn.close.assert_called_once()
    
    @patch('database.db.psycopg2.connect')
    def test_init_database(self, mock_connect, mock_db_connection):
        """Test database initialization"""
        mock_conn, mock_cur = mock_db_connection
        mock_connect.return_value = mock_conn
        
        db = Database()
        db.init_database()
        
        # Verify tables are created
        assert mock_cur.execute.call_count >= 4  # At least 2 tables + 4 indexes
    
    @patch('database.db.psycopg2.connect')
    def test_write_sensehat_data(self, mock_connect, mock_db_connection):
        """Test writing Sense HAT data"""
        mock_conn, mock_cur = mock_db_connection
        mock_connect.return_value = mock_conn
        
        with patch.object(Config, 'DEVICE_ID', 'test-device'):
            db = Database()
            
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
            
            db.write_sensehat_data(data)
            
            mock_cur.execute.assert_called()
            mock_conn.commit.assert_called_once()
    
    @patch('database.db.psycopg2.connect')
    def test_write_raspberry_pi_data(self, mock_connect, mock_db_connection):
        """Test writing Raspberry Pi system data"""
        mock_conn, mock_cur = mock_db_connection
        mock_connect.return_value = mock_conn
        
        with patch.object(Config, 'DEVICE_ID', 'test-device'):
            db = Database()
            
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
            
            db.write_raspberry_pi_data(data)
            
            mock_cur.execute.assert_called()
            mock_conn.commit.assert_called_once()
    
    @patch('database.db.psycopg2.connect')
    def test_write_error_rollback(self, mock_connect, mock_db_connection):
        """Test rollback on write error"""
        mock_conn, mock_cur = mock_db_connection
        mock_connect.return_value = mock_conn
        mock_cur.execute.side_effect = Exception("Database error")
        
        db = Database()
        data = SenseHatData(
            temperature=25.5, humidity=60.0, pressure=1013.25,
            pitch=0.0, roll=0.0, yaw=0.0,
            accel_x=0.0, accel_y=0.0, accel_z=1.0,
            gyro_x=0.0, gyro_y=0.0, gyro_z=0.0,
            compass_x=0.0, compass_y=0.0, compass_z=0.0,
        )
        
        with pytest.raises(Exception):
            db.write_sensehat_data(data)
        
        mock_conn.rollback.assert_called_once()
    
    def test_get_database_singleton(self):
        """Test get_database returns singleton"""
        db1 = get_database()
        db2 = get_database()
        
        assert db1 is db2


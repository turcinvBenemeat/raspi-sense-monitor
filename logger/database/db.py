"""
Database module for Raspberry Pi Sense HAT Monitor
Handles PostgreSQL connection and database operations
"""
from typing import Optional
import psycopg2
from psycopg2.extensions import connection

from ..config import Config
from ..models import SenseHatData, RaspberryPiData


class Database:
    """Database connection and operations manager"""
    
    def __init__(self):
        self._connection: Optional[connection] = None
    
    def get_connection(self) -> connection:
        """Get or create database connection"""
        if self._connection is None or self._connection.closed:
            self._connection = psycopg2.connect(
                host=Config.POSTGRES_HOST,
                port=Config.POSTGRES_PORT,
                database=Config.POSTGRES_DB,
                user=Config.POSTGRES_USER,
                password=Config.POSTGRES_PASSWORD
            )
        return self._connection
    
    def close(self):
        """Close database connection"""
        if self._connection and not self._connection.closed:
            self._connection.close()
            self._connection = None
    
    def init_database(self):
        """Initialize database tables and indexes"""
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            
            # Create sensehat table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sensehat (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
                    temperature FLOAT,
                    humidity FLOAT,
                    pressure FLOAT,
                    pitch FLOAT,
                    roll FLOAT,
                    yaw FLOAT,
                    accel_x FLOAT,
                    accel_y FLOAT,
                    accel_z FLOAT,
                    gyro_x FLOAT,
                    gyro_y FLOAT,
                    gyro_z FLOAT,
                    compass_x FLOAT,
                    compass_y FLOAT,
                    compass_z FLOAT
                )
            """)
            
            # Create raspberry_pi table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS raspberry_pi (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
                    cpu_temp FLOAT,
                    cpu_percent FLOAT,
                    cpu_count INTEGER,
                    cpu_freq_mhz FLOAT,
                    mem_total_gb FLOAT,
                    mem_used_gb FLOAT,
                    mem_available_gb FLOAT,
                    mem_percent FLOAT,
                    disk_total_gb FLOAT,
                    disk_used_gb FLOAT,
                    disk_free_gb FLOAT,
                    disk_percent FLOAT,
                    load_avg_1min FLOAT,
                    load_avg_5min FLOAT,
                    load_avg_15min FLOAT
                )
            """)
            
            # Create indexes on timestamp for better query performance
            cur.execute("CREATE INDEX IF NOT EXISTS idx_sensehat_timestamp ON sensehat(timestamp)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_raspberry_pi_timestamp ON raspberry_pi(timestamp)")
            
            conn.commit()
            cur.close()
            print("Database initialized successfully", flush=True)
        except Exception as e:
            print(f"Warning: Could not initialize database: {e}", flush=True)
            print("Database will be initialized on first connection", flush=True)
    
    def write_sensehat_data(self, data: SenseHatData):
        """Write Sense HAT sensor data to database"""
        conn = self.get_connection()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                INSERT INTO sensehat (
                    timestamp, temperature, humidity, pressure,
                    pitch, roll, yaw,
                    accel_x, accel_y, accel_z,
                    gyro_x, gyro_y, gyro_z,
                    compass_x, compass_y, compass_z
                ) VALUES (
                    NOW(), %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s
                )
            """, (
                float(data.temperature),
                float(data.humidity),
                float(data.pressure),
                float(data.pitch),
                float(data.roll),
                float(data.yaw),
                float(data.accel_x),
                float(data.accel_y),
                float(data.accel_z),
                float(data.gyro_x),
                float(data.gyro_y),
                float(data.gyro_z),
                float(data.compass_x),
                float(data.compass_y),
                float(data.compass_z),
            ))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
    
    def write_raspberry_pi_data(self, data: RaspberryPiData):
        """Write Raspberry Pi system metrics to database"""
        conn = self.get_connection()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                INSERT INTO raspberry_pi (
                    timestamp, cpu_temp, cpu_percent, cpu_count, cpu_freq_mhz,
                    mem_total_gb, mem_used_gb, mem_available_gb, mem_percent,
                    disk_total_gb, disk_used_gb, disk_free_gb, disk_percent,
                    load_avg_1min, load_avg_5min, load_avg_15min
                ) VALUES (
                    NOW(), %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s
                )
            """, (
                data.cpu_temp,
                float(data.cpu_percent) if data.cpu_percent is not None else None,
                int(data.cpu_count) if data.cpu_count is not None else None,
                float(data.cpu_freq_mhz) if data.cpu_freq_mhz is not None else None,
                float(data.mem_total_gb),
                float(data.mem_used_gb),
                float(data.mem_available_gb),
                float(data.mem_percent),
                float(data.disk_total_gb),
                float(data.disk_used_gb),
                float(data.disk_free_gb),
                float(data.disk_percent),
                float(data.load_avg_1min),
                float(data.load_avg_5min),
                float(data.load_avg_15min),
            ))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()


# Global database instance
_db = Database()

# Initialize database on module import
_db.init_database()


def get_database() -> Database:
    """Get the global database instance"""
    return _db


"""
Data models for sensor and system metrics
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class SenseHatData:
    """Model for Sense HAT sensor data"""
    temperature: float
    humidity: float
    pressure: float
    pitch: float
    roll: float
    yaw: float
    accel_x: float
    accel_y: float
    accel_z: float
    gyro_x: float
    gyro_y: float
    gyro_z: float
    compass_x: float
    compass_y: float
    compass_z: float


@dataclass
class RaspberryPiData:
    """Model for Raspberry Pi system metrics"""
    cpu_temp: Optional[float]
    cpu_percent: float
    cpu_count: Optional[int]
    cpu_freq_mhz: Optional[float]
    mem_total_gb: float
    mem_used_gb: float
    mem_available_gb: float
    mem_percent: float
    disk_total_gb: float
    disk_used_gb: float
    disk_free_gb: float
    disk_percent: float
    load_avg_1min: float
    load_avg_5min: float
    load_avg_15min: float


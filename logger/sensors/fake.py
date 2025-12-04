"""
Fake sensor data generators for testing and development
Generates realistic fake data for Sense HAT and system metrics
"""
import random
import time
import math

# Import models - handle both relative and absolute imports
try:
    from models import SenseHatData, RaspberryPiData
except ImportError:
    from ..models import SenseHatData, RaspberryPiData


class FakeSenseHatReader:
    """Generates fake Sense HAT sensor data"""
    
    def __init__(self):
        self.start_time = time.time()
        self.base_temp = 20.0  # Base temperature in Celsius
        self.base_humidity = 50.0  # Base humidity in %
        self.base_pressure = 1013.25  # Base pressure in hPa
        
        # Base values for motion sensors
        self.base_pitch = 0.0
        self.base_roll = 0.0
        self.base_yaw = 0.0
        
        import logging
        logging.getLogger("sense_logger").info("Fake Sense HAT reader initialized")
    
    def is_available(self) -> bool:
        """Fake Sense HAT is always available"""
        return True
    
    def read(self) -> SenseHatData:
        """Generate fake Sense HAT sensor data with realistic variations"""
        t = time.time() - self.start_time
        
        # Temperature: varies with sine wave (simulating day/night cycle) + noise
        temp = self.base_temp + 5 * math.sin(t / 3600) + random.uniform(-1, 1)
        
        # Humidity: varies inversely with temperature + noise
        humidity = self.base_humidity - (temp - self.base_temp) * 2 + random.uniform(-3, 3)
        humidity = max(20, min(80, humidity))  # Clamp to realistic range
        
        # Pressure: slight variations + noise
        pressure = self.base_pressure + random.uniform(-5, 5)
        
        # Orientation: slow drift with small random variations
        self.base_pitch += random.uniform(-0.5, 0.5)
        self.base_roll += random.uniform(-0.5, 0.5)
        self.base_yaw += random.uniform(-1, 1)
        
        pitch = self.base_pitch + random.uniform(-2, 2)
        roll = self.base_roll + random.uniform(-2, 2)
        yaw = self.base_yaw + random.uniform(-2, 2)
        
        # Acceleration: simulate small movements (gravity + small vibrations)
        accel_x = random.uniform(-0.1, 0.1)
        accel_y = random.uniform(-0.1, 0.1)
        accel_z = 1.0 + random.uniform(-0.05, 0.05)  # Gravity
        
        # Gyroscope: small rotational movements
        gyro_x = random.uniform(-5, 5)
        gyro_y = random.uniform(-5, 5)
        gyro_z = random.uniform(-5, 5)
        
        # Magnetometer: simulate compass readings
        compass_x = random.uniform(-50, 50)
        compass_y = random.uniform(-50, 50)
        compass_z = random.uniform(-50, 50)
        
        return SenseHatData(
            temperature=round(temp, 2),
            humidity=round(humidity, 2),
            pressure=round(pressure, 2),
            pitch=round(pitch, 2),
            roll=round(roll, 2),
            yaw=round(yaw, 2),
            accel_x=round(accel_x, 4),
            accel_y=round(accel_y, 4),
            accel_z=round(accel_z, 4),
            gyro_x=round(gyro_x, 2),
            gyro_y=round(gyro_y, 2),
            gyro_z=round(gyro_z, 2),
            compass_x=round(compass_x, 2),
            compass_y=round(compass_y, 2),
            compass_z=round(compass_z, 2),
        )


class FakeSystemReader:
    """Generates fake Raspberry Pi system metrics"""
    
    def __init__(self):
        self.start_time = time.time()
        self.base_cpu_temp = 45.0  # Base CPU temperature
        self.base_cpu_percent = 20.0  # Base CPU usage
        self.base_mem_percent = 50.0  # Base memory usage
        self.base_disk_percent = 40.0  # Base disk usage
        
        import logging
        logging.getLogger("sense_logger").info("Fake system reader initialized")
    
    def read(self) -> RaspberryPiData:
        """Generate fake system metrics with realistic variations"""
        t = time.time() - self.start_time
        
        # CPU temperature: varies with load + noise
        cpu_temp = self.base_cpu_temp + random.uniform(-3, 8)
        
        # CPU usage: varies with sine wave (simulating workload) + noise
        cpu_percent = self.base_cpu_percent + 10 * math.sin(t / 60) + random.uniform(-5, 5)
        cpu_percent = max(5, min(95, cpu_percent))  # Clamp to realistic range
        
        # CPU count: fixed value
        cpu_count = 4
        
        # CPU frequency: varies slightly
        cpu_freq_mhz = 1500 + random.uniform(-100, 100)
        
        # Memory: simulate gradual changes
        mem_total_gb = 4.0  # Fixed total
        mem_percent = self.base_mem_percent + random.uniform(-5, 5)
        mem_percent = max(30, min(80, mem_percent))  # Clamp to realistic range
        mem_used_gb = mem_total_gb * (mem_percent / 100)
        mem_available_gb = mem_total_gb - mem_used_gb
        
        # Disk: simulate gradual changes
        disk_total_gb = 32.0  # Fixed total
        disk_percent = self.base_disk_percent + random.uniform(-1, 1)
        disk_percent = max(35, min(45, disk_percent))  # Clamp to realistic range
        disk_used_gb = disk_total_gb * (disk_percent / 100)
        disk_free_gb = disk_total_gb - disk_used_gb
        
        # Load average: varies with CPU usage
        load_avg_1min = (cpu_percent / 100) * 2 + random.uniform(-0.2, 0.2)
        load_avg_5min = load_avg_1min * 0.9 + random.uniform(-0.1, 0.1)
        load_avg_15min = load_avg_5min * 0.95 + random.uniform(-0.1, 0.1)
        
        return RaspberryPiData(
            cpu_temp=round(cpu_temp, 2),
            cpu_percent=round(cpu_percent, 2),
            cpu_count=cpu_count,
            cpu_freq_mhz=round(cpu_freq_mhz, 2),
            mem_total_gb=round(mem_total_gb, 2),
            mem_used_gb=round(mem_used_gb, 2),
            mem_available_gb=round(mem_available_gb, 2),
            mem_percent=round(mem_percent, 2),
            disk_total_gb=round(disk_total_gb, 2),
            disk_used_gb=round(disk_used_gb, 2),
            disk_free_gb=round(disk_free_gb, 2),
            disk_percent=round(disk_percent, 2),
            load_avg_1min=round(load_avg_1min, 2),
            load_avg_5min=round(load_avg_5min, 2),
            load_avg_15min=round(load_avg_15min, 2),
        )


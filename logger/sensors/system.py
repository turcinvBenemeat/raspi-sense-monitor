"""
Raspberry Pi system metrics reader
"""
import os
import psutil

# Import models - handle both relative and absolute imports
try:
    from models import RaspberryPiData
except ImportError:
    from ..models import RaspberryPiData


class SystemReader:
    """Reads Raspberry Pi system metrics"""
    
    def read(self) -> RaspberryPiData:
        """Read all system metrics and return as model"""
        # CPU temperature (Raspberry Pi specific)
        cpu_temp = None
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                cpu_temp = float(f.read().strip()) / 1000.0  # Convert from millidegrees
        except (FileNotFoundError, IOError):
            pass
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # CPU frequency
        cpu_freq = psutil.cpu_freq()
        cpu_freq_current = cpu_freq.current if cpu_freq else None
        
        # Memory
        mem = psutil.virtual_memory()
        mem_total = mem.total / (1024**3)  # GB
        mem_used = mem.used / (1024**3)  # GB
        mem_available = mem.available / (1024**3)  # GB
        mem_percent = mem.percent
        
        # Disk
        disk = psutil.disk_usage("/")
        disk_total = disk.total / (1024**3)  # GB
        disk_used = disk.used / (1024**3)  # GB
        disk_free = disk.free / (1024**3)  # GB
        disk_percent = disk.percent
        
        # Load average (1, 5, 15 minutes)
        load_avg = os.getloadavg()
        
        return RaspberryPiData(
            cpu_temp=cpu_temp,
            cpu_percent=cpu_percent,
            cpu_count=cpu_count,
            cpu_freq_mhz=cpu_freq_current,
            mem_total_gb=mem_total,
            mem_used_gb=mem_used,
            mem_available_gb=mem_available,
            mem_percent=mem_percent,
            disk_total_gb=disk_total,
            disk_used_gb=disk_used,
            disk_free_gb=disk_free,
            disk_percent=disk_percent,
            load_avg_1min=load_avg[0],
            load_avg_5min=load_avg[1],
            load_avg_15min=load_avg[2],
        )


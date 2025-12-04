import os
import time
from sense_hat import SenseHat
import psutil
from db import get_database, SenseHatData, RaspberryPiData

sense = SenseHat()
db = get_database()


def read_sense_data() -> SenseHatData:
    """Read Sense HAT sensor data and return as model"""
    # Environmental sensors
    temp = sense.get_temperature()
    hum = sense.get_humidity()
    pres = sense.get_pressure()

    # Orientation (requires calibration)
    orientation = sense.get_orientation()
    pitch = orientation.get("pitch")
    roll = orientation.get("roll")
    yaw = orientation.get("yaw")

    # Acceleration (raw)
    accel_raw = sense.get_accelerometer_raw()
    ax = accel_raw["x"]
    ay = accel_raw["y"]
    az = accel_raw["z"]

    # Gyroscope (raw)
    gyro_raw = sense.get_gyroscope_raw()
    gx = gyro_raw["x"]
    gy = gyro_raw["y"]
    gz = gyro_raw["z"]

    # Magnetometer/Compass (raw)
    compass_raw = sense.get_compass_raw()
    mx = compass_raw["x"]
    my = compass_raw["y"]
    mz = compass_raw["z"]

    return SenseHatData(
        temperature=temp,
        humidity=hum,
        pressure=pres,
        pitch=pitch,
        roll=roll,
        yaw=yaw,
        accel_x=ax,
        accel_y=ay,
        accel_z=az,
        gyro_x=gx,
        gyro_y=gy,
        gyro_z=gz,
        compass_x=mx,
        compass_y=my,
        compass_z=mz,
    )


def read_system_data() -> RaspberryPiData:
    """Read Raspberry Pi system metrics and return as model"""
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




def main():
    interval = float(os.environ.get("SAMPLE_INTERVAL", "5"))
    while True:
        try:
            # Read and write Sense HAT data
            sense_data = read_sense_data()
            db.write_sensehat_data(sense_data)
            print("Wrote Sense HAT:", sense_data, flush=True)
            
            # Read and write system metrics
            system_data = read_system_data()
            db.write_raspberry_pi_data(system_data)
            print("Wrote System:", system_data, flush=True)
        except Exception as e:
            print("Error:", e, flush=True)
        time.sleep(interval)


if __name__ == "__main__":
    main()
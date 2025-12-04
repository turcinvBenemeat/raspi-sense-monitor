import os
import time
from sense_hat import SenseHat
from influxdb_client import InfluxDBClient, Point, WritePrecision
import psutil

sense = SenseHat()

# InfluxDB configuration from environment variables
INFLUX_URL = os.environ.get("INFLUX_URL", "http://localhost:8086")
INFLUX_TOKEN = os.environ.get("INFLUX_TOKEN", "super-secret-token")
INFLUX_ORG = os.environ.get("INFLUX_ORG", "bt-org")
INFLUX_BUCKET = os.environ.get("INFLUX_BUCKET", "sensehat")

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api()


def read_sense_data():
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

    return {
        "temperature": temp,
        "humidity": hum,
        "pressure": pres,
        "pitch": pitch,
        "roll": roll,
        "yaw": yaw,
        "accel_x": ax,
        "accel_y": ay,
        "accel_z": az,
        "gyro_x": gx,
        "gyro_y": gy,
        "gyro_z": gz,
        "compass_x": mx,
        "compass_y": my,
        "compass_z": mz,
    }


def read_system_data():
    """Read Raspberry Pi system metrics"""
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
    
    return {
        "cpu_temp": cpu_temp,
        "cpu_percent": cpu_percent,
        "cpu_count": cpu_count,
        "cpu_freq_mhz": cpu_freq_current,
        "mem_total_gb": mem_total,
        "mem_used_gb": mem_used,
        "mem_available_gb": mem_available,
        "mem_percent": mem_percent,
        "disk_total_gb": disk_total,
        "disk_used_gb": disk_used,
        "disk_free_gb": disk_free,
        "disk_percent": disk_percent,
        "load_avg_1min": load_avg[0],
        "load_avg_5min": load_avg[1],
        "load_avg_15min": load_avg[2],
    }


def write_to_influx(data):
    p = (
        Point("sensehat")
        .field("temperature", float(data["temperature"]))
        .field("humidity", float(data["humidity"]))
        .field("pressure", float(data["pressure"]))
        .field("pitch", float(data["pitch"]))
        .field("roll", float(data["roll"]))
        .field("yaw", float(data["yaw"]))
        .field("accel_x", float(data["accel_x"]))
        .field("accel_y", float(data["accel_y"]))
        .field("accel_z", float(data["accel_z"]))
        .field("gyro_x", float(data["gyro_x"]))
        .field("gyro_y", float(data["gyro_y"]))
        .field("gyro_z", float(data["gyro_z"]))
        .field("compass_x", float(data["compass_x"]))
        .field("compass_y", float(data["compass_y"]))
        .field("compass_z", float(data["compass_z"]))
        .time(time.time_ns(), WritePrecision.NS)
    )
    write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=p)


def write_system_to_influx(data):
    """Write system metrics to InfluxDB"""
    p = Point("raspberry_pi")
    
    # Add fields only if they're not None
    if data["cpu_temp"] is not None:
        p = p.field("cpu_temp", float(data["cpu_temp"]))
    if data["cpu_percent"] is not None:
        p = p.field("cpu_percent", float(data["cpu_percent"]))
    if data["cpu_count"] is not None:
        p = p.field("cpu_count", int(data["cpu_count"]))
    if data["cpu_freq_mhz"] is not None:
        p = p.field("cpu_freq_mhz", float(data["cpu_freq_mhz"]))
    
    p = (
        p.field("mem_total_gb", float(data["mem_total_gb"]))
        .field("mem_used_gb", float(data["mem_used_gb"]))
        .field("mem_available_gb", float(data["mem_available_gb"]))
        .field("mem_percent", float(data["mem_percent"]))
        .field("disk_total_gb", float(data["disk_total_gb"]))
        .field("disk_used_gb", float(data["disk_used_gb"]))
        .field("disk_free_gb", float(data["disk_free_gb"]))
        .field("disk_percent", float(data["disk_percent"]))
        .field("load_avg_1min", float(data["load_avg_1min"]))
        .field("load_avg_5min", float(data["load_avg_5min"]))
        .field("load_avg_15min", float(data["load_avg_15min"]))
        .time(time.time_ns(), WritePrecision.NS)
    )
    write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=p)


def main():
    interval = float(os.environ.get("SAMPLE_INTERVAL", "5"))
    while True:
        try:
            # Read and write Sense HAT data
            sense_data = read_sense_data()
            write_to_influx(sense_data)
            print("Wrote Sense HAT:", sense_data, flush=True)
            
            # Read and write system metrics
            system_data = read_system_data()
            write_system_to_influx(system_data)
            print("Wrote System:", system_data, flush=True)
        except Exception as e:
            print("Error:", e, flush=True)
        time.sleep(interval)


if __name__ == "__main__":
    main()
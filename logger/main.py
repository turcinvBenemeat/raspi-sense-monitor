import os
import time
from sense_hat import SenseHat
import psutil
import psycopg2

sense = SenseHat()

# PostgreSQL configuration from environment variables
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")
POSTGRES_DB = os.environ.get("POSTGRES_DB", "sensehat")
POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "postgres")

# Create database connection
def get_db_connection():
    return psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )

# Initialize database tables
def init_database():
    try:
        conn = get_db_connection()
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
        conn.close()
        print("Database initialized successfully", flush=True)
    except Exception as e:
        print(f"Warning: Could not initialize database: {e}", flush=True)
        print("Database will be initialized on first connection", flush=True)

# Initialize database on import (will retry on first write if it fails)
init_database()


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


def write_to_postgres(data):
    """Write Sense HAT data to PostgreSQL"""
    conn = get_db_connection()
    cur = conn.cursor()
    
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
        float(data["temperature"]),
        float(data["humidity"]),
        float(data["pressure"]),
        float(data["pitch"]),
        float(data["roll"]),
        float(data["yaw"]),
        float(data["accel_x"]),
        float(data["accel_y"]),
        float(data["accel_z"]),
        float(data["gyro_x"]),
        float(data["gyro_y"]),
        float(data["gyro_z"]),
        float(data["compass_x"]),
        float(data["compass_y"]),
        float(data["compass_z"]),
    ))
    
    conn.commit()
    cur.close()
    conn.close()


def write_system_to_postgres(data):
    """Write system metrics to PostgreSQL"""
    conn = get_db_connection()
    cur = conn.cursor()
    
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
        data["cpu_temp"],
        float(data["cpu_percent"]) if data["cpu_percent"] is not None else None,
        int(data["cpu_count"]) if data["cpu_count"] is not None else None,
        float(data["cpu_freq_mhz"]) if data["cpu_freq_mhz"] is not None else None,
        float(data["mem_total_gb"]),
        float(data["mem_used_gb"]),
        float(data["mem_available_gb"]),
        float(data["mem_percent"]),
        float(data["disk_total_gb"]),
        float(data["disk_used_gb"]),
        float(data["disk_free_gb"]),
        float(data["disk_percent"]),
        float(data["load_avg_1min"]),
        float(data["load_avg_5min"]),
        float(data["load_avg_15min"]),
    ))
    
    conn.commit()
    cur.close()
    conn.close()


def main():
    interval = float(os.environ.get("SAMPLE_INTERVAL", "5"))
    while True:
        try:
            # Read and write Sense HAT data
            sense_data = read_sense_data()
            write_to_postgres(sense_data)
            print("Wrote Sense HAT:", sense_data, flush=True)
            
            # Read and write system metrics
            system_data = read_system_data()
            write_system_to_postgres(system_data)
            print("Wrote System:", system_data, flush=True)
        except Exception as e:
            print("Error:", e, flush=True)
        time.sleep(interval)


if __name__ == "__main__":
    main()
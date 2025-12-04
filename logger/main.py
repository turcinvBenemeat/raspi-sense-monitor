import os
import time
from sense_hat import SenseHat
from influxdb_client import InfluxDBClient, Point, WritePrecision

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
        .time(time.time_ns(), WritePrecision.NS)
    )
    write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=p)


def main():
    interval = float(os.environ.get("SAMPLE_INTERVAL", "5"))
    while True:
        try:
            data = read_sense_data()
            write_to_influx(data)
            print("Wrote:", data, flush=True)
        except Exception as e:
            print("Error:", e, flush=True)
        time.sleep(interval)


if __name__ == "__main__":
    main()
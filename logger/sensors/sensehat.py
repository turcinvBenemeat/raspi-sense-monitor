"""
Sense HAT sensor reader
"""
from sense_hat import SenseHat
from ..models import SenseHatData


class SenseHatReader:
    """Reads data from Sense HAT sensors"""
    
    def __init__(self):
        self.sense = SenseHat()
    
    def read(self) -> SenseHatData:
        """Read all Sense HAT sensor data and return as model"""
        # Environmental sensors
        temp = self.sense.get_temperature()
        hum = self.sense.get_humidity()
        pres = self.sense.get_pressure()

        # Orientation (requires calibration)
        orientation = self.sense.get_orientation()
        pitch = orientation.get("pitch")
        roll = orientation.get("roll")
        yaw = orientation.get("yaw")

        # Acceleration (raw)
        accel_raw = self.sense.get_accelerometer_raw()
        ax = accel_raw["x"]
        ay = accel_raw["y"]
        az = accel_raw["z"]

        # Gyroscope (raw)
        gyro_raw = self.sense.get_gyroscope_raw()
        gx = gyro_raw["x"]
        gy = gyro_raw["y"]
        gz = gyro_raw["z"]

        # Magnetometer/Compass (raw)
        compass_raw = self.sense.get_compass_raw()
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


"""
Sense HAT sensor reader
"""
from sense_hat import SenseHat

# Import models - handle both relative and absolute imports
try:
    from models import SenseHatData
except ImportError:
    from ..models import SenseHatData


class SenseHatReader:
    """Reads data from Sense HAT sensors"""
    
    def __init__(self):
        self.sense = None
        self.available = False
        self._initialize()
    
    def _initialize(self):
        """Initialize Sense HAT if available"""
        try:
            self.sense = SenseHat()
            # Test if Sense HAT is actually connected
            _ = self.sense.get_temperature()
            self.available = True
            import logging
            logging.getLogger("sense_logger").info("Sense HAT detected and initialized")
        except (ImportError, OSError, RuntimeError) as e:
            self.available = False
            import logging
            logger = logging.getLogger("sense_logger")
            logger.warning(f"Sense HAT not available: {e}")
            logger.info("Continuing without Sense HAT sensors...")
    
    def is_available(self) -> bool:
        """Check if Sense HAT is available"""
        return self.available
    
    def read(self) -> SenseHatData:
        """Read all Sense HAT sensor data and return as model"""
        if not self.available:
            raise RuntimeError("Sense HAT is not available")
        
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


"""
Main entry point for Raspberry Pi Sense HAT Monitor
"""
import time
from config import Config
from database import get_database
from utils.logger import setup_logger

# Setup logger
logger = setup_logger()

# Import sensor readers based on mode
if Config.FAKE_DATA:
    from sensors.fake import FakeSenseHatReader, FakeSystemReader
    SenseHatReader = FakeSenseHatReader
    SystemReader = FakeSystemReader
    logger.info("FAKE_DATA mode enabled - using fake sensor data")
else:
    from sensors import SenseHatReader, SystemReader


def main():
    """Main logging loop"""
    db = get_database()
    sensehat_reader = SenseHatReader()
    system_reader = SystemReader()
    
    interval = Config.SAMPLE_INTERVAL
    
    device_info = f" (Device: {Config.DEVICE_ID})" if Config.DEVICE_ID else ""
    mode_info = " [FAKE DATA MODE]" if Config.FAKE_DATA else ""
    logger.info(f"Starting logger{device_info}{mode_info}...")
    
    if not Config.FAKE_DATA and not sensehat_reader.is_available():
        logger.warning("Sense HAT not available, continuing with system metrics only")
    
    while True:
        try:
            # Read and write Sense HAT data (if available or in fake mode)
            if Config.FAKE_DATA or sensehat_reader.is_available():
                try:
                    sense_data = sensehat_reader.read()
                    db.write_sensehat_data(sense_data)
                    logger.debug(f"Wrote Sense HAT: {sense_data}")
                except Exception as e:
                    logger.error(f"Sense HAT error: {e}", exc_info=True)
            
            # Read and write system metrics
            system_data = system_reader.read()
            db.write_raspberry_pi_data(system_data)
            logger.debug(f"Wrote System: {system_data}")
        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)
        time.sleep(interval)


if __name__ == "__main__":
    main()

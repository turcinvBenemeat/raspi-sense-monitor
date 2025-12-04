"""
Main entry point for Raspberry Pi Sense HAT Monitor
"""
import time
from config import Config
from database import get_database
from sensors import SenseHatReader, SystemReader
from utils.logger import setup_logger

# Setup logger
logger = setup_logger()


def main():
    """Main logging loop"""
    db = get_database()
    sensehat_reader = SenseHatReader()
    system_reader = SystemReader()
    
    interval = Config.SAMPLE_INTERVAL
    
    device_info = f" (Device: {Config.DEVICE_ID})" if Config.DEVICE_ID else ""
    logger.info(f"Starting logger{device_info}...")
    
    if not sensehat_reader.is_available():
        logger.warning("Sense HAT not available, continuing with system metrics only")
    
    while True:
        try:
            # Read and write Sense HAT data (if available)
            if sensehat_reader.is_available():
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

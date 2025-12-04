"""
Main entry point for Raspberry Pi Sense HAT Monitor
"""
import time
from config import Config
from database import get_database
from sensors import SenseHatReader, SystemReader
from utils import setup_logger

# Setup logger
logger = setup_logger()


def main():
    """Main logging loop"""
    db = get_database()
    system_reader = SystemReader()
    
    # Initialize Sense HAT reader if enabled
    sensehat_reader = None
    use_sensehat = False
    
    if Config.ENABLE_SENSEHAT:
        sensehat_reader = SenseHatReader()
        if sensehat_reader.is_available():
            use_sensehat = True
            logger.info("Sense HAT logging enabled")
        else:
            logger.warning("Sense HAT not available, continuing with system metrics only")
    else:
        logger.info("Sense HAT logging disabled by configuration")
    
    if not Config.ENABLE_SYSTEM_METRICS:
        logger.warning("System metrics logging is disabled")
    
    interval = Config.SAMPLE_INTERVAL
    
    device_info = f" (Device: {Config.DEVICE_ID})" if Config.DEVICE_ID else ""
    logger.info(f"Starting logger{device_info}...")
    
    while True:
        try:
            # Read and write Sense HAT data (if available and enabled)
            if use_sensehat and sensehat_reader:
                try:
                    sense_data = sensehat_reader.read()
                    db.write_sensehat_data(sense_data)
                    logger.debug(f"Wrote Sense HAT: {sense_data}")
                except Exception as e:
                    logger.error(f"Sense HAT error: {e}", exc_info=True)
            
            # Read and write system metrics (if enabled)
            if Config.ENABLE_SYSTEM_METRICS:
                system_data = system_reader.read()
                db.write_raspberry_pi_data(system_data)
                logger.debug(f"Wrote System: {system_data}")
        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)
        time.sleep(interval)


if __name__ == "__main__":
    main()

"""
Main entry point for Raspberry Pi Sense HAT Monitor
"""
import time
from config import Config
from database import get_database
from sensors import SenseHatReader, SystemReader


def main():
    """Main logging loop"""
    db = get_database()
    sensehat_reader = SenseHatReader()
    system_reader = SystemReader()
    
    interval = Config.SAMPLE_INTERVAL
    
    while True:
        try:
            # Read and write Sense HAT data
            sense_data = sensehat_reader.read()
            db.write_sensehat_data(sense_data)
            print("Wrote Sense HAT:", sense_data, flush=True)
            
            # Read and write system metrics
            system_data = system_reader.read()
            db.write_raspberry_pi_data(system_data)
            print("Wrote System:", system_data, flush=True)
        except Exception as e:
            print("Error:", e, flush=True)
        time.sleep(interval)


if __name__ == "__main__":
    main()

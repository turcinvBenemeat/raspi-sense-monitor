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
    system_reader = SystemReader()
    
    # Initialize Sense HAT reader if enabled
    sensehat_reader = None
    use_sensehat = False
    
    if Config.ENABLE_SENSEHAT:
        sensehat_reader = SenseHatReader()
        if sensehat_reader.is_available():
            use_sensehat = True
            print("Sense HAT logging enabled", flush=True)
        else:
            print("Sense HAT not available, continuing with system metrics only", flush=True)
    else:
        print("Sense HAT logging disabled by configuration", flush=True)
    
    if not Config.ENABLE_SYSTEM_METRICS:
        print("Warning: System metrics logging is disabled", flush=True)
    
    interval = Config.SAMPLE_INTERVAL
    
    device_info = f" (Device: {Config.DEVICE_ID})" if Config.DEVICE_ID else ""
    print(f"Starting logger{device_info}...", flush=True)
    
    while True:
        try:
            # Read and write Sense HAT data (if available and enabled)
            if use_sensehat and sensehat_reader:
                try:
                    sense_data = sensehat_reader.read()
                    db.write_sensehat_data(sense_data)
                    print("Wrote Sense HAT:", sense_data, flush=True)
                except Exception as e:
                    print(f"Sense HAT error: {e}", flush=True)
            
            # Read and write system metrics (if enabled)
            if Config.ENABLE_SYSTEM_METRICS:
                system_data = system_reader.read()
                db.write_raspberry_pi_data(system_data)
                print("Wrote System:", system_data, flush=True)
        except Exception as e:
            print("Error:", e, flush=True)
        time.sleep(interval)


if __name__ == "__main__":
    main()

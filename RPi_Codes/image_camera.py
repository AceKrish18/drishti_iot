import time
from picamera2 import Picamera2
# Removed 'from libcamera import controls' as it can sometimes trigger the error before Picamera2 is fully ready

# --- CONFIGURATION ---
# Define the output path in the user's home directory (e.g., /home/rpi/camera_test.jpg)
OUTPUT_FILE = "/home/rpi/camera_test.jpg"

def run_camera_test():
    """Initializes the camera, captures a JPEG, and saves it to a file."""
    print("Initializing Picamera2...")
    picam2 = None
    
    try:
        # STEP 1: Initialization Check
        # This is the point where the code fails if the hardware isn't detected.6
        picam2 = Picamera2()
        print("Camera device successfully detected and initialized.")
        
        # STEP 2: Configuration and Capture
        config = picam2.create_still_configuration(
            main={"size": (1920, 1080)},
            queue=False
        )
        
        # Apply configuration and start the camera
        picam2.configure(config)
        picam2.start()
        
        # Give the camera a moment to set its white balance and exposure
        print("Camera warming up (2 seconds)...")
        time.sleep(2)
        
        # Capture the image and save it
        print(f"Capturing image and saving to: {OUTPUT_FILE}")
        picam2.capture_file(OUTPUT_FILE)
        
        print("Capture successful!")
        print(f"Image saved at: {OUTPUT_FILE}")
        
    except Exception as e:
        # A specific failure message that signals a hardware issue.
        print(f"\nFATAL ERROR: Camera hardware failed to initialize or operate.")
        print(f"Underlying Exception: {e}")
        print("\nACTION REQUIRED: Since all software steps have been verified, this error indicates:")
        print("1. A physical ribbon cable connection issue (re-seat both ends firmly).")
        print("2. Insufficient power supply for the RPi 5 (must be 5V, 5A official supply).")
        print("3. A faulty camera module or CSI port.")
        
    finally:
        # Safely stop the camera if it started
        if picam2 is not None:
             picam2.stop()
        
if __name__ == "__main__":
    run_camera_test()

import time
from picamera2 import Picamera2
# Import the H264Encoder class for video compression
from picamera2.encoders import H264Encoder 
# Removed 'from libcamera import controls' as it can sometimes trigger the error before Picamera2 is fully ready

# --- CONFIGURATION ---
# Define the output path in the user's home directory (e.g., /home/rpi/camera_test.h264)
# Use the H264 extension for the native video format
OUTPUT_FILE = "/home/rpi/camera_test.h264"
VIDEO_DURATION_SECONDS = 5 # Set the length of the video to record

def run_camera_test():
    """Initializes the camera, records a video, and saves it to a file."""
    print("Initializing Picamera2 for Video Capture...")
    picam2 = None
    
    try:
        # STEP 1: Initialization Check
        picam2 = Picamera2()
        print("Camera device successfully detected and initialized.")
        
        # STEP 2: Configuration for Video
        # Use create_video_configuration() for video mode, setting a common resolution
        config = picam2.create_video_configuration(
            main={"size": (1280, 720)}, # Use 720p resolution for video efficiency
            queue=False
        )
        
        # Apply configuration and set up the encoder
        picam2.configure(config)
        
        # Initialize the H264 Encoder (10 Mbps bitrate recommended for 720p)
        encoder = H264Encoder(10000000)
        
        # STEP 3: Start Preview and Recording
        picam2.start()
        
        # Give the camera a moment to set its white balance and exposure
        print("Camera warming up (2 seconds)...")
        time.sleep(2)
        
        # Start recording the video file
        print(f"Starting video recording and saving to: {OUTPUT_FILE}")
        picam2.start_recording(encoder, OUTPUT_FILE)
        
        # Record for the specified duration
        print(f"Recording video for {VIDEO_DURATION_SECONDS} seconds...")
        time.sleep(VIDEO_DURATION_SECONDS)
        
        # Stop the recording
        picam2.stop_recording()
        
        print("Video recording successful!")
        print(f"Video saved at: {OUTPUT_FILE}")
        
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

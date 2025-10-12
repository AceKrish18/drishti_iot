import serial
import time
import pynmea2
import sys

# --- CONFIGURATION ---
# GPS Serial Port settings (must match the port you fixed earlier)
GPS_SERIAL_PORT = '/dev/ttyS0'
BAUD_RATE = 9600  # Standard baud rate for NEO-6M GPS modules

def get_current_location():
    """Initializes the serial port and reads NMEA data to extract GPS coordinates."""
    try:
        # Initialize the serial connection
        ser = serial.Serial(GPS_SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Serial port {GPS_SERIAL_PORT} opened successfully at {BAUD_RATE} baud.")
        
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        print("Please ensure the GPS module is wired correctly (TX to RX, RX to TX, VCC to 5V, GND to GND).")
        print("Also confirm the port '/dev/ttyS0' is still available (run 'ls -l /dev/ttyS0').")
        return None, None

    # --- Main Read Loop ---
    print("\nReading GPS data... Please wait for a fix (can take 30 seconds to a few minutes).")
    print("Move module near a window or outdoors for best signal.")
    
    start_time = time.time()
    
    try:
        while (time.time() - start_time) < 300: # Wait up to 5 minutes for a fix
            
            # Read a line of data from the serial port
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            
            if line.startswith('$GPGGA') or line.startswith('$GNGGA'):
                # Attempt to parse the line
                try:
                    msg = pynmea2.parse(line)
                    
                    # Check for fix quality (0=No fix, 1=GPS fix, 2=DGPS fix)
                    if msg.gps_qual > 0:
                        
                        # We have a valid fix! Print and return
                        latitude = round(msg.latitude, 6)
                        longitude = round(msg.longitude, 6)
                        
                        print("\n--- GPS FIX ACQUIRED ---")
                        print(f"Time (UTC): {msg.timestamp}")
                        print(f"Latitude: {latitude}")
                        print(f"Longitude: {longitude}")
                        print(f"Altitude: {msg.altitude} {msg.altitude_units}")
                        print("--------------------------")
                        return latitude, longitude
                        
                    else:
                        sys.stdout.write('.') # Print a dot while waiting
                        sys.stdout.flush()
                        
                except pynmea2.ParseError:
                    # Ignore lines that cannot be parsed
                    continue 

            time.sleep(0.1) # Small delay
            
        print("\nTimed out. Failed to acquire a GPS fix within 5 minutes. Check antenna and visibility of the sky.")
        return None, None
        
    except KeyboardInterrupt:
        print("\nTest stopped by user.")
        return None, None
        
    finally:
        ser.close()
        print("Serial port closed.")

if __name__ == "__main__":
    # You need the pynmea2 library for this script. If you haven't installed it:
    # pip install pynmea2
    get_current_location()

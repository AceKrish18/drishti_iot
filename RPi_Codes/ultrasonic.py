import time
import sys
import lgpio as gpio

# --- CONFIGURATION (Adjust these BCM pin numbers based on your wiring) ---
# NOTE: Using BCM numbering (e.g., 23 and 24, not physical pin 16 and 18)
TRIGGER_PIN = 23  # Output pin to TRIG
ECHO_PIN = 24     # Input pin from ECHO (MUST BE VIA VOLTAGE DIVIDER)

# Speed of sound in cm/µs
SPEED_OF_SOUND = 0.0343 
# Time out after 0.5 seconds if no echo is received (to prevent infinite loops)
TIMEOUT = 0.5

# --- Setup ---
try:
    # Open the GPIO chip
    h = gpio.gpiochip_open(0)
    
    # Set up the pins
    gpio.gpio_claim_output(h, TRIGGER_PIN)
    gpio.gpio_claim_input(h, ECHO_PIN)
    
except Exception as e:
    print(f"Error initializing GPIO: {e}")
    sys.exit()

def get_distance():
    # 1. Ensure the trigger is low
    gpio.gpio_write(h, TRIGGER_PIN, 0)
    time.sleep(0.000002) # Wait 2 µs
    
    # 2. Send the 10µs pulse to trigger the sensor
    gpio.gpio_write(h, TRIGGER_PIN, 1)
    time.sleep(0.000010) # 10 µs pulse
    gpio.gpio_write(h, TRIGGER_PIN, 0)

    # 3. Wait for the ECHO pin to go HIGH (pulse start)
    start_time = time.time()
    
    # Wait until Echo pin is high
    while gpio.gpio_read(h, ECHO_PIN) == 0:
        if time.time() - start_time > TIMEOUT:
            return -1 # Timeout
        time.sleep(0.000001)
    
    pulse_start = time.time()

    # 4. Wait for the ECHO pin to go LOW (pulse end)
    while gpio.gpio_read(h, ECHO_PIN) == 1:
        if time.time() - start_time > TIMEOUT:
            return -1 # Timeout
        time.sleep(0.000001)

    pulse_end = time.time()
    
    # 5. Calculate distance
    pulse_duration = pulse_end - pulse_start
    distance_cm = (pulse_duration * 1000000) * SPEED_OF_SOUND / 2
    
    return round(distance_cm, 2)

# --- Main Loop ---
try:
    print("--- Ultrasonic Sensor Test ---")
    print(f"Testing Trigger Pin: {TRIGGER_PIN}, Echo Pin: {ECHO_PIN}")
    while True:
        dist = get_distance()
        
        if dist == -1:
            print("Timeout: Sensor failed to return an echo pulse.")
        elif dist > 400:
            print("Distance: Out of range (> 400 cm)")
        else:
            print(f"Distance: {dist} cm")
            
        time.sleep(1)

except KeyboardInterrupt:
    print("\nTest stopped by user.")
    
finally:
    # Cleanup GPIO resources
    gpio.gpio_close(h)
    print("GPIO resources released.")

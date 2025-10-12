import time
from pushbullet import Listener, Pushbullet

# --- CONFIGURATION ---
# Replace this with the Access Token you generated
API_KEY = "o.ACzUX1nPIhUlmLtIf5pCOZusDpFdt3OW" 

# --- MAIN SCRIPT ---
def on_push(push):
    """
    Callback function to handle incoming pushes.
    This function will be executed for every new event.
    """
    # Notifications from your phone are of type 'mirror'
    if push.get("type") == "mirror":
        print(f"Notification Received!")
        print(f"  App: {push.get('application_name')}")
        print(f"  Title: {push.get('title')}")
        print(f"  Body: {push.get('body')}")
        print("-" * 20)
        
        # Here you can add your own logic to process the data
        # For example, if the notification is from a specific app:
        # if push.get('application_name') == "Gmail":
        #     # Do something specific for Gmail notifications
        #     print("It's an email!")
            

def main():
    """
    Main function to start the listener.
    """
    if API_KEY == "YOUR_ACCESS_TOKEN_HERE":
        print("Error: Please replace 'YOUR_ACCESS_TOKEN_HERE' with your actual Pushbullet API Key.")
        return

    pb = Pushbullet(API_KEY)
    
    # Create a listener that runs in a separate thread
    listener = Listener(account=pb, on_push=on_push)
    
    try:
        print("Listening for notifications... Press Ctrl+C to exit.")
        listener.run_forever()
    except KeyboardInterrupt:
        print("Stopping listener.")
    finally:
        listener.close() # Close the connection

if __name__ == "__main__":
    main()
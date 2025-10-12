import google.generativeai as genai
from google.api_core import exceptions

def verify_gemini_api_key():
    """
    A simple script to verify if a Gemini API key is valid.
    """
    print("--- Gemini API Key Verification Tool ---")
    
    # Paste your API key here, inside the quotes
    api_key_to_test = "AIzaSyAlUPOxXg_h2Cp_F26zqq7kV8reYbNmceE"

    if not api_key_to_test or "YOUR_GEMINI_API_KEY_HERE" in api_key_to_test:
        print("\n ERROR: Please paste your API key into the 'api_key_to_test' variable in this script.")
        return

    try:
        # Configure the client with the provided key
        genai.configure(api_key=api_key_to_test)
        
        print("\nAttempting to connect to Google's servers...")
        
        # Make a lightweight, non-generative call to list models.
        # This is a standard way to check authentication.
        models = genai.list_models()
        
        print("\n SUCCESS! Your API key is valid and working correctly.")
        print("Successfully authenticated and received a list of available models.")
        
    except exceptions.PermissionDenied as e:
        print("\n FAILURE: API Key is NOT valid.")
        print("--------------------------------------------------")
        print("Google's server returned a 'Permission Denied' error.")
        print("This confirms the API key you provided is invalid or has been revoked.")
        print("Please generate a NEW key in Google AI Studio and try again.")
        print("--------------------------------------------------")
        # print(f"Full error details: {e}") # Uncomment for more technical details

    except Exception as e:
        print(f"\n An unexpected error occurred: {e}")
        print("This might be a network issue or something else. Please check your internet connection.")

if __name__ == "__main__":
    verify_gemini_api_key()

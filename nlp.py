# This script demonstrates how to use the Google Gemini API with Python.
#
# Before running, you need to install the library:
# pip install google-generativeai

import google.generativeai as genai
import os

def main():
    """
    Main function to configure the API, send a prompt, and print the response.
    """
    try:
        # --- Configuration ---
        # Configure the API key.
        # IMPORTANT: Replace "YOUR_API_KEY" with your actual Gemini API key.
        # For better security, it's recommended to use environment variables
        # or a secret management system instead of hardcoding the key.
        # Example using environment variable:
        # api_key = os.environ.get("GEMINI_API_KEY")
        # genai.configure(api_key=api_key)
        
        # api_key = "AIzaSyAlUPOxXg_h2Cp_F26zqq7kV8reYbNmceE" # <-- PASTE YOUR KEY HERE
        
        if api_key == "YOUR_API_KEY":
            print("Please replace 'YOUR_API_KEY' with your actual Gemini API key.")
            return

        genai.configure(api_key=api_key)

        # --- Model Initialization ---
        # Create an instance of the generative model.
        # Using the 'gemini-2.5-flash' model as requested.
        model = genai.GenerativeModel('gemini-2.5-flash')

        # --- Prompt and Generation ---
        # Define the prompt you want to send to the model.
        prompt = "what are hardships of blind people?"

        print(f"Sending prompt: '{prompt}'")

        # Generate content based on the prompt.
        response = model.generate_content(prompt)

        # --- Display the Response ---
        # Print the generated text from the response.
        print("\n--- Gemini API Response ---")
        print(response.text)
        print("-------------------------\n")

    except Exception as e:
        print(f"An error occurred: {e}")
        print("\nPlease ensure your API key is correct and you have an active internet connection.")

if __name__ == "__main__":
    main()


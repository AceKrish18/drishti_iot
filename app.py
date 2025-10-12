from flask import Flask, render_template, jsonify
import threading
import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
import playsound
import tempfile
import os
import re
import sys
import time

# --- Force the script to ignore any potentially conflicting environment variables ---
if 'GOOGLE_API_KEY' in os.environ:
    print("Found and removed a conflicting GOOGLE_API_KEY environment variable.")
    del os.environ['GOOGLE_API_KEY']

app = Flask(__name__)

# --- Paste your VALID Gemini API key here ---
API_KEY = "AIzaSyAlUPOxXg_h2Cp_F26zqq7kV8reYbNmceE"

# This dictionary is shared between the Flask app and the voice assistant thread
latest_qa = {"question": None, "answer": None}
voice_thread = None

# --- API Key Verification Function ---
def verify_api_key():
    """Checks if the provided API key is valid upon starting the app."""
    print("\n--- Verifying Gemini API Key ---")
    if not API_KEY or API_KEY == "YOUR_VALID_GEMINI_API_KEY":
        print(" FAILURE: API Key is not set. Please paste your key into the API_KEY variable.")
        sys.exit(1)
    try:
        genai.configure(api_key=API_KEY)
        models = [m for m in genai.list_models()]
        if not models:
            raise Exception("No models found, key might be restricted.")
        print(" SUCCESS: Your API key is valid and connected successfully.")
    except Exception as e:
        print(f"FAILURE: The API key is NOT valid. Error: {e}")
        print("--- Please generate a new key from Google AI Studio and restart the app. ---")
        sys.exit(1)

# --- Voice Assistant Functions ---

def speak(text):
    """Speak the text aloud using gTTS"""
    if text:
        clean_text = re.sub(r'[*_`]', '', text).replace('\n', '. ')
        tts = gTTS(clean_text, lang='en')
        tmp_file = os.path.join(tempfile.gettempdir(), "temp_speech.mp3")
        tts.save(tmp_file)
        playsound.playsound(tmp_file)
        os.remove(tmp_file)

def listen_to_voice():
    """Capture voice input and convert to text"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening... Please speak your question:")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Sorry, could not understand your voice.")
        return None
    except sr.RequestError as e:
        print(f"Speech recognition request failed; {e}")
        return None

def ask_gemini(prompt):
    """Send text prompt to Gemini API and get a concise response"""
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel("gemini-2.5-pro")
        response = model.generate_content(f"Answer concisely: {prompt}")
        return response.text
    except Exception as e:
        print(f"Error during Gemini API call: {e}")
        return f"An error occurred: {str(e)}"

def run_voice_assistant(qa_storage):
    """Run the voice assistant only once."""
    print("\nConfiguring Gemini API for the voice assistant thread...")
    genai.configure(api_key=API_KEY)
    print("Configuration complete for this thread.")

    user_input = listen_to_voice()
    if not user_input:
        qa_storage['question'] = "No input detected."
        qa_storage['answer'] = "Assistant stopped."
        return

    qa_storage['question'] = user_input
    qa_storage['answer'] = "Thinking..."

    if user_input.lower() in ["exit", "quit", "stop"]:
        print("Exiting voice assistant...")
        speak("Goodbye!")
        qa_storage['question'] = "Exiting..."
        qa_storage['answer'] = "Assistant stopped."
        return

    answer = ask_gemini(user_input)
    print("\nGemini:", answer)
    qa_storage['answer'] = answer
    speak(answer)

# --- Flask Routes ---

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start_voice_assistant")
def start_voice_assistant():
    """Starts the voice assistant in a separate thread."""
    global voice_thread
    if voice_thread is None or not voice_thread.is_alive():
        voice_thread = threading.Thread(target=run_voice_assistant, args=(latest_qa,))
        voice_thread.daemon = True
        voice_thread.start()
        return jsonify({"status": "Voice assistant started successfully."})
    else:
        return jsonify({"status": "Voice assistant is already running."})

@app.route("/get_latest_qa")
def get_latest_qa():
    """Provides the latest question and answer to the frontend."""
    return jsonify(latest_qa)

if __name__ == "__main__":
    # Run the verification before starting the web server
    verify_api_key()
    print("--- Starting Flask Web Server ---")
    app.run(debug=True, use_reloader=False)

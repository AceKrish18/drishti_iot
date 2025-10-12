from flask import Flask, render_template, request, jsonify
import threading
import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
import playsound
import tempfile
import os
import re
import sys
import test  # Your YOLO detection module

app = Flask(__name__)

# Global variables
voice_thread = None
detection_thread = None
latest_qa = {"question": None, "answer": None}
stop_currency_flag = False  # For currency detection

# --- Gemini API Setup ---
API_KEY = "AIzaSyAlUPOxXg_h2Cp_F26zqq7kV8reYbNmceE"

def verify_api_key():
    if not API_KEY or API_KEY == "YOUR_VALID_GEMINI_API_KEY":
        print("API key not set.")
        sys.exit(1)
    try:
        genai.configure(api_key=API_KEY)
        models = [m for m in genai.list_models()]
        if not models:
            raise Exception("No models found, key might be restricted.")
        print("Gemini API key verified.")
    except Exception as e:
        print(f"API key invalid: {e}")
        sys.exit(1)

# --- Voice Assistant Functions ---
def speak(text):
    if text:
        clean_text = re.sub(r'[*_`]', '', text).replace('\n', '. ')
        tts = gTTS(clean_text, lang='en')
        tmp_file = os.path.join(tempfile.gettempdir(), "temp_speech.mp3")
        tts.save(tmp_file)
        playsound.playsound(tmp_file)
        os.remove(tmp_file)

def listen_to_voice(duration=5):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=duration, phrase_time_limit=duration)
        except sr.WaitTimeoutError:
            print("No speech detected within timeout.")
            return None
    try:
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Could not understand audio.")
        return None
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return None


def ask_gemini(prompt):
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel("gemini-2.5-pro")
        response = model.generate_content(f"Answer concisely: {prompt}")
        return response.text
    except Exception as e:
        return f"Error: {e}"

def run_voice_assistant(qa_storage):
    user_input = listen_to_voice(duration=5)  # Only listen for 5 seconds
    if not user_input:
        qa_storage['question'] = "No input detected."
        qa_storage['answer'] = "Listening stopped."
        return

    qa_storage['question'] = user_input
    qa_storage['answer'] = "Thinking..."

    if user_input.lower() in ["exit", "quit", "stop"]:
        speak("Goodbye!")
        qa_storage['question'] = "Exiting..."
        qa_storage['answer'] = "Assistant stopped."
        return

    answer = ask_gemini(user_input)
    qa_storage['answer'] = answer
    speak(answer)


# --- Flask Routes ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start_voice_assistant")
def start_voice_assistant():
    global voice_thread
    if voice_thread is None or not voice_thread.is_alive():
        voice_thread = threading.Thread(target=run_voice_assistant, args=(latest_qa,))
        voice_thread.daemon = True
        voice_thread.start()
        return jsonify({"status": "Voice assistant started."})
    return jsonify({"status": "Voice assistant already running."})

@app.route("/get_latest_qa")
def get_latest_qa():
    return jsonify(latest_qa)

# --- YOLO Detection Routes ---
@app.route("/run_detection_page")
def run_detection_page():
    """Serve YOLO page and start detection"""
    global detection_thread
    if detection_thread is None or not detection_thread.is_alive():
        detection_thread = threading.Thread(target=test.start_detection)
        detection_thread.daemon = True
        detection_thread.start()
    return render_template("index2.html")

@app.route("/start_detection", methods=["POST"])
def start_detection():
    global detection_thread
    if detection_thread is None or not detection_thread.is_alive():
        detection_thread = threading.Thread(target=test.start_detection)
        detection_thread.daemon = True
        detection_thread.start()
        return jsonify({"status": "Detection started"})
    return jsonify({"status": "Detection already running"})

@app.route("/stop_detection", methods=["POST"])
def stop_detection():
    test.stop_detection()
    return jsonify({"status": "Detection stopped"})

# --- Currency Detection Routes ---
@app.route("/currency_detection")
def currency_detection_page():
    """Serve currency detection page and start detection thread"""
    global detection_thread, stop_currency_flag
    stop_currency_flag = False  # Reset flag on page load

    if detection_thread is None or not detection_thread.is_alive():
        from notes import main as currency_main
        detection_thread = threading.Thread(target=currency_main, args=())
        detection_thread.daemon = True
        detection_thread.start()
    return render_template("index3.html")

@app.route("/start_currency_detection", methods=["POST"])
def start_currency_detection():
    global detection_thread
    if detection_thread is None or not detection_thread.is_alive():
        import notes
        detection_thread = threading.Thread(target=notes.main)
        detection_thread.daemon = True
        detection_thread.start()
        return jsonify({"status": "Currency detection started"})
    return jsonify({"status": "Detection already running"})

# --- At top ---
stop_currency_flag = False  # Shared flag

# --- Stop route ---
@app.route("/stop_currency_detection", methods=["POST"])
def stop_currency_detection():
    import notes  # make sure this import is the same module running detection
    notes.stop_currency_flag = True  # set the flag in notes.py
    return jsonify({"status": "Currency detection stopped"})


if __name__ == "__main__":
    verify_api_key()
    app.run(debug=True, use_reloader=False)

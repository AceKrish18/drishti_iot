import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
import playsound
import tempfile
import os
import re

# --- Configure your Gemini API key ---
# PASTE YOUR KNOWN-GOOD API KEY HERE. This is the one that
# passed the test in 'verify_key.py'.
api_key = "YOUR_VALID_GEMINI_API_KEY"

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
        # --- THIS IS THE KEY CHANGE ---
        # Explicitly configure the client right before making the call.
        # This overrides any potential environment variables or cached configs.
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(f"Answer concisely: {prompt}")
        return response.text
    except Exception as e:
        # Provide a more detailed error message on the frontend
        print(f"Error during Gemini API call: {e}")
        return f"An error occurred with the API: {str(e)}"

def run_voice_assistant(qa_storage):
    """
    The main loop for the voice assistant.
    It updates a shared dictionary (qa_storage) with the latest Q&A.
    """
    print("Voice assistant thread started. Say 'exit' to quit.")
    while True:
        user_input = listen_to_voice()
        if not user_input:
            continue

        qa_storage['question'] = user_input
        qa_storage['answer'] = "Thinking..."

        if user_input.lower() in ["exit", "quit", "stop"]:
            print("Exiting voice assistant...")
            speak("Goodbye!")
            qa_storage['question'] = "Exiting..."
            qa_storage['answer'] = "Assistant stopped."
            break
        
        answer = ask_gemini(user_input)
        print("\nGemini:", answer)
        
        qa_storage['answer'] = answer
        
        speak(answer)

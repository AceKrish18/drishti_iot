import time
import cv2
import threading
import pygame
import os
from gtts import gTTS
from inference_sdk import InferenceHTTPClient
from app2 import stop_currency_flag  # Import shared stop flag from Flask app

speak_lock = threading.Lock()

def speak(text):
    if speak_lock.acquire(blocking=False):
        audio_file = "temp_speech.mp3"
        try:
            tts = gTTS(text=text, lang='hi')
            tts.save(audio_file)
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        finally:
            pygame.mixer.music.unload()
            speak_lock.release()
            if os.path.exists(audio_file):
                os.remove(audio_file)

def main():
    pygame.mixer.init()

    CLIENT = InferenceHTTPClient(
        api_url="https://detect.roboflow.com",
        api_key="PceHEiXl1cNBewrgTXGu"
    )
    MODEL_ID = "currency-detection-cgpjn/2"
    CONFIDENCE_THRESHOLD = 0.5

    translation_dict = {
        "10": "दस रुपये", "20": "बीस रुपये", "50": "पचास रुपये",
        "100": "सौ रुपये", "200": "दो सौ रुपये", "500": "पांच सौ रुपये"
    }

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("Error: Cannot open webcam")
        return

    prev_time = 0
    last_api_call_time = 0
    api_call_interval = 5  # seconds

    while True:
        if stop_currency_flag:  # Stop flag from Flask
            print("Currency detection stopped.")
            break

        ret, frame = cap.read()
        if not ret:
            break

        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if prev_time else 0
        prev_time = curr_time

        display_frame = frame.copy()
        cv2.putText(display_frame, f'FPS: {fps:.2f}', (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow('Indian Currency Detection (Roboflow API)', display_frame)

        # API call at interval
        if curr_time - last_api_call_time > api_call_interval:
            last_api_call_time = curr_time
            try:
                result = CLIENT.infer(frame, model_id=MODEL_ID)
                detected_names = {p['class'] for p in result['predictions']
                                  if p['confidence'] >= CONFIDENCE_THRESHOLD}

                if detected_names:
                    hindi_names = [translation_dict.get(name, name) for name in detected_names]
                    text_to_speak = "मैंने देखा: " + ", ".join(hindi_names)
                    print(f"[{time.strftime('%H:%M:%S')}] Detected: {', '.join(detected_names)}")
                    threading.Thread(target=speak, args=(text_to_speak,), daemon=True).start()

            except Exception as e:
                print(f"API Error: {e}")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()

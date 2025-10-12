import cv2
import torch
from ultralytics import YOLO
import time
import threading
from gtts import gTTS
import os
import pygame

# Global variables
detection_thread = None
stop_flag = threading.Event()
speak_lock = threading.Lock()

# Initialize pygame mixer once globally
pygame.mixer.init()

# Full translation dictionary
translation_dict = {
    "person": "व्यक्ति", "bicycle": "साइकिल", "car": "गाड़ी", "motorcycle": "मोटरसाइकिल",
    "airplane": "हवाई जहाज", "bus": "बस", "train": "रेलगाड़ी", "truck": "ट्रक", "boat": "नाव",
    "traffic light": "यातायात बत्ती", "fire hydrant": "दमकल", "stop sign": "स्टॉप साइन",
    "parking meter": "पार्किंग मीटर", "bench": "बेंच", "bird": "पक्षी", "cat": "बिल्ली",
    "dog": "कुत्ता", "horse": "घोड़ा", "sheep": "भेड़", "cow": "गाय", "elephant": "हाथी",
    "bear": "भालू", "zebra": "ज़ेबरा", "giraffe": "जिराफ़", "backpack": "बस्ता", "umbrella": "छाता",
    "handbag": "हैंडबैग", "tie": "टाई", "suitcase": "सूटकेस", "frisbee": "फ्रिसबी", "skis": "स्की",
    "snowboard": "स्नोबोर्ड", "sports ball": "गेंद", "kite": "पतंग", "baseball bat": "बल्ला",
    "baseball glove": "दस्ताना", "skateboard": "स्केटबोर्ड", "surfboard": "सर्फबोर्ड",
    "tennis racket": "टेनिस रैकेट", "bottle": "बोतल", "wine glass": "शराब का गिलास", "cup": "कप",
    "fork": "कांटा", "knife": "चाकू", "spoon": "चम्मच", "bowl": "कटोरा", "banana": "केला",
    "apple": "सेब", "sandwich": "सैंडविच", "orange": "संतरा", "broccoli": "ब्रोकोली",
    "carrot": "गाजर", "hot dog": "हॉट डॉग", "pizza": "पिज्जा", "donut": "डोनट", "cake": "केक",
    "chair": "कुर्सी", "couch": "सोफ़ा", "potted plant": "पौधा", "bed": "बिस्तर",
    "dining table": "डाइनिंग टेबल", "toilet": "शौचालय", "tv": "टीवी", "laptop": "लैपटॉप",
    "mouse": "माउस", "remote": "रिमोट", "keyboard": "कीबोर्ड", "cell phone": "मोबाइल फोन",
    "microwave": "माइक्रोवेव", "oven": "ओवन", "toaster": "टोस्टर", "sink": "सिंक",
    "refrigerator": "फ्रिज", "book": "किताब", "clock": "घड़ी", "vase": "गुलदस्ता",
    "scissors": "कैंची", "teddy bear": "टेडी बेयर", "hair drier": "हेयर ड्रायर", "toothbrush": "टूथब्रश"
}

def speak(text):
    """Thread-safe Hindi speech generation."""
    with speak_lock:
        audio_file = "temp_speech.mp3"
        try:
            tts = gTTS(text=text, lang='hi')
            tts.save(audio_file)
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        except Exception as e:
            print(f"Error in speak: {e}")
        finally:
            pygame.mixer.music.unload()
            if os.path.exists(audio_file):
                try:
                    os.remove(audio_file)
                except OSError as e:
                    print(f"Error removing audio file: {e}")

def yolo_detection():
    """Main YOLO detection loop."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    model = YOLO('yolov8n.pt')
    model.to(device)

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("Error: Cannot open webcam")
        return

    prev_time = 0
    last_speech_time = 0
    speech_interval = 5

    while not stop_flag.is_set():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame, stream=True, verbose=False)
        for r in results:
            annotated_frame = r.plot()
            curr_time = time.time()
            fps = 1 / (curr_time - prev_time) if prev_time else 0
            prev_time = curr_time
            cv2.putText(annotated_frame, f'FPS: {fps:.2f}', (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow('YOLOv8 Hindi Object Detection', annotated_frame)

            if curr_time - last_speech_time > speech_interval:
                last_speech_time = curr_time
                detected_hindi_names = {translation_dict.get(model.names[int(box.cls[0])], 
                                                            model.names[int(box.cls[0])])
                                        for box in r.boxes}
                if detected_hindi_names:
                    text_to_speak = "मैंने देखा: " + ", ".join(detected_hindi_names)
                    print(f"[{time.strftime('%H:%M:%S')}] Queuing speech: {text_to_speak}")
                    threading.Thread(target=speak, args=(text_to_speak,), daemon=True).start()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            stop_flag.set()
            break

    cap.release()
    cv2.destroyAllWindows()
    print("YOLO detection stopped.")

def start_detection():
    """Starts YOLO detection in a separate thread."""
    global detection_thread, stop_flag
    stop_flag.clear()
    if detection_thread is None or not detection_thread.is_alive():
        detection_thread = threading.Thread(target=yolo_detection)
        detection_thread.start()
        return "Detection started"
    return "Detection already running"

def stop_detection():
    """Stops YOLO detection."""
    global stop_flag
    stop_flag.set()
    if detection_thread is not None:
        detection_thread.join()
    return "Detection stopped"

if __name__ == '__main__':
    start_detection()

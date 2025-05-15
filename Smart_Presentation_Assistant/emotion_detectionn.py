import cv2
from deepface import DeepFace
import numpy as np

def detect_emotion(frame):
    try:
        result = DeepFace.analyze(
            img_path=frame,
            actions=['emotion'],
            enforce_detection=False
        )
        dominant_emotion = result[0]['dominant_emotion'].lower()
        if dominant_emotion in ['happy', 'surprise', 'neutral']:
            emotion = 'happy'
        elif dominant_emotion in ['sad', 'angry', 'fear']:
            emotion = 'sad'
        else:
            emotion = 'happy'
        print(f"Detected emotion: {emotion}")
        return emotion
    except Exception as e:
        print(f"Emotion detection error: {e}")
        return 'happy'

def handle_emotion_pause(frame, emotion, slideshow_active):
    if emotion == 'sad' and slideshow_active:
        status_text = "Paused: Sad emotion detected"
        color = (0, 0, 255)
        cv2.destroyWindow("Slideshow")
        slideshow_active = False
    else:
        status_text = f"Emotion: Happy"
        color = (0, 255, 0)
    cv2.putText(frame, status_text, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    return frame, slideshow_active
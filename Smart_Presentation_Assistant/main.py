import cv2
import sys
import os
import platform
import time
import numpy as np
import mediapipe as mp

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
print("Importing modules...")
try:
    from camera_calibration import calibrate_camera, undistort_frame
    from face_auth import authenticate_presenter, display_authentication_status
    from gesture_controll import detect_gesture, control_presentation, display_gesture_feedback, init_voice_engine
    from emotion_detectionn import detect_emotion, handle_emotion_pause
    from ui import create_ui_overlay
    print("Modules imported successfully")
except Exception as e:
    print(f"Failed to import modules: {e}")
    sys.exit(1)

def load_slide_images(images_dir):
    print(f"Loading slide images from {images_dir}...")
    slide_images = []
    for i in range(1, 10):
        img_path = os.path.join(images_dir, f"{i}.jpg")
        if not os.path.exists(img_path):
            print(f"Error: {img_path} not found.")
            return []
        img = cv2.imread(img_path)
        if img is None:
            print(f"Error: Failed to load {img_path}.")
            return []
        slide_images.append(img)
    print(f"Loaded {len(slide_images)} slide images.")
    return slide_images

def main():
    images_dir = os.path.abspath("images")
    reference_path = os.path.abspath("reference.jpg")
    print(f"Checking files: images_dir={images_dir}, reference={reference_path}")
    if not os.path.exists(images_dir):
        print(f"Error: Images directory {images_dir} not found.")
        sys.exit(1)
    if not os.path.exists(reference_path):
        print(f"Error: {reference_path} not found.")
        sys.exit(1)
    
    slide_images = load_slide_images(images_dir)
    if not slide_images:
        print("Error: No valid slide images loaded.")
        sys.exit(1)
    
    print("Initializing voice engine...")
    if not init_voice_engine():
        print("Proceeding without voice feedback.")
    
    print("Opening webcam...")
    cap = None
    for index in range(3):
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        if cap.isOpened():
            print(f"Webcam opened at index {index}")
            break
        print(f"Webcam index {index} failed")
        cap.release()
    if not cap or not cap.isOpened():
        print("Error: Could not open webcam after 3 attempts.")
        sys.exit(1)
    
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.3)
    calibration_data = None
    presenter_authenticated = False
    presenter_name = "Presenter"
    current_slide = 0
    slideshow_active = False
    auth_attempts = 0
    max_auth_attempts = 10
    
    print("Starting main loop...")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break
        
        frame = undistort_frame(frame, calibration_data)
        
        if not presenter_authenticated and auth_attempts < max_auth_attempts:
            presenter_authenticated = authenticate_presenter(frame, reference_path, presenter_name)
            auth_attempts += 1
            frame = create_ui_overlay(frame, presenter_name, presenter_authenticated, None, 'happy', {})
            if auth_attempts == max_auth_attempts:
                print("Max authentication attempts reached. Proceeding without authentication.")
                presenter_authenticated = True  # Fallback
        else:
            gesture, frame, debug_info = detect_gesture(frame, hands)
            emotion = detect_emotion(frame)
            frame, slideshow_active = handle_emotion_pause(frame, emotion, slideshow_active)
            if emotion != 'sad':
                current_slide, slideshow_active = control_presentation(gesture, slide_images, current_slide, slideshow_active)
            frame = create_ui_overlay(frame, presenter_name, presenter_authenticated, gesture, emotion, debug_info)
        
        cv2.imshow("Presentation Assistant", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    print("Cleaning up...")
    cap.release()
    cv2.destroyAllWindows()
    hands.close()
    cv2.destroyWindow("Slideshow")

if __name__ == "__main__":
    print("Starting main.py...")
    main()
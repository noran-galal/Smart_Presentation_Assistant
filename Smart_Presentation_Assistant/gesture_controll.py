import cv2
import mediapipe as mp
import numpy as np
import pyttsx3
import platform
import time

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

tts_engine = None
def init_voice_engine():
    global tts_engine
    driver = 'sapi5' if platform.system() == 'Windows' else 'espeak' if platform.system() == 'Linux' else 'nsss'
    for attempt in range(3):
        try:
            tts_engine = pyttsx3.init(driver)
            tts_engine.setProperty('rate', 120)
            voices = tts_engine.getProperty('voices')
            print("Available voices:", [v.id for v in voices])
            if voices:
                tts_engine.setProperty('voice', voices[0].id)
            print(f"Voice engine initialized with {driver} (attempt {attempt+1})")
            print(f"Voice rate: {tts_engine.getProperty('rate')}, Voice ID: {tts_engine.getProperty('voice')}")
            tts_engine.say("Voice feedback test")
            tts_engine.runAndWait()
            print("Test voice played successfully")
            return True
        except Exception as e:
            print(f"Voice init attempt {attempt+1} failed: {e}")
            time.sleep(1)
    print("Failed to initialize voice engine after 3 attempts")
    tts_engine = None
    return False

def voice_feedback(message):
    if tts_engine is None:
        print(f"Voice feedback unavailable: Engine not initialized. Fallback: {message}")
        return
    try:
        tts_engine.say(message)
        tts_engine.runAndWait()
        print(f"Voice feedback: {message}")
    except Exception as e:
        print(f"Voice feedback error: {e}. Fallback: {message}")

def detect_gesture(frame, hands):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    print(f"Hand detection: {'Hands detected' if results.multi_hand_landmarks else 'No hands detected'}")
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            gesture, debug_info = classify_gesture(hand_landmarks)
            return gesture, frame, debug_info
    return None, frame, {}

def classify_gesture(hand_landmarks):
    landmarks = hand_landmarks.landmark
    wrist = landmarks[0]
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    index_mcp = landmarks[5]
    middle_tip = landmarks[12]
    middle_mcp = landmarks[9]
    ring_tip = landmarks[16]
    ring_mcp = landmarks[13]
    pinky_tip = landmarks[20]
    pinky_mcp = landmarks[17]
    
    fingers = [
        (index_tip.y < index_mcp.y, "Index"),
        (middle_tip.y < middle_mcp.y, "Middle"),
        (ring_tip.y < ring_mcp.y, "Ring"),
        (pinky_tip.y < pinky_mcp.y, "Pinky")
    ]
    extended_fingers = sum(1 for extended, _ in fingers if extended)
    finger_spread = abs(index_tip.x - middle_tip.x) if extended_fingers >= 1 else 0.0
    thumb_wrist_y_diff = thumb_tip.y - wrist.y
    
    debug_info = {
        'extended_fingers': extended_fingers,
        'thumb_wrist_y_diff': thumb_wrist_y_diff,
        'finger_spread': finger_spread,
        'finger_states': ', '.join(f"{name}: {'Extended' if ext else 'Curled'}" for ext, name in fingers)
    }
    print(f"Wrist: ({wrist.x:.2f}, {wrist.y:.2f})")
    print(f"Thumb Tip: ({thumb_tip.x:.2f}, {thumb_tip.y:.2f})")
    print(f"Extended Fingers: {extended_fingers}/4")
    print(f"Finger States: {debug_info['finger_states']}")
    print(f"Thumb-Wrist Y Diff: {thumb_wrist_y_diff:.2f}")
    print(f"Finger Spread: {finger_spread:.2f}")
    
    if extended_fingers >= 3 and finger_spread > 0.03:
        print("Detected: End (Stop)")
        voice_feedback("Presentation ended")
        return "End", debug_info
    elif extended_fingers == 2 and fingers[0][0] and fingers[1][0] and not fingers[2][0] and not fingers[3][0]:
        print("Detected: Start (Peace)")
        voice_feedback("Presentation started")
        return "Start", debug_info
    elif thumb_wrist_y_diff < -0.05 and extended_fingers == 0:
        print("Detected: Previous (Like)")
        voice_feedback("Previous slide activated")
        return "Previous", debug_info
    elif thumb_wrist_y_diff > 0.05 and extended_fingers == 0:
        print("Detected: Next (Dislike)")
        voice_feedback("Next slide activated")
        return "Next", debug_info
    print(f"No gesture detected. Reasons: Extended Fingers={extended_fingers}, Finger Spread={finger_spread:.2f}")
    voice_feedback("No gesture detected")
    return None, debug_info

def control_presentation(gesture, slide_images, current_slide, slideshow_active):
    if not gesture:
        return current_slide, slideshow_active
    
    if gesture == "Start":
        slideshow_active = True
        current_slide = 1
        if slide_images:
            cv2.imshow("Slideshow", slide_images[0])
        voice_feedback(f"Showing slide {current_slide}")
    elif gesture == "Previous" and slideshow_active and current_slide > 1:
        current_slide -= 1
        cv2.imshow("Slideshow", slide_images[current_slide - 1])
        voice_feedback(f"Showing slide {current_slide}")
    elif gesture == "Next" and slideshow_active and current_slide < len(slide_images):
        current_slide += 1
        cv2.imshow("Slideshow", slide_images[current_slide - 1])
        voice_feedback(f"Showing slide {current_slide}")
    elif gesture == "End":
        slideshow_active = False
        current_slide = 0
        cv2.destroyWindow("Slideshow")
    
    return current_slide, slideshow_active

def display_gesture_feedback(frame, gesture, debug_info):
    y_offset = 60
    if gesture:
        cv2.putText(frame, f"Gesture: {gesture} ✓", (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        y_offset += 30
    instructions = [
        "Previous: Thumbs up (like)",
        "Next: Thumbs down (dislike)",
        "Start: Peace sign (index & middle extended)",
        "End: Open palm facing webcam (stop)"
    ]
    debug_texts = [
        f"Ext. Fingers: {debug_info.get('extended_fingers', 0)}/4",
        f"Thumb Y Diff: {debug_info.get('thumb_wrist_y_diff', 0.0):.2f}",
        f"Finger Spread: {debug_info.get('finger_spread', 0.0):.2f}"
    ]
    for i, instruction in enumerate(instructions):
        cv2.putText(frame, instruction, (10, y_offset + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    for i, text in enumerate(debug_texts):
        cv2.putText(frame, text, (10, y_offset + (len(instructions) + i) * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    return frame

if __name__ == "__main__":
    init_voice_engine()
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        exit()
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.3)
    slide_images = [cv2.imread(f"images/{i}.jpg") for i in range(1, 10)]
    current_slide = 0
    slideshow_active = False
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break
        gesture, frame, debug_info = detect_gesture(frame, hands)
        frame = display_gesture_feedback(frame, gesture, debug_info)
        current_slide, slideshow_active = control_presentation(gesture, slide_images, current_slide, slideshow_active)
        cv2.imshow("Gesture Control", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    hands.close()
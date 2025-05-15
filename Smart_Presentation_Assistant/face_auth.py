import cv2
import os
from deepface import DeepFace
import numpy as np

def authenticate_presenter(frame, reference_image_path, presenter_name):
    if not os.path.exists(reference_image_path):
        print(f"Error: Reference image {reference_image_path} not found.")
        return False
    
    try:
        temp_frame_path = "temp_frame.jpg"
        cv2.imwrite(temp_frame_path, frame)
        result = DeepFace.verify(
            img1_path=temp_frame_path,
            img2_path=reference_image_path,
            model_name="VGG-Face",
            distance_metric="cosine",
            enforce_detection=False
        )
        os.remove(temp_frame_path)
        is_authenticated = result["verified"]
        print(f"Presenter {presenter_name} {'authenticated successfully' if is_authenticated else 'authentication failed'}.")
        return is_authenticated
    except Exception as e:
        print(f"Authentication error: {e}")
        return False

def display_authentication_status(frame, is_authenticated, presenter_name):
    status_text = f"Presenter: {presenter_name} ({'Authenticated' if is_authenticated else 'Not Authenticated'})"
    color = (0, 255, 0) if is_authenticated else (0, 0, 255)
    cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    return frame
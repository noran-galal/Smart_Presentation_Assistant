import cv2

def create_ui_overlay(frame, presenter_name, is_authenticated, gesture, emotion, debug_info):
    status_text = f"Presenter: {presenter_name} ({'Authenticated' if is_authenticated else 'Not Authenticated'})"
    color = (0, 255, 0) if is_authenticated else (0, 0, 255)
    cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    
    y_offset = 60
    if gesture:
        cv2.putText(frame, f"Gesture: {gesture} ✓", (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        y_offset += 30
    
    if emotion == 'sad':
        cv2.putText(frame, "Paused: Sad emotion detected", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    else:
        cv2.putText(frame, "Emotion: Happy", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
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
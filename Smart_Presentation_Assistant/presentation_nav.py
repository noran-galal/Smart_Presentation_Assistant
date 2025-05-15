import pyautogui
from pptx import Presentation

def control_presentation(gesture):
    pyautogui.FAILSAFE = True
    if gesture == "Next":
        pyautogui.press("right")
    elif gesture == "Previous":
        pyautogui.press("left")
    elif gesture == "Start":
        pyautogui.press("f5")
    elif gesture == "End":
        pyautogui.press("esc")

def load_presentation(file_path):
    try:
        prs = Presentation(file_path)
        return prs
    except Exception as e:
        print(f"Error loading presentation: {e}")
        return None

if __name__ == "__main__":
    # Test with keyboard simulation
    control_presentation("Next") 
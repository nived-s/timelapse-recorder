import cv2
import numpy as np
import pyautogui
from PIL import Image

# Set recording options
output_file = "screen_record_raw.mp4"
fps = 10  # Record at 10 FPS for performance (or 30 if your system can handle it)
record_seconds = 300  # Record duration in seconds (e.g., 5 minutes)

# Load the custom cursor image
cursor_img = Image.open('resources/cursor.png')
# You can adjust the cursor size if needed
cursor_size = (24, 24)  # Standard cursor size
cursor_img = cursor_img.resize(cursor_size)

def draw_cursor(screenshot):
    # Convert screenshot to PIL Image if it's not already
    if isinstance(screenshot, np.ndarray):
        screenshot = Image.fromarray(screenshot)
    
    # Get current mouse position
    mouse_x, mouse_y = pyautogui.position()
    
    # Create a copy of the screenshot
    result = screenshot.copy()
    
    # Paste the cursor at the current mouse position
    # Adjust position so cursor point matches mouse position (you might need to adjust these offsets)
    cursor_x = mouse_x - cursor_size[0]//2
    cursor_y = mouse_y - cursor_size[1]//2
    
    # Paste the cursor with transparency
    result.paste(cursor_img, (cursor_x, cursor_y), cursor_img)
    
    return result

screen_size = pyautogui.size()
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(output_file, fourcc, fps, screen_size)

print("Recording started...")

for _ in range(int(fps * record_seconds)):
    # Capture screenshot
    img = pyautogui.screenshot()
    
    # Draw custom cursor
    img = draw_cursor(img)
    
    # Convert to numpy array and change color space for OpenCV
    frame = np.array(img)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
    # Write frame to video
    out.write(frame)

out.release()
print("Recording complete.")

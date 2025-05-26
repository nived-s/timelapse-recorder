import cv2
import numpy as np
import pyautogui

# Set recording options
output_file = "screen_record_raw.mp4"
fps = 10  # Record at 10 FPS for performance (or 30 if your system can handle it)
record_seconds = 300  # Record duration in seconds (e.g., 5 minutes)

screen_size = pyautogui.size()
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(output_file, fourcc, fps, screen_size)

print("Recording started...")
for _ in range(int(fps * record_seconds)):
    img = pyautogui.screenshot()
    frame = np.array(img)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    out.write(frame)

out.release()
print("Recording complete.")

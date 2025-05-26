import cv2
import numpy as np
import pyautogui
from PIL import Image
import threading
import time


class ScreenRecorder:
    def __init__(self, output_file="screen_record_raw.mp4", fps=10):
        self.output_file = output_file
        self.fps = fps
        self.recording = False
        self.thread = None

        # Load the custom cursor image
        self.cursor_img = Image.open('resources/cursor.png')
        self.cursor_size = (24, 24)  # Standard cursor size
        self.cursor_img = self.cursor_img.resize(self.cursor_size)

        # Initialize video writer
        self.screen_size = pyautogui.size()
        self.fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.out = None

    def draw_cursor(self, screenshot):
        # Convert screenshot to PIL Image if it's not already
        if isinstance(screenshot, np.ndarray):
            screenshot = Image.fromarray(screenshot)

        # Get current mouse position
        mouse_x, mouse_y = pyautogui.position()

        # Create a copy of the screenshot
        result = screenshot.copy()

        # Paste the cursor at the current mouse position
        cursor_x = mouse_x - self.cursor_size[0]//2
        cursor_y = mouse_y - self.cursor_size[1]//2

        # Paste the cursor with transparency
        result.paste(self.cursor_img, (cursor_x, cursor_y), self.cursor_img)

        return result

    def record_loop(self):
        self.out = cv2.VideoWriter(
            self.output_file, self.fourcc, self.fps, self.screen_size)
        
        frame_duration = 1.0 / self.fps  # Time per frame in seconds
        next_frame_time = time.time()

        while self.recording:
            current_time = time.time()
            
            # Capture screenshot
            img = pyautogui.screenshot()
            
            # Draw custom cursor
            img = self.draw_cursor(img)
            
            # Convert to numpy array and change color space for OpenCV
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Write frame to video
            self.out.write(frame)
            
            # Calculate sleep time for next frame
            next_frame_time += frame_duration
            sleep_time = next_frame_time - time.time()
            
            # Only sleep if we're ahead of schedule
            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                # We're behind schedule, update next_frame_time
                next_frame_time = time.time()

    def start(self):
        if not self.recording:
            self.recording = True
            self.thread = threading.Thread(target=self.record_loop)
            self.thread.start()

    def stop(self):
        if self.recording:
            self.recording = False
            if self.thread:
                self.thread.join()
            if self.out:
                self.out.release()


# Example of using the ScreenRecorder class
if __name__ == "__main__":
    recorder = ScreenRecorder(output_file="my_recording.mp4", fps=15)
    try:
        recorder.start()
        print("Recording... Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        recorder.stop()
        print("Recording stopped.")

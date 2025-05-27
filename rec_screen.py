import cv2
import numpy as np
import pyautogui
from PIL import Image
import threading
import time
import win32gui
import win32api


class ScreenRecorder: 
    def __init__(self, output_file="screen_record_raw.mp4", fps=10, capture_region=None):
        # Store capture region
        self.capture_region = capture_region or {
            'left': 0, 
            'top': 0,
            'width': win32api.GetSystemMetrics(0),  # screen width
            'height': win32api.GetSystemMetrics(1)  # screen height
        }
        
        self.output_file = output_file
        self.fps = fps
        self.recording = False
        self.thread = None

        # Load the custom cursor image
        self.cursor_img = Image.open('resources/cursor.png')
        self.cursor_size = (24, 24)  # Standard cursor size
        self.cursor_img = self.cursor_img.resize(self.cursor_size)

        # Standard HD output size
        self.output_size = (1920, 1080)
        self.fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.out = None 
        
    def draw_cursor(self, img):
        """Draw cursor on the image with proper position calculation"""
        try:
            # Get current cursor position as tuple (x, y)
            cursor_pos = win32gui.GetCursorPos()
            
            # Calculate cursor position relative to capture region
            cursor_x = cursor_pos[0] - self.capture_region['left']
            cursor_y = cursor_pos[1] - self.capture_region['top']
            
            # Check if cursor is within capture region
            if (0 <= cursor_x < self.capture_region['width'] and 
                0 <= cursor_y < self.capture_region['height']):
                
                # Create a copy of the image
                result = img.copy()
                # Paste cursor at the adjusted position
                result.paste(self.cursor_img, (int(cursor_x), int(cursor_y)), self.cursor_img)
                return result
            
            return img  # Return original image if cursor is outside
            
        except Exception as e:
            print(f"Error drawing cursor: {e}")
            return img  # Return original image if there's an error
    
    def record_loop(self):
        self.out = cv2.VideoWriter(
            self.output_file, self.fourcc, self.fps, self.output_size)

        frame_duration = 1.0 / self.fps  # Time per frame in seconds
        next_frame_time = time.time()

        while self.recording:
            current_time = time.time()
            # Use self.capture_region instead of self.region
            img = pyautogui.screenshot(region=(
                self.capture_region['left'],
                self.capture_region['top'],
                self.capture_region['width'],
                self.capture_region['height']
            ))

            # Draw custom cursor (adjusted for region)
            img = self.draw_cursor(img)

            # Resize to 1920x1080
            img = img.resize(self.output_size, Image.Resampling.LANCZOS)

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

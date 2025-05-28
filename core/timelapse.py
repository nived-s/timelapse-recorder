import cv2
import os
import mss
import numpy as np
import time
import win32gui
from PIL import Image


class TimeLapseConverter:
    def __init__(self, speed_factor=10):
        self.speed_factor = speed_factor

    def convert(self, input_file, output_file):
        """
        Convert a video to timelapse by keeping 1 frame out of every N frames
        where N is the speed_factor.
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")

        cap = cv2.VideoCapture(input_file)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

        frame_count = 0
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                # Keep only 1 out of every N frames
                if frame_count % self.speed_factor == 0:
                    out.write(frame)
                frame_count += 1
        finally:
            cap.release()
            out.release()

        if frame_count == 0:
            raise RuntimeError("No frames were read from the input file")

        return output_file


class TimeLapseScreenRecorder:
    """
    Records a timelapse of the screen by capturing frames at set intervals and writing them to a video file.
    - interval_seconds: Time between each frame capture (higher = faster timelapse effect)
    - output_fps: Playback speed of the output video (e.g., 30 for smooth playback)
    - monitor: Which monitor to record (1 = primary)
    """

    def __init__(self, interval_seconds=2, output_fps=30, monitor=1):
        self.interval_seconds = interval_seconds
        self.output_fps = output_fps
        self.monitor = monitor  # 1 for primary monitor
        self._recording = False

    def record(self, output_file):
        with mss.mss() as sct:
            if self.monitor >= len(sct.monitors):
                raise ValueError(
                    f"Monitor index {self.monitor} is out of range. Available monitors: {len(sct.monitors)-1}")
            monitor = sct.monitors[self.monitor]
            width = monitor['width']
            height = monitor['height']
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out = cv2.VideoWriter(output_file, fourcc,
                                  self.output_fps, (width, height))
            if not out.isOpened():
                raise IOError(
                    f"Could not open output file for writing: {output_file}")

            self._recording = True
            frame_count = 0
            # Load cursor image
            cursor_img = Image.open('resources/cursor.png').resize((24, 24))
            try:
                while self._recording:
                    try:
                        img = np.array(sct.grab(monitor))
                        # Convert to PIL Image for cursor drawing
                        pil_img = Image.fromarray(
                            cv2.cvtColor(img, cv2.COLOR_BGRA2RGB))
                        # Get cursor position
                        cursor_pos = win32gui.GetCursorPos()
                        cursor_x = cursor_pos[0] - monitor['left']
                        cursor_y = cursor_pos[1] - monitor['top']
                        # Draw cursor if within bounds
                        if (0 <= cursor_x < width and 0 <= cursor_y < height):
                            pil_img.paste(
                                cursor_img, (int(cursor_x), int(cursor_y)), cursor_img)
                        # Convert back to OpenCV BGR
                        frame = cv2.cvtColor(
                            np.array(pil_img), cv2.COLOR_RGB2BGR)
                        out.write(frame)
                        frame_count += 1
                    except Exception as e:
                        print(f"[ERROR] Failed to capture or write frame: {e}")
                    time.sleep(self.interval_seconds)
            finally:
                out.release()
        video_length = frame_count / self.output_fps if self.output_fps else 0
        if frame_count == 0:
            print("[WARNING] No frames were captured. Output video may be empty.")

    def stop(self):
        self._recording = False


# Example usage
if __name__ == "__main__":
    # Example usage for screen timelapse recording
    recorder = TimeLapseScreenRecorder(
        interval_seconds=2, output_fps=30, monitor=1)
    recorder.record("timelapse_screen_output.mp4", duration_seconds=60)

    # Example usage for video file timelapse conversion
    # converter = TimeLapseConverter(speed_factor=10)
    # converter.convert("input.mp4", "timelapse_output.mp4")

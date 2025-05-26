import cv2
import os


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


# Example usage
if __name__ == "__main__":
    converter = TimeLapseConverter(speed_factor=10)
    converter.convert("input.mp4", "timelapse_output.mp4")

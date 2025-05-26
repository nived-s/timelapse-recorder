import cv2

input_file = "game_rec.mkv"
output_file = "timelapse_output.mp4"
speed_factor = 10  # Speed up 10x

cap = cv2.VideoCapture(input_file)
fps = cap.get(cv2.CAP_PROP_FPS)
width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break
    # Keep only 1 out of every N frames
    if frame_count % speed_factor == 0:
        out.write(frame)
    frame_count += 1

cap.release()
out.release()
print(f"Timelapse saved as {output_file}")

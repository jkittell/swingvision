import cv2

def extract_frames(video_path, fps=30):
    cap = cv2.VideoCapture(video_path)
    frames = []

    # Get the frame rate of the video
    frame_rate = int(cap.get(cv2.CAP_PROP_FPS))

    # Calculate the number of frames to skip to get to the desired frame rate
    frame_interval = int(frame_rate / fps)

    frame_count = 0

    while True:
        success, frame = cap.read()
        if not success:
            break
        # Extract frames at the specified frame rate
        if frame_count % frame_interval == 0:
            frames.append(frame)
        frame_count += 1

    cap.release()

    return frames
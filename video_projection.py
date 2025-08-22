kimport cv2
import numpy as np
import pyvirtualcam
import ctypes
from screeninfo import get_monitors

# DPI awareness
ctypes.windll.shcore.SetProcessDpiAwareness(1)

# Load video
video_path = "video2.mp4"
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("Unable to read the video.")
    exit()

# Get FPS
fps = cap.get(cv2.CAP_PROP_FPS)

# Monitors
monitors = get_monitors()
if len(monitors) < 3:
    print("At least three monitors are required.")
    exit()

# Monitor 3 (TV)
monitor_tv = monitors[2]
# Monitor 2 (OBS)
monitor_obs = monitors[1]

# Resize directly to screen resolution (fullscreen, aspect ratio preserved)
def resize_to_screen(img, monitor):
    screen_w, screen_h = monitor.width, monitor.height
    video_ratio = img.shape[1] / img.shape[0]
    screen_ratio = screen_w / screen_h

    if abs(video_ratio - screen_ratio) > 0.01:
        new_height = screen_h
        new_width = int(new_height * video_ratio)

        if new_width > screen_w:
            new_width = screen_w
            new_height = int(new_width / video_ratio)

        img = cv2.resize(img, (new_width, new_height))
    else:
        img = cv2.resize(img, (screen_w, screen_h))

    return img

# Initialize OBS camera
ret, frame = cap.read()
if not ret:
    print("Unable to read the first frame.")
    exit()

# Set up OBS virtual camera
obs_width = 1920
obs_height = 1080
cam = pyvirtualcam.Camera(width=obs_width, height=obs_height, fps=30, fmt=pyvirtualcam.PixelFormat.BGR)

# Set up OpenCV window for the third monitor (TV)
cv2.namedWindow("TV Display", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("TV Display", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
cv2.moveWindow("TV Display", monitor_tv.x, monitor_tv.y)

# Display loop
while True:
    ret, frame = cap.read()
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Restart the video if it's over
        continue

    # Direct TV with OpenCV (Display on TV screen)
    frame_resized_tv = resize_to_screen(frame, monitor_tv)
    cv2.imshow("TV Display", frame_resized_tv)  # OpenCV window to display the video

    # OBS (mirror video for virtual camera)
    mirror = cv2.flip(frame, 1)
    frame_resized_obs = resize_to_screen(mirror, monitor_obs)

    # Ensure that the OBS frame is resized to 1920x1080
    frame_resized_obs = cv2.resize(frame_resized_obs, (obs_width, obs_height))

    # Send to OBS Virtual Camera
    cam.send(frame_resized_obs)

    # Handle video FPS timing to avoid skipping frames
    key = cv2.waitKey(int(1000 / fps))  # Control frame rate timing

    # Exit if user presses 'q'
    if key == ord('q'):
        break

cap.release()
cam.close()
cv2.destroyAllWindows()

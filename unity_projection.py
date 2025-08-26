import tkinter as tk
from PIL import Image, ImageTk
from screeninfo import get_monitors
import ctypes
import numpy as np
import cv2
import pyvirtualcam
import argparse


ctypes.windll.shcore.SetProcessDpiAwareness(1)


parser = argparse.ArgumentParser(description="Display two images (TV and OBS) from given paths.")
parser.add_argument("--tv", required=True, help="Path of the image to display on the TV screen")
parser.add_argument("--obs", required=True, help="Path of the image to stream to the OBS virtual camera")
args = parser.parse_args()

image_tv_path = args.tv
image_obs_path = args.obs

monitors = get_monitors()
if len(monitors) < 3:
    print("Error: At least three monitors are required.")
    exit()

monitor_tv = monitors[2]
monitor_obs = monitors[1]


def resize_to_screen(img_pil, monitor):
    screen_w, screen_h = monitor.width, monitor.height
    video_ratio = img_pil.width / img_pil.height
    screen_ratio = screen_w / screen_h

    if abs(video_ratio - screen_ratio) > 0.01:
        new_height = screen_h
        new_width = int(new_height * video_ratio)
        if new_width > screen_w:
            new_width = screen_w
            new_height = int(new_width / video_ratio)
        img_pil = img_pil.resize((new_width, new_height), Image.LANCZOS)
    else:
        img_pil = img_pil.resize((screen_w, screen_h), Image.LANCZOS)

    return img_pil


def load_image_safe(path):
    try:
        return Image.open(path).convert("RGB")
    except Exception:
        return None


root = tk.Tk()
root.withdraw()

tv_window = tk.Toplevel()
tv_window.overrideredirect(True)
tv_window.geometry(f"{monitor_tv.width}x{monitor_tv.height}+{monitor_tv.x}+{monitor_tv.y}")
tv_window.configure(bg="black")
tv_window.attributes("-topmost", True)

tv_canvas = tk.Canvas(tv_window, width=monitor_tv.width, height=monitor_tv.height, bg="black", highlightthickness=0)
tv_canvas.pack()


init_image = load_image_safe(image_obs_path)
while init_image is None:
    print("Waiting for the initial OBS image...")
    root.after(500)
    root.update()
    init_image = load_image_safe(image_obs_path)

resized = resize_to_screen(init_image, monitor_obs)
obs_np = np.array(resized)
obs_bgr = cv2.cvtColor(obs_np, cv2.COLOR_RGB2BGR)

cam = pyvirtualcam.Camera(width=obs_bgr.shape[1], height=obs_bgr.shape[0], fps=30, fmt=pyvirtualcam.PixelFormat.BGR)
cam.send(obs_bgr)
cam.sleep_until_next_frame()
print(f"OBS virtual camera active: {cam.device}")


def update():
    img_tv = load_image_safe(image_tv_path)
    img_obs = load_image_safe(image_obs_path)

    if img_tv:
        resized_tv = resize_to_screen(img_tv, monitor_tv)
        img_tk = ImageTk.PhotoImage(resized_tv, master=tv_window)

        if not hasattr(tv_window, "img_id"):
            tv_window.img_id = tv_canvas.create_image(0, 0, anchor="nw", image=img_tk)
        else:
            tv_canvas.itemconfig(tv_window.img_id, image=img_tk)

        tv_window.image_tk = img_tk

    if img_obs:
        mirrored = img_obs.transpose(Image.FLIP_LEFT_RIGHT)
        resized_obs = resize_to_screen(mirrored, monitor_obs)
        obs_np = np.array(resized_obs)
        obs_bgr = cv2.cvtColor(obs_np, cv2.COLOR_RGB2BGR)
        cam.send(obs_bgr)
        cam.sleep_until_next_frame()

    tv_window.after(33, update)  


update()
root.mainloop()

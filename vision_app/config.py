
from __future__ import annotations
from pathlib import Path
import cv2



APP_TITLE = "Vision Setup"

ROOT_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT_DIR / "assets"
ASSETS_DIR.mkdir(exist_ok=True)

MARKER_IMAGE = ASSETS_DIR / "MainBefore.jpg"
FALLBACK_IMAGE = ASSETS_DIR / "image_4_3.jpg"

# tkSliderWidget local (si non installé globalement)
TKSLIDER_DIR = ROOT_DIR / "tkSliderWidget"

# FFmpeg (DLL/EXE) optionnel
FFMPEG_DIR = ROOT_DIR / "ffmpeg"

# Camera
CAM_INDEX = 1                 # index comme dans ton code
CAM_DEVICE_NAME = None        # e.g. "USB2.0 HD UVC WebCam"
PREFERRED_BACKENDS = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_FFMPEG]

# Exposition
AUTO_EXPO = 0.25
EXPO_DEFAULT = -5.0
EXPO_MIN, EXPO_MAX = -13.0, -1.0

# UI timings
FRAME_DELAY_MS = 100
MATCH_DELAY_MS = 150

# HSV defaults
HSV_DEFAULTS = ((100, 130), (100, 255), (50, 255))

# Moyenne glissante
HISTORY_LEN = 10

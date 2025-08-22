
from __future__ import annotations
from pathlib import Path
import cv2



APP_TITLE = "Vision Setup"

ROOT_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT_DIR / "assets"
ASSETS_DIR.mkdir(exist_ok=True)

MARKER_IMAGE = ASSETS_DIR / "MainBefore.jpg"
FALLBACK_IMAGE = ASSETS_DIR / "image_4_3.jpg"


TKSLIDER_DIR = ROOT_DIR / "tkSliderWidget"


FFMPEG_DIR = ROOT_DIR / "ffmpeg"

# Camera
CAM_INDEX = 1                
CAM_DEVICE_NAME = None        
PREFERRED_BACKENDS = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_FFMPEG]


AUTO_EXPO = 0.25
EXPO_DEFAULT = -5.0
EXPO_MIN, EXPO_MAX = -13.0, -1.0


FRAME_DELAY_MS = 100
MATCH_DELAY_MS = 150


HSV_DEFAULTS = ((100, 130), (100, 255), (50, 255))


HISTORY_LEN = 10


from __future__ import annotations
import cv2
from typing import Tuple, Iterable, Optional
from ..config import FFMPEG_DIR, CAM_DEVICE_NAME, PREFERRED_BACKENDS
from ..utils.system import add_ffmpeg_dir

class VideoCaptureService:
    def __init__(self, index: int, backends: Iterable[int] = PREFERRED_BACKENDS, device_name: Optional[str] = CAM_DEVICE_NAME) -> None:
        add_ffmpeg_dir(FFMPEG_DIR)
        self.cap = None
        self._ok = False

        tries = []
        if device_name:
            for api in backends:
                tries.append((f"video={device_name}", api))
        for api in backends:
            tries.append((index, api))

        for source, api in tries:
            cap = cv2.VideoCapture(source, api)
            if cap is not None and cap.isOpened():
                self.cap = cap
                self._ok = True
                break
            if cap is not None:
                cap.release()

    @property
    def is_opened(self) -> bool:
        return bool(self._ok and self.cap is not None and self.cap.isOpened())

    def configure_manual_exposure(self, auto: float, exposure: float) -> None:
        if not self.is_opened: return
        self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, float(auto))
        self.cap.set(cv2.CAP_PROP_EXPOSURE, float(exposure))

    def set_exposure(self, exposure: float) -> None:
        if self.is_opened:
            self.cap.set(cv2.CAP_PROP_EXPOSURE, float(exposure))

    def read(self) -> Tuple[bool, object]:
        if not self.is_opened:
            return False, None
        return self.cap.read()

    def release(self) -> None:
        if self.cap:
            self.cap.release()

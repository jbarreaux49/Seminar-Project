
from __future__ import annotations
import os, sys, platform
from pathlib import Path

def is_windows() -> bool:
    return platform.system().lower().startswith("win")

def add_ffmpeg_dir(ffmpeg_dir: Path) -> None:
    try:
        if is_windows() and ffmpeg_dir.exists():
            os.add_dll_directory(str(ffmpeg_dir))
    except Exception:
        pass

def ensure_tkslider_on_path(tkslider_dir: Path) -> None:
    if tkslider_dir.exists():
        # Insère la racine pour que "from tkSliderWidget.tkSliderWidget import Slider" fonctionne
        sys.path.insert(0, str(tkslider_dir.parent))

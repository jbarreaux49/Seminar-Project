from __future__ import annotations
import cv2
import numpy as np
from PIL import Image, ImageTk


def draw_quad(img_bgr: np.ndarray, quad: np.ndarray | None, color=(0, 255, 0), thickness: int = 2) -> np.ndarray:
    out = img_bgr.copy()
    if quad is not None:
        cv2.polylines(out, [np.int32(quad)], True, color, thickness)
    return out


def pil_from_bgr(bgr: np.ndarray) -> Image.Image:
    return Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))


def photoimage_fit(img_pil: Image.Image, frame_size: tuple[int, int]) -> ImageTk.PhotoImage | None:
    fw, fh = frame_size
    if fw < 10 or fh < 10:
        return None
    iw, ih = img_pil.size
    r_img = iw / ih
    r_fr = fw / fh
    if r_fr > r_img:
        nh = fh
        nw = int(nh * r_img)
    else:
        nw = fw
        nh = int(nw / r_img)
    resized = img_pil.resize((nw, nh), Image.LANCZOS)
    return ImageTk.PhotoImage(resized)


class GestionAffichage:
    @staticmethod
    def resize_image(image: Image.Image, label, frame) -> None:
        """
        used on the first menu: adapts to the frame size by reading its dimensions.
        """
        frame.update_idletasks()
        frame_width = frame.winfo_width()
        frame_height = frame.winfo_height()
        if frame_width < 10 or frame_height < 10:
            return
        img_width, img_height = image.size
        img_ratio = img_width / img_height
        frame_ratio = frame_width / frame_height
        if frame_ratio > img_ratio:
            new_height = frame_height
            new_width = int(new_height * img_ratio)
        else:
            new_width = frame_width
            new_height = int(new_width / img_ratio)
        resized = image.resize((new_width, new_height), Image.LANCZOS)
        photo = ImageTk.PhotoImage(resized)
        label.config(image=photo)
        label.image = photo
        label.place(x=(frame_width - new_width) // 2,y=(frame_height - new_height) // 2,width=new_width,height=new_height)

    @staticmethod
    def resize_image_fixed(image: Image.Image, label, target_w: int, target_h: int) -> None:
        """
        used on the second menu: does not read the frame size, prevents resizing jitter.
        """
        if target_w < 10 or target_h < 10:
            return

        img_w, img_h = image.size
        img_ratio = img_w / img_h
        frame_ratio = target_w / target_h

        if frame_ratio > img_ratio:
            new_h = target_h
            new_w = int(new_h * img_ratio)
        else:
            new_w = target_w
            new_h = int(new_w / img_ratio)

        resized = image.resize((new_w, new_h), Image.LANCZOS)
        photo = ImageTk.PhotoImage(resized)

        label.config(image=photo)
        label.image = photo
        label.place(x=(target_w - new_w) // 2,y=(target_h - new_h) // 2,width=new_w,height=new_h)

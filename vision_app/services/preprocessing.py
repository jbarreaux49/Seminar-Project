
from __future__ import annotations
import cv2
import numpy as np
from typing import Tuple
from PIL import Image
from ..models import HsvThresholds

K5 = np.ones((5, 5), np.uint8)

def compute_hsv_mask(bgr: np.ndarray, h: Tuple[int, int], s: Tuple[int, int], v: Tuple[int, int]) -> np.ndarray:
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    lower = np.array([h[0], s[0], v[0]], dtype=np.uint8)
    upper = np.array([h[1], s[1], v[1]], dtype=np.uint8)
    mask = cv2.inRange(hsv, lower, upper)
    return cv2.morphologyEx(mask, cv2.MORPH_CLOSE, K5)

def biggest_inner_quad(mask: np.ndarray) -> np.ndarray | None:
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    best_inner, max_area = None, 0.0
    if hierarchy is None:
        return None
    for i, h in enumerate(hierarchy[0]):
        if h[3] != -1:
            cnt = contours[i]
            epsilon = 0.02 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            if len(approx) == 4:
                area = cv2.contourArea(approx)
                if area > max_area:
                    best_inner, max_area = approx, area
    return best_inner


class ControleurImage:
    """Same API as before: takes a PIL.Image and returns (mask_pil, annotated_pil).
       Now optionally accepts an HsvThresholds object to drive the thresholds explicitly.
    """
    def __init__(self, slider_h, slider_s, slider_v):
        self.slider_h = slider_h
        self.slider_s = slider_s
        self.slider_v = slider_v

    def traiter_image(self, image: Image.Image, thresholds: "HsvThresholds | None" = None):
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(image_cv, cv2.COLOR_BGR2HSV)

        if thresholds is None:
            h_min, h_max = self.slider_h.getValues()
            s_min, s_max = self.slider_s.getValues()
            v_min, v_max = self.slider_v.getValues()
        else:
            h_min, h_max = thresholds.h
            s_min, s_max = thresholds.s
            v_min, v_max = thresholds.v

        lower = np.array([h_min, s_min, v_min], dtype=np.uint8)
        upper = np.array([h_max, s_max, v_max], dtype=np.uint8)
        mask = cv2.inRange(hsv, lower, upper)
        mask_clean = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, K5)

        contours, hierarchy = cv2.findContours(mask_clean, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        best_inner = None
        max_area = 0.0
        if hierarchy is not None:
            for i, h in enumerate(hierarchy[0]):
                if h[3] != -1:
                    cnt = contours[i]
                    epsilon = 0.02 * cv2.arcLength(cnt, True)
                    approx = cv2.approxPolyDP(cnt, epsilon, True)
                    if len(approx) == 4:
                        area = cv2.contourArea(approx)
                        if area > max_area:
                            best_inner, max_area = approx, area

        annotated = image_cv.copy()
        if best_inner is not None:
            cv2.polylines(annotated, [np.int32(best_inner)], True, (0, 255, 0), 2)

        pil_mask = Image.fromarray(mask_clean).convert("RGB")
        pil_annotated = Image.fromarray(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB))
        return pil_mask, pil_annotated

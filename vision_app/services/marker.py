
from __future__ import annotations
import cv2
import numpy as np
from collections import deque
from typing import Deque
from ..models.geometry import HomographyResult

class MarkerTracker:
    def __init__(self, history_len: int = 10) -> None:
        self.sift = cv2.SIFT_create()
        self.bf = cv2.BFMatcher()
        self.history: Deque[np.ndarray] = deque(maxlen=history_len)
        self.marker_gray: np.ndarray | None = None

    def load_marker(self, bgr: np.ndarray) -> None:
        self.marker_gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    def match(self, frame_bgr: np.ndarray) -> HomographyResult:
        if self.marker_gray is None:
            return HomographyResult(None, None, None)
        kp1, des1 = self.sift.detectAndCompute(self.marker_gray, None)
        kp2, des2 = self.sift.detectAndCompute(frame_bgr, None)
        if des1 is None or des2 is None:
            return HomographyResult(None, None, None)
        good = []
        for m in self.bf.knnMatch(des1, des2, k=2):
            if len(m) == 2 and m[0].distance < 0.75 * m[1].distance:
                good.append(m[0])
        matches_vis = cv2.drawMatches(self.marker_gray, kp1, frame_bgr, kp2, good, None,
                                      flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
        if len(good) < 4:
            return HomographyResult(None, None, matches_vis)
        src = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        H, _ = cv2.findHomography(src, dst, cv2.RANSAC, 5.0)
        dst_quad = None
        if H is not None:
            h, w = self.marker_gray.shape
            quad = np.float32([[0, 0], [0, h], [w, h], [w, 0]]).reshape(-1, 1, 2)
            proj = cv2.perspectiveTransform(quad, H)
            self.history.append(proj.reshape(4, 2))
            avg = np.mean(np.array(self.history), axis=0).reshape(-1, 1, 2)
            dst_quad = avg
        return HomographyResult(H, dst_quad, matches_vis)

class AnalyseurSIFT:
    def __init__(self, marker_gray: np.ndarray):
        self.marker_gray = marker_gray
        self.sift = cv2.SIFT_create()

    def detecter_correspondances(self, image_bgr: np.ndarray):
        kp1, des1 = self.sift.detectAndCompute(self.marker_gray, None)
        kp2, des2 = self.sift.detectAndCompute(image_bgr, None)
        if des1 is None or des2 is None:
            return [], kp1, kp2, des1
        bf = cv2.BFMatcher()
        good = []
        matches = bf.knnMatch(des1, des2, k=2)
        for m in matches:
            if len(m) == 2:
                m1, m2 = m
                if m1.distance < 0.75 * m2.distance:
                    good.append(m1)
        return good, kp1, kp2, des1

from __future__ import annotations
from typing import Tuple, Optional
import numpy as np

try:
    from shapely.geometry import Polygon  
    _HAS_SHAPELY = True
except Exception:
    Polygon = None  
    _HAS_SHAPELY = False


def order_points_clockwise(pts: np.ndarray) -> np.ndarray:
    """
    Reorder a set of 4 points into a consistent clockwise order:
    top-left, top-right, bottom-right, bottom-left.
    """
    pts = np.asarray(pts, dtype="float32").reshape(4, 2)
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]   # top-left
    rect[2] = pts[np.argmax(s)]   # bottom-right
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # top-right
    rect[3] = pts[np.argmax(diff)]  # bottom-left
    return rect


def coverage_and_angles(ref_quad: np.ndarray, marker_quad: np.ndarray) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """
    Compute the overlap percentage and approximate orientation angles between
    a reference quadrilateral and a detected marker quadrilateral.
    """
    recouvrement, angle_x, angle_y = None, None, None
    try:
        rq = order_points_clockwise(ref_quad.reshape(4, 2))
        mq = order_points_clockwise(marker_quad.reshape(4, 2))

        if _HAS_SHAPELY:
            poly_cadre = Polygon(rq)
            poly_marker = Polygon(mq)
            if poly_cadre.is_valid and poly_marker.is_valid and poly_cadre.area > 0:
                intersection = poly_cadre.intersection(poly_marker).area
                recouvrement = (intersection / poly_cadre.area) * 100.0

        import cv2
        H, _ = cv2.findHomography(mq, rq)
        if H is not None:
            r1, r2 = H[:, 0], H[:, 1]
            angle_x = float(np.degrees(np.arctan2(r1[1], r1[0])))
            angle_y = float(np.degrees(np.arctan2(r2[1], r2[0])))
    except Exception:
        pass
    return recouvrement, angle_x, angle_y


from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import numpy as np


@dataclass
class HomographyResult:
    """
    Container for the result of a homography estimation.

    Attributes:
        H: The 3x3 homography matrix mapping the marker to the reference frame.

        dst_quad: The projected quadrilateral (4x2 points) in the destination image after applying the homography.

        matches_vis:
            An image (NumPy array) containing visualization of the feature matches between the marker and the current frame, for debugging/inspection.
    """
    H: Optional[np.ndarray]
    dst_quad: Optional[np.ndarray]
    matches_vis: Optional[np.ndarray]

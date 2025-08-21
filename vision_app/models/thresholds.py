
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple

Range = Tuple[int, int]

@dataclass
class HsvThresholds:
    h: Range
    s: Range
    v: Range

    @classmethod
    def from_defaults(cls, defaults: Tuple[Range, Range, Range]) -> "HsvThresholds":
        return cls(*defaults)

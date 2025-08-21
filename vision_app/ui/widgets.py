
from __future__ import annotations
import tkinter as tk
from tkinter import ttk

try:
    from tkSliderWidget.tkSliderWidget import Slider as ThirdPartySlider 
except Exception:
    ThirdPartySlider = None

class RangeSlider(ttk.Frame):
    def __init__(self, parent, text: str, min_val: int, max_val: int, init_lis=(0, 255), on_change=None):
        super().__init__(parent)
        ttk.Label(self, text=text).pack(pady=4)
        self.on_change = on_change
        if ThirdPartySlider is not None:
            self._impl = ThirdPartySlider(self, height=40, min_val=min_val, max_val=max_val,
                                          init_lis=list(init_lis), show_value=True)
            self._impl.pack(fill="x", padx=24)
            if on_change:
                self._impl.setValueChangeCallback(on_change)
            self.getValues = self._impl.getValues 
        else:
            inner = ttk.Frame(self); inner.pack(fill="x", padx=16)
            self._min = tk.DoubleVar(value=init_lis[0])
            self._max = tk.DoubleVar(value=init_lis[1])
            row = ttk.Frame(inner); row.pack(fill="x")
            ttk.Label(row, text="min").pack(side="left")
            self.smin = ttk.Scale(row, from_=min_val, to=max_val, variable=self._min, command=lambda *_: on_change and on_change())
            self.smin.pack(side="left", fill="x", expand=True, padx=6)
            row2 = ttk.Frame(inner); row2.pack(fill="x")
            ttk.Label(row2, text="max").pack(side="left")
            self.smax = ttk.Scale(row2, from_=min_val, to=max_val, variable=self._max, command=lambda *_: on_change and on_change())
            self.smax.pack(side="left", fill="x", expand=True, padx=6)

    def getValues(self):  
        return (int(self._min.get()), int(self._max.get()))

class SingleSlider(ttk.Frame):
    def __init__(self, parent, text: str, min_val: float, max_val: float, init_val: float, on_change=None):
        super().__init__(parent)
        ttk.Label(self, text=text).pack(pady=4)
        self.var = tk.DoubleVar(value=init_val)
        self.scale = ttk.Scale(self, from_=min_val, to=max_val, variable=self.var,
                               command=lambda *_: on_change and on_change())
        self.scale.pack(fill="x", padx=24)

    def value(self) -> float:
        return float(self.var.get())

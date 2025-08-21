from __future__ import annotations
import tkinter as tk
from tkinter import ttk
import cv2
import numpy as np
from PIL import Image

from ..config import (
    APP_TITLE, CAM_INDEX, AUTO_EXPO, EXPO_DEFAULT, EXPO_MIN, EXPO_MAX,
    HSV_DEFAULTS, FRAME_DELAY_MS, MATCH_DELAY_MS, MARKER_IMAGE, FALLBACK_IMAGE, HISTORY_LEN,
    TKSLIDER_DIR,
)
from ..utils.system import ensure_tkslider_on_path
ensure_tkslider_on_path(TKSLIDER_DIR)

from .widgets import RangeSlider, SingleSlider
try:
    from tkSliderWidget.tkSliderWidget import Slider as ThirdPartySlider 
except Exception:
    ThirdPartySlider = None

from ..services.video import VideoCaptureService
from ..services.preprocessing import compute_hsv_mask, biggest_inner_quad, ControleurImage
from ..services.marker import MarkerTracker, AnalyseurSIFT
from ..services.drawing import pil_from_bgr, draw_quad, GestionAffichage
from ..models.metrics import coverage_and_angles
from ..models import HsvThresholds


class MainWindow:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        try:
            self.root.state('zoomed')
        except Exception:
            pass

        self.cap = VideoCaptureService(CAM_INDEX)
        self.cap.configure_manual_exposure(auto=AUTO_EXPO, exposure=EXPO_DEFAULT)

        self.mode_columns = False
        self.ref_quad = None
        self.latest_frame = None
        self.tracker = MarkerTracker(history_len=HISTORY_LEN)

        self.PANEL_W_2 = self.root.winfo_screenwidth() // 2
        self.PANEL_H_2 = self.root.winfo_screenheight() // 2

        self._build_first_screen()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ---------- SCREEN 1 ----------
    def _build_first_screen(self) -> None:
        root = self.root
        for i in range(2):
            root.grid_rowconfigure(i, weight=1)
            root.grid_columnconfigure(i, weight=1)

        self.Frame1 = tk.Frame(root, bg="white", relief="solid", bd=1)
        self.Frame2 = tk.Frame(root, bg="white", relief="solid", bd=1)
        self.Frame3 = tk.Frame(root, bg="white", relief="solid", bd=1)
        self.Frame4 = tk.Frame(root, bg="white", relief="solid", bd=1)
        self.Frame1.grid(row=0, column=0, sticky="nsew")
        self.Frame2.grid(row=0, column=1, sticky="nsew")
        self.Frame3.grid(row=1, column=0, sticky="nsew")
        self.Frame4.grid(row=1, column=1, sticky="nsew")

        self.label_1 = tk.Label(self.Frame1)
        self.label_1.place(x=0, y=0)
        self.label_3 = tk.Label(self.Frame3)
        self.label_3.place(x=0, y=0)
        self.label_4 = tk.Label(self.Frame4)
        self.label_4.place(x=0, y=0)

        self._add_controls(self.Frame2)
        self._init_display_loop()

    def _add_controls(self, parent):
        parent.columnconfigure(0, weight=1)
        frames = []
        for i in range(6):
            parent.rowconfigure(i, weight=1)
            frame = tk.Frame(parent, bg="white", bd=1, relief="solid")
            frame.grid(row=i, column=0, sticky="nsew")
            frame.update_idletasks()
            frame.grid_propagate(False)
            frames.append(frame)

        # Hue
        self.slider = RangeSlider(frames[0], "Hue", 0, 255, HSV_DEFAULTS[0], on_change=self._on_hsv_change)
        self.slider.place(relx=0.1, rely=0.8, relwidth=0.8, anchor="w")

        # Saturation
        self.slider2 = RangeSlider(frames[1], "Saturation", 0, 255, HSV_DEFAULTS[1], on_change=self._on_hsv_change)
        self.slider2.place(relx=0.1, rely=0.8, relwidth=0.8, anchor="w")

        # Value
        self.slider3 = RangeSlider(frames[2], "Value / Luminance", 0, 255, HSV_DEFAULTS[2], on_change=self._on_hsv_change)
        self.slider3.place(relx=0.1, rely=0.8, relwidth=0.8, anchor="w")
 
        if ThirdPartySlider is not None:
            self.slider_expo = ThirdPartySlider(
                frames[3], height=40, min_val=EXPO_MIN, max_val=EXPO_MAX, init_lis=[EXPO_DEFAULT], show_value=True
            )
            self.slider_expo.place(relx=0.1, rely=0.8, relwidth=0.8, anchor="w")
            ttk.Label(frames[3], text="Exposure").place(relx=0.5, rely=0.3, anchor="center")
            self.slider_expo.setValueChangeCallback(self._on_expo_change)
        else:
            exo = SingleSlider(frames[3], "Exposure", EXPO_MIN, EXPO_MAX, EXPO_DEFAULT, on_change=self._on_expo_change)
            exo.pack(fill="x", padx=24, pady=8)
            self.slider_expo = exo

        switch_btn = ttk.Button(frames[5], text="Next", command=lambda: [self._validate_cadre(), self._build_second_screen()])
        switch_btn.pack(pady=10)

        self.controleur = ControleurImage(self.slider, self.slider2, self.slider3)

    def _on_hsv_change(self, *_):
        if self.latest_frame is None:
            return

        h_min, h_max = self.slider.getValues()
        s_min, s_max = self.slider2.getValues()
        v_min, v_max = self.slider3.getValues()
        thresholds = HsvThresholds((h_min, h_max), (s_min, s_max), (v_min, v_max))

        image_pil = Image.fromarray(cv2.cvtColor(self.latest_frame, cv2.COLOR_BGR2RGB))
        _, annotated = self.controleur.traiter_image(image_pil, thresholds=thresholds)
        GestionAffichage.resize_image(annotated, self.label_4, self.Frame4)

    def _validate_cadre(self):
        if self.latest_frame is None:
            print("No webcam frame captured")
            return

        h_min, h_max = self.slider.getValues()
        s_min, s_max = self.slider2.getValues()
        v_min, v_max = self.slider3.getValues()
        thresholds = HsvThresholds((h_min, h_max), (s_min, s_max), (v_min, v_max))

        image_bgr = self.latest_frame.copy()
        mask = compute_hsv_mask(image_bgr, thresholds.h, thresholds.s, thresholds.v)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

        best = biggest_inner_quad(mask)

        if best is not None:
            self.ref_quad = np.float32(best.reshape(4, 2))
            print("Frame saved and image frozen for SIFT")
        else:
            self.ref_quad = None
            print("No frame detected.")

    def _init_display_loop(self):
        def update_frame():
            if self.mode_columns:
                return

            ok, frame = self.cap.read()
            if not ok:
                print("Error reading webcam.")
                self.root.after(FRAME_DELAY_MS, update_frame)
                return

            self.latest_frame = frame.copy()
            image_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            h_min, h_max = self.slider.getValues()
            s_min, s_max = self.slider2.getValues()
            v_min, v_max = self.slider3.getValues()
            thresholds = HsvThresholds((h_min, h_max), (s_min, s_max), (v_min, v_max))

            mask_pil, annotated_pil = self.controleur.traiter_image(image_pil, thresholds=thresholds)

            GestionAffichage.resize_image(image_pil, self.label_1, self.Frame1)
            GestionAffichage.resize_image(mask_pil, self.label_3, self.Frame3)
            GestionAffichage.resize_image(annotated_pil, self.label_4, self.Frame4)

            self.root.after(FRAME_DELAY_MS, update_frame)

        update_frame()

    # ---------- SCREEN 2 ----------
    def _build_second_screen(self):
        self.mode_columns = True
        self._cancel_second_loop()

        for w in self.root.winfo_children():
            w.destroy()

        for i in range(2):
            self.root.rowconfigure(i, weight=1)
        for j in range(2):
            self.root.columnconfigure(j, weight=1)

        self.col1 = tk.Frame(self.root, bg="#f5f5f5", relief="solid", bd=1, width=self.PANEL_W_2, height=self.PANEL_H_2)
        self.col2 = tk.Frame(self.root, bg="#e8f5e9", relief="solid", bd=1, width=self.PANEL_W_2, height=self.PANEL_H_2)
        self.col3 = tk.Frame(self.root, bg="#fffbe6", relief="solid", bd=1, width=self.PANEL_W_2, height=self.PANEL_H_2)
        self.col4 = tk.Frame(self.root, bg="#e6f7ff", relief="solid", bd=1, width=self.PANEL_W_2, height=self.PANEL_H_2)
        self.col1.grid(row=0, column=0, sticky="nsew")
        self.col2.grid(row=0, column=1, sticky="nsew")
        self.col3.grid(row=1, column=0, sticky="nsew")
        self.col4.grid(row=1, column=1, sticky="nsew")

        for f in (self.col1, self.col2, self.col3, self.col4):
            f.grid_propagate(False)

        if ThirdPartySlider is not None:
            self.slider_expo2 = ThirdPartySlider(
                self.col1, min_val=EXPO_MIN, max_val=EXPO_MAX,
                init_lis=[EXPO_DEFAULT], show_value=True, height=40
            )
            self.slider_expo2.place(x=40, y=60, width=self.PANEL_W_2 - 80)
            ttk.Label(self.col1, text="Exposure").place(x=self.PANEL_W_2 // 2, y=20, anchor="center")
            self.slider_expo2.setValueChangeCallback(self._on_expo_change)
        else:
            ttk.Label(self.col1, text="Exposure").place(x=self.PANEL_W_2 // 2, y=20, anchor="center")
            exo2 = SingleSlider(self.col1, "", EXPO_MIN, EXPO_MAX, EXPO_DEFAULT, on_change=self._on_expo_change)
            exo2.place(x=40, y=60, width=self.PANEL_W_2 - 80)
            self.slider_expo2 = exo2

        btn_back = ttk.Button(self.col1, text="Reconfigure frame", command=self._back_to_first_screen)
        btn_back.place(x=40, y=120, width=self.PANEL_W_2 - 80, height=32)

        self.label_matches = tk.Label(self.col2)
        self.label_matches.place(x=0, y=0)

        self.label_estimation = tk.Label(self.col3)
        self.label_estimation.place(x=0, y=0)

        self.label_infos = tk.Label(
            self.col4, text="", justify="left", anchor="nw",
            font=("Consolas", 11), bg="#e6f7ff"
        )
        self.label_infos.place(x=8, y=8, width=self.PANEL_W_2 - 16, height=self.PANEL_H_2 - 16)

        self.marker_bgr = cv2.imread(str(MARKER_IMAGE)) if MARKER_IMAGE.exists() else None
        if self.marker_bgr is None:
            self.label_infos.config(text="Marker not found in ./assets/MainBefore.jpg")
            if hasattr(self, "marker_gray"):
                del self.marker_gray
            if hasattr(self, "analyseur"):
                del self.analyseur
        else:
            self.marker_gray = cv2.cvtColor(self.marker_bgr, cv2.COLOR_BGR2GRAY)
            self.tracker.load_marker(self.marker_bgr)
            from ..services.marker import AnalyseurSIFT
            self.analyseur = AnalyseurSIFT(self.marker_gray)

        self._loop_columns()

    def _back_to_first_screen(self):
        self._cancel_second_loop()
        self.mode_columns = False
        self.ref_quad = None
        if hasattr(self, "_marker_history"):
            del self._marker_history
        for w in self.root.winfo_children():
            w.destroy()
        self._build_first_screen()

    def _cancel_second_loop(self):
        if getattr(self, "_loop_job", None):
            try:
                self.root.after_cancel(self._loop_job)
            except Exception:
                pass
            self._loop_job = None

    def _loop_columns(self):
        if not self.mode_columns:
            return
        if not (hasattr(self, "label_infos") and self.label_infos.winfo_exists()):
            return

        ok, frame = self.cap.read()
        if not ok:
            self._loop_job = self.root.after(MATCH_DELAY_MS, self._loop_columns)
            return

        original_bgr = frame.copy()

        result = self.tracker.match(original_bgr)

        matched_img = original_bgr.copy()
        if hasattr(self, "analyseur") and hasattr(self, "marker_gray"):
            good, kp1, kp2, des1 = self.analyseur.detecter_correspondances(original_bgr)
            if kp1 is not None and kp2 is not None:
                matched_img = cv2.drawMatches(
                    self.marker_gray, kp1,
                    original_bgr, kp2,
                    good, None,
                    flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
                )
        else:
            if result.matches_vis is not None:
                matched_img = result.matches_vis

        found_marker = original_bgr.copy()
        if result.dst_quad is not None:
            cv2.polylines(found_marker, [np.int32(result.dst_quad)], True, (255, 0, 0), 3)
        if self.ref_quad is not None:
            cv2.polylines(found_marker, [np.int32(self.ref_quad)], True, (0, 255, 0), 3)

        infos_text = ""
        if self.ref_quad is not None and result.dst_quad is not None and len(result.dst_quad) == 4:
            recouvrement, angle_x, angle_y = coverage_and_angles(self.ref_quad, result.dst_quad.reshape(4, 2))
            if recouvrement is not None:
                infos_text += f"Overlap: {recouvrement:.2f}%\n"
            if angle_x is not None and angle_y is not None:
                infos_text += f"Tilt X: {angle_x:.2f}°\nTilt Y: {angle_y:.2f}°\n"
        else:
            infos_text += "Frame or marker not detected.\n"

        try:
            self.label_infos.config(text=infos_text)
            self.label_infos.config(fg="red" if "Error" in infos_text else "black")
        except tk.TclError:
            return

        pil_matches = Image.fromarray(cv2.cvtColor(matched_img, cv2.COLOR_BGR2RGB))
        pil_estimation = Image.fromarray(cv2.cvtColor(found_marker, cv2.COLOR_BGR2RGB))
        GestionAffichage.resize_image_fixed(pil_matches, self.label_matches, self.PANEL_W_2, self.PANEL_H_2)
        GestionAffichage.resize_image_fixed(pil_estimation, self.label_estimation, self.PANEL_W_2, self.PANEL_H_2)

        self._loop_job = self.root.after(MATCH_DELAY_MS, self._loop_columns)

    def _on_expo_change(self, *_):
        try:
            if hasattr(self.slider_expo, "getValues"):
                val = float(self.slider_expo.getValues()[0])
            elif hasattr(self.slider_expo, "value"):
                val = float(self.slider_expo.value())
            elif hasattr(self, "slider_expo2"):
                if hasattr(self.slider_expo2, "getValues"):
                    val = float(self.slider_expo2.getValues()[0])
                elif hasattr(self.slider_expo2, "value"):
                    val = float(self.slider_expo2.value())
                else:
                    return
            else:
                return
            self.cap.set_exposure(val)
            print(f"Exposure set to {val}")
        except Exception as e:
            print(f"Error setting exposure: {e}")

    def _on_close(self):
        self.cap.release()
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()

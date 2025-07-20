import cv2
import numpy as np
import datetime
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
from PIL import Image, ImageTk  # pillow is required
import collections
import os
import platform
from pathlib import Path


class WebcamMonitor:
    """Tkinter GUI wrapper around OpenCV detection & recording logic."""

    def __init__(self, root):
        self.root = root
        self.root.title("Webcam Monitor – Motion & Human Detection")

        # ==== Video panel ====
        self.video_label = ttk.Label(root)
        self.video_label.pack(padx=5, pady=5)

        # ==== Controls ====
        controls = ttk.Frame(root)
        controls.pack(fill="x", padx=5, pady=5)

        # Store parameter variables (only adjustable via Settings dialog)
        self.min_area_var = tk.IntVar(value=5000)
        self.pre_buffer_var = tk.IntVar(value=10)
        self.post_buffer_var = tk.IntVar(value=10)

        # Camera index variable (for settings)
        self.cam_index_var = tk.IntVar(value=0)

        # Destination directory for recordings
        default_dir = Path.home() / "Videos" / "SecCam"
        default_dir.mkdir(parents=True, exist_ok=True)
        self.destination_dir = tk.StringVar(value=str(default_dir))

        self.status_var = tk.StringVar(value="Idle")
        ttk.Label(root, textvariable=self.status_var).pack(pady=(0, 5))

        btn_frame = ttk.Frame(root)
        btn_frame.pack(pady=(0, 10))
        self.start_btn = ttk.Button(btn_frame, text="Start", command=self.start)
        self.start_btn.grid(row=0, column=0, padx=5)
        self.stop_btn = ttk.Button(btn_frame, text="Stop", command=self.stop, state="disabled")
        self.stop_btn.grid(row=0, column=1, padx=5)
        self.settings_btn = ttk.Button(btn_frame, text="Settings", command=self.toggle_settings)
        self.settings_btn.grid(row=0, column=2, padx=5)
        self.export_btn = ttk.Button(btn_frame, text="Export Log", command=self.export_log)
        self.export_btn.grid(row=0, column=3, padx=5)

        # ==== Detection list ====
        list_frame = ttk.Frame(root)
        list_frame.pack(fill="both", expand=True, padx=5, pady=(0, 10))
        ttk.Label(list_frame, text="Detections (double-click to open)").pack(anchor="w")

        self.detection_list = tk.Listbox(list_frame, height=8)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.detection_list.yview)
        self.detection_list.configure(yscrollcommand=scrollbar.set)
        self.detection_list.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.detection_list.bind("<Double-Button-1>", self.open_selected_clip)

        # Internal list to keep metadata about detections (dicts with timestamp & filename)
        self.detections = []

        # Settings window reference
        self.settings_win = None

        # ==== Internal state ====
        self.running = False
        self.cap = None
        self.backSub = None
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.recording = False
        self.out = None
        self.frames_since_last_detection = 0
        self.frame_buffer = None  # will hold pre-buffer frames (deque)
        self.pre_buffer_frames = 0  # depends on fps

        self.frame_width = 0
        self.frame_height = 0
        self.fps = 30.0
        # Inter-frame delay for GUI update (ms). Will use minimal delay to pull frames as fast as the camera provides.
        self.frame_delay = 1

        # Always record option
        self.always_record_var = tk.BooleanVar(value=True)

        # Master recording writer
        self.master_recording = False
        self.master_out = None

        self.update_job = None

        # Close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Keyboard shortcut to open settings (press 's' or 'S')
        self.root.bind_all("<KeyPress-s>", self.toggle_settings)
        self.root.bind_all("<KeyPress-S>", self.toggle_settings)

    # ------------------------------------------------------------------
    def start(self):
        if self.running:
            return
        self.cap = cv2.VideoCapture(self.cam_index_var.get())
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Could not open webcam.")
            return

        # Frame properties for video writer
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps_from_cam = self.cap.get(cv2.CAP_PROP_FPS)
        self.fps = fps_from_cam if fps_from_cam > 0 else 30.0
        # Use minimal delay (1 ms). Rely on camera/internal rate for frame pacing.
        self.frame_delay = 1

        # Pre/Post buffer frame calculations
        self.pre_buffer_frames = int(self.pre_buffer_var.get() * self.fps)
        self.post_buffer_frames = int(self.post_buffer_var.get() * self.fps)
        self.frame_buffer = collections.deque(maxlen=self.pre_buffer_frames)

        # Background subtractor
        self.backSub = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50, detectShadows=True)

        self.running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.status_var.set("Running")

        # Start frame loop
        self.update_frame()

        # Start master recording if option enabled
        if self.always_record_var.get() and not self.master_recording:
            self._start_master_recording()

    # ------------------------------------------------------------------
    def stop(self):
        if not self.running:
            return
        self.running = False
        self.status_var.set("Stopping…")
        if self.update_job is not None:
            self.root.after_cancel(self.update_job)
            self.update_job = None
        self._release_resources()
        self.video_label.configure(image="")
        # Stop master recording if running
        self._stop_master_recording()
        self.status_var.set("Stopped")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

    # ------------------------------------------------------------------
    def update_frame(self):
        if not self.running:
            return
        ret, frame = self.cap.read()
        if not ret:
            self.status_var.set("Failed to grab frame")
            self.stop()
            return

        # Save raw frame to buffer (for pre-recording)
        raw_frame = frame.copy()
        if self.frame_buffer is not None:
            self.frame_buffer.append(raw_frame)

        # Main detection logic -------------------------------------------------
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Human detection
        human_detected = False
        for (x, y, w, h) in self.face_cascade.detectMultiScale(gray, 1.3, 5):
            human_detected = True
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            # Label the detected human
            label_y = y - 10 if y - 10 > 10 else y + h + 20
            cv2.putText(frame, "Human", (x, label_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        # Motion detection
        motion_detected = False
        fgMask = self.backSub.apply(frame)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        fgMask = cv2.morphologyEx(fgMask, cv2.MORPH_OPEN, kernel, iterations=2)
        contours, _ = cv2.findContours(fgMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            if cv2.contourArea(cnt) > self.min_area_var.get():
                motion_detected = True
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if motion_detected or human_detected:
            cv2.putText(frame, "Motion/Human Detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            self.frames_since_last_detection = 0
            if not self.recording:
                filename_only = datetime.datetime.now().strftime("recording_%Y%m%d_%H%M%S.avi")
                filepath = os.path.join(self.destination_dir.get(), filename_only)
                # Ensure directory exists (user might have typed new path without browsing)
                Path(self.destination_dir.get()).mkdir(parents=True, exist_ok=True)
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                self.out = cv2.VideoWriter(filepath, fourcc, self.fps, (self.frame_width, self.frame_height))
                # Write pre-buffer frames first
                if self.frame_buffer is not None:
                    for bf in self.frame_buffer:
                        self.out.write(bf)
                self.recording = True
                # Log this detection
                timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.detections.append({"timestamp": timestamp_str, "filename": filepath})
                self.detection_list.insert(tk.END, f"{timestamp_str} – {filename_only}")
        else:
            if self.recording:
                self.frames_since_last_detection += 1
                if self.frames_since_last_detection > self.post_buffer_frames:
                    self._stop_recording()

        if self.recording and self.out is not None:
            self.out.write(frame)
        # ---------------------------------------------------------------------

        # Convert and display in Tkinter
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(Image.fromarray(rgb))
        self.video_label.imgtk = img  # save reference
        self.video_label.configure(image=img)

        # Schedule next frame
        self.update_job = self.root.after(self.frame_delay, self.update_frame)

        # If master recording on, write raw frame
        if self.master_recording and self.master_out is not None:
            # Overlay current timestamp on the frame
            time_str = datetime.datetime.now().strftime("%H:%M:%S")
            overlay_frame = raw_frame.copy()
            cv2.putText(overlay_frame, time_str, (10, self.frame_height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            self.master_out.write(overlay_frame)

    # ------------------------------------------------------------------
    def _stop_recording(self):
        if self.recording:
            self.recording = False
            if self.out is not None:
                self.out.release()
                self.out = None

    # ------------------------------------------------------------------
    def _release_resources(self):
        self._stop_recording()
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    # ------------------------------------------------------------------
    def on_close(self):
        self.stop()
        self.root.destroy()

    # ------------------------------------------------------------------
    def toggle_settings(self, event=None):
        # If window exists and is visible, close it (toggle behavior)
        if self.settings_win is not None and self.settings_win.winfo_exists():
            self.settings_win.destroy()
            self.settings_win = None
            return

        self.settings_win = tk.Toplevel(self.root)
        self.settings_win.title("Settings")
        self.settings_win.resizable(False, False)

        # When the window is closed via the window manager, clear reference
        self.settings_win.protocol("WM_DELETE_WINDOW", lambda: (self.settings_win.destroy(), setattr(self, 'settings_win', None)))

        row = 0
        ttk.Label(self.settings_win, text="Camera index:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        ttk.Spinbox(self.settings_win, from_=0, to=10, textvariable=self.cam_index_var, width=5).grid(row=row, column=1, padx=5, pady=5)

        row += 1
        ttk.Label(self.settings_win, text="Min motion area:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.settings_win, textvariable=self.min_area_var, width=10).grid(row=row, column=1, padx=5, pady=5)

        row += 1
        ttk.Label(self.settings_win, text="Pre-record buffer (s):").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.settings_win, textvariable=self.pre_buffer_var, width=10).grid(row=row, column=1, padx=5, pady=5)

        row += 1
        ttk.Label(self.settings_win, text="Post-record buffer (s):").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.settings_win, textvariable=self.post_buffer_var, width=10).grid(row=row, column=1, padx=5, pady=5)

        # Always record checkbox
        row += 1
        ttk.Checkbutton(self.settings_win, text="Always record (master clip)", variable=self.always_record_var).grid(row=row, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        # Destination directory row
        row += 1
        ttk.Label(self.settings_win, text="Save directory:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        dir_entry = ttk.Entry(self.settings_win, textvariable=self.destination_dir, width=30)
        dir_entry.grid(row=row, column=1, padx=5, pady=5)
        ttk.Button(self.settings_win, text="Browse…", command=self._browse_destination).grid(row=row, column=2, padx=5, pady=5)

        row += 1
        ttk.Button(self.settings_win, text="Close", command=self.settings_win.destroy).grid(row=row, column=0, columnspan=3, pady=10)

    # ------------------------------------------------------------------
    def open_selected_clip(self, event=None):
        selection = self.detection_list.curselection()
        if not selection:
            return
        idx = selection[0]
        clip_path = self.detections[idx]["filename"]
        try:
            if platform.system() == "Windows":
                os.startfile(clip_path)
            elif platform.system() == "Darwin":
                import subprocess
                subprocess.Popen(["open", clip_path])
            else:
                import subprocess
                subprocess.Popen(["xdg-open", clip_path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open clip:\n{e}")

    # ------------------------------------------------------------------
    def export_log(self):
        if not self.detections:
            messagebox.showinfo("Export Log", "No detections to export yet.")
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not filepath:
            return  # user cancelled
        try:
            import csv
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Filename"])
                for det in self.detections:
                    writer.writerow([det["timestamp"], det["filename"]])
            messagebox.showinfo("Export Log", f"Log exported to {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export log:\n{e}")

    # ------------------------------------------------------------------
    def _browse_destination(self):
        selected = filedialog.askdirectory(initialdir=self.destination_dir.get() or str(Path.home()), title="Select destination folder")
        if selected:
            self.destination_dir.set(selected)
            # Ensure directory exists
            Path(selected).mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    def _start_master_recording(self):
        if self.master_recording:
            return
        filename_only = datetime.datetime.now().strftime("master_%Y%m%d_%H%M%S.avi")
        filepath = os.path.join(self.destination_dir.get(), filename_only)
        Path(self.destination_dir.get()).mkdir(parents=True, exist_ok=True)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.master_out = cv2.VideoWriter(filepath, fourcc, self.fps, (self.frame_width, self.frame_height))
        if self.master_out.isOpened():
            self.master_recording = True

    # ------------------------------------------------------------------
    def _stop_master_recording(self):
        if self.master_recording:
            self.master_recording = False
            if self.master_out is not None:
                self.master_out.release()
                self.master_out = None


# ============================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = WebcamMonitor(root)
    root.mainloop() 